#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 World Wide Workshop Foundation
# Copyright 2007 Collabora Ltd
# Copyright 2008 Morgan Collett
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# If you find this activity useful or end up using parts of it in one of
# your own creations we would love to hear from you at
# info@WorldWideWorkshop.org !

from gi.repository import GdkPixbuf

import subprocess
import cPickle
import json
import logging

from hashlib import sha1
from datetime import date
from gettext import gettext as _

import telepathy
import telepathy.client

from sugar3.presence.tubeconn import TubeConnection

from sugar3.activity import activity
from sugar3.graphics.alert import NotifyAlert

from sugar3.presence import presenceservice
from sugar3.datastore import datastore
from sugar3 import profile

from Widgets import Toolbar

# Interfaces
from Widgets import NewPollCanvas   # Create a new poll.
from Widgets import SelectCanvas    # Select one available poll.
from Widgets import PollCanvas      # Participate in a poll.

from PollSession import PollSession
from PollSession import Poll

SERVICE = "org.worldwideworkshop.olpc.PollBuilder"
IFACE = SERVICE
PATH = "/org/worldwideworkshop/olpc/PollBuilder"


class PollBuilder(activity.Activity):
    """
    Sugar activity for polls

    Poll implements a simple tool that allows children to express
    their opinions on a given topic by selecting one of five
    answer choices and submitting a vote. The results are tallied
    by total number of votes and percentage of total votes cast.

    A future version of this activity will be networked over the
    OLPC mesh to allow sharing of the poll.
    """

    def __init__(self, handle):

        activity.Activity.__init__(self, handle)

        self._logger = logging.getLogger('poll-activity')
        self._logger.debug('Starting Poll activity')

        self._polls = set()
        self.current_vote = None
        self._current_view = None
        self._previewing = False

        # This property allows result viewing while voting
        self._view_answer = True

        # This property allows use image in answer
        self._use_image = False

        # This property allows play a sound when click in
        # the button to make a vote
        self._play_vote_sound = False

        # This property allows remember in the radio button options
        # the last vote
        self._remember_last_vote = True

        # This property has the image size
        self._image_size = {'height': 100, 'width': 100}

        # get the Presence Service
        self.pservice = presenceservice.get_instance()
        self.initiating = False

        # Buddy object for you
        owner = self.pservice.get_owner()
        self.owner = owner
        self.nick = owner.props.nick
        self.nick_sha1 = sha1(self.nick).hexdigest()

        toolbar = Toolbar(self)
        toolbar.create_button.connect('clicked', self.__button_new_clicked)
        toolbar.choose_button.connect('clicked', self.__button_select_clicked)
        self.set_toolbar_box(toolbar)

        self._create_new_poll()

        self.show_all()

        self.poll_session = None

        self.connect('shared', self.__shared_cb)
        self.connect('joined', self.__joined_cb)

    def __create_pixbufs(self, images_ds_object_id):
        """
        Crea las imágenes de la encuesta, al leer desde el journal.
        """

        pixbufs = {}

        for index, ds_object_id in images_ds_object_id.iteritems():
            if not ds_object_id == '':
                image_file_path = datastore.get(ds_object_id).file_path
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                    image_file_path, self._image_size['height'],
                    self._image_size['width'])
                pixbufs[int(index)] = pixbuf

            else:
                pixbufs[int(index)] = ''

        return pixbufs

    def __get_images_ds_objects(self, images_ds_object_id):
        """
        Obtiene las imagenes almacenadas en el jornal.
        """

        images_ds_objects = {}

        for index, ds_object_id in images_ds_object_id.iteritems():
            images_ds_objects[int(index)] = {}

            if not ds_object_id == '':
                images_ds_objects[int(index)]['id'] = ds_object_id
                images_ds_objects[int(index)]['file_path'] = \
                    datastore.get(ds_object_id).file_path

        return images_ds_objects

    def read_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

                self._view_answer = data['view_answer']
                self._remember_last_vote = data['remember_last_vote']
                self._play_vote_sound = data['play_vote_sound']
                self._use_image = data['use_image']
                self._image_size = data['image_size']
                self._polls = set()
                for poll_data in data['polls_data']:
                    # json stores the dictionary keys as strings,
                    # convert to int
                    options = {}
                    for key in poll_data['options']:
                        options[int(key)] = poll_data['options'][key]

                    images_ds_objects = {}
                    for key in poll_data['images_ds_objects']:
                        images_ds_objects[int(key)] = \
                            poll_data['images_ds_objects'][key]

                    data = {}
                    for key in poll_data['data']:
                        data[int(key)] = poll_data['data'][key]

                    images = self.__create_pixbufs(images_ds_objects)
                    images_ds_object = self.__get_images_ds_objects(
                        images_ds_objects)
                    self._polls.add(Poll(
                        self, poll_data['title'], poll_data['author'],
                        poll_data['active'],
                        date.fromordinal(poll_data['createdate']),
                        poll_data['maxvoters'], poll_data['question'],
                        poll_data['number_of_options'],
                        options, data, poll_data['votes'],
                        images, images_ds_object))
        except:
            # if can't read json, try read with the old format
            self._old_read_file(file_path)

        # if there are polls loaded, show the selection screen
        # if not, show the creation screen
        if self._polls:
            self.set_canvas(SelectCanvas(self))
        else:
            self._create_new_poll()

        self.get_toolbar_box().update_configs()

    def _old_read_file(self, file_path):
        """
        This method use pickle to read files saved by old versions of the
        activity
        """

        self._logger.debug(
            'Reading OLD FORMAT file from datastore via Journal: %s' %
            file_path)

        self._polls = set()

        f = open(file_path, 'r')
        num_polls = cPickle.load(f)
        activity_settings = cPickle.load(f)
        self._view_answer = activity_settings['view_answer']
        self._remember_last_vote = activity_settings['remember_last_vote']
        self._play_vote_sound = activity_settings['play_vote_sound']
        self._use_image = activity_settings['use_image']
        self._image_size = cPickle.load(f)

        for p in range(num_polls):
            title = cPickle.load(f)
            author = cPickle.load(f)
            active = cPickle.load(f)
            createdate_i = cPickle.load(f)
            maxvoters = cPickle.load(f)
            question = cPickle.load(f)
            number_of_options = cPickle.load(f)
            options = cPickle.load(f)
            data = cPickle.load(f)
            votes = cPickle.load(f)
            images_ds_objects_id = cPickle.load(f)
            images = self.__create_pixbufs(images_ds_objects_id)

            images_ds_object = self.__get_images_ds_objects(
                images_ds_objects_id)

            poll = Poll(self, title, author, active,
                        date.fromordinal(int(createdate_i)),
                        maxvoters, question, number_of_options, options,
                        data, votes, images, images_ds_object)

            self._polls.add(poll)

        f.close()

        self.set_canvas(SelectCanvas(self))

    def write_file(self, file_path):
        """
        Implement writing to the journal

        This is called within sugar3.activity.Activity code
        which provides the file_path.
        """

        polls_data = []
        for poll in self._polls:
            polls_data.append(poll.dump())
        data = {
            'view_answer': self._view_answer,
            'remember_last_vote': self._remember_last_vote,
            'play_vote_sound': self._play_vote_sound,
            'use_image': self._use_image,
            'image_size': self._image_size,
            'polls_data': polls_data}

        with open(file_path, 'w') as f:
            f.write(json.dumps(data))

    def get_alert(self, title, text):
        """
        Show an alert above the activity.
        """

        alert = NotifyAlert(timeout=5)
        alert.props.title = title
        alert.props.msg = text
        self.add_alert(alert)
        alert.connect('response', self.__alert_cancel_cb)
        alert.show()

    def __alert_cancel_cb(self, alert, response_id):
        """
        Callback for alert events
        """

        self.remove_alert(alert)

    def _poll_canvas(self):
        """
        Show the poll canvas where children vote on an existing poll.
        """
        self._current_view = 'poll'
        self.current_vote = None
        return PollCanvas(self._poll, self.current_vote,
                          self._view_answer, self._previewing)

    def _select_poll_button_cb(self, button, sha=None):
        """
        A VOTE or SEE RESULTS button was clicked.
        """
        if not sha:
            self._logger.debug('Strange, which button was clicked?')
            return

        self._previewing = False
        self.__switch_to_poll(sha)
        self.set_canvas(self._poll_canvas())

    def _delete_poll_button_cb(self, button, sha):
        """
        A DELETE button was clicked.
        """

        if not sha:
            self._logger.debug('Strange, which button was clicked?')
            return

        if self._poll.sha == sha:
            self._logger.debug('delete_poll: removing current poll')

        for poll in self._polls:
            if poll.sha == sha:
                self._polls.remove(poll)

        self.set_canvas(SelectCanvas(self))

    def vote_choice_radio_button(self, widget, data):
        """
        Track which radio button has been selected

        This is connected to the vote choice radio buttons.
        data contains the choice (0 - 4) selected.
        """

        self.current_vote = data

    def __play_vote_button_sound(self):

        try:
            # FIXME: Cambiar por gst
            subprocess.Popen("aplay extras/vote-sound.wav", shell=True)

        except (OSError, ValueError), e:
            logging.exception(e)

    def button_vote_cb(self, button):
        """
        Register a vote

        Take the selected option from self.current_vote
        and increment the poll_data.
        """

        if self.current_vote is not None:
            if self._poll.vote_count >= self._poll.maxvoters:
                self._logger.debug('Hit the max voters, ignoring this vote.')
                return

            self._logger.debug('Voted ' + str(self.current_vote))

            try:
                self._poll.register_vote(self.current_vote, self.nick_sha1)

            except OverflowError:
                self._logger.debug('Local vote failed: '
                                   'maximum votes already registered.')

            except ValueError:
                self._logger.debug('Local vote failed: poll closed.')

            self._logger.debug('Results: ' + str(self._poll.data))

            if self._play_vote_sound:
                self.__play_vote_button_sound()

            if not self._remember_last_vote:
                self.current_vote = None

            self.set_canvas(PollCanvas(self._poll,
                                       self.current_vote, self._view_answer,
                                       self._previewing))
        else:
            self.get_alert(
                _('Poll Activity'),
                _('To vote you have to select first one option'))

    def __button_select_clicked(self, button):
        """
        Show Choose a Poll canvas
        """

        self.set_canvas(SelectCanvas(self))

    def __button_new_clicked(self, button):
        """
        Show Build a Poll canvas.
        """
        self._create_new_poll()

    def _create_new_poll(self):
        # Reset vote data to 0
        self._poll = Poll(activity=self, author=profile.get_nick_name(),
                          active=False)
        self.current_vote = None
        self.set_canvas(NewPollCanvas(self._poll))

    def button_edit_clicked(self, button):

        self.set_canvas(NewPollCanvas(self._poll))

    def __switch_to_poll(self, sha):
        """
        Set self._poll to the specified poll with sha

        sha -- string
        """

        for poll in self._polls:
            if poll.sha == sha:
                self._poll = poll
                break

    def get_my_polls(self):
        """
        Return list of Polls for all polls I created.
        """

        return [poll for poll in self._polls if poll.author == self.nick]

    def vote_on_poll(self, author, title, choice, votersha):
        """
        Register a vote on a poll from the mesh.

        author -- string
        title -- string
        choice -- integer 0-4
        votersha -- string
          sha1 of the voter nick
        """

        for poll in self._polls:
            if poll.author == author and poll.title == title:
                try:
                    poll.register_vote(choice, votersha)
                    self.get_alert(_('Vote'),
                                   _('Somebody voted on %s') % title)

                    if self._poll == poll and self._current_view == 'poll':
                        self.set_canvas(PollCanvas(self._poll,
                                                   self.current_vote,
                                                   self._view_answer,
                                                   self._previewing))

                except OverflowError:
                    self._logger.debug(
                        'Ignored mesh vote %u from %s:'
                        ' poll reached maximum votes.',
                        choice, votersha)

                except ValueError:
                    self._logger.debug(
                        'Ignored mesh vote %u from %s: poll closed.',
                        choice, votersha)

    # COLABORATION >>

    def __shared_cb(self, activity):
        """
        Callback for completion of sharing this activity.
        """

        self._logger.debug('My activity was shared')
        self.initiating = True

        self.__sharing_setup()

        self._logger.debug('This is my activity: making a tube...')

        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(
            SERVICE, {})

    def __sharing_setup(self):
        """
        Setup my Tubes channel.

        Called from _shared_cb or _joined_cb.
        """

        if self.shared_activity is None:
            self._logger.error('Failed to share or join activity')
            return

        self.conn = self.shared_activity.telepathy_conn
        self.tubes_chan = self.shared_activity.telepathy_tubes_chan
        self.text_chan = self.shared_activity.telepathy_text_chan

        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal(
            'NewTube', self.__new_tube_cb)

        self.shared_activity.connect('buddy-joined', self.__buddy_joined_cb)
        self.shared_activity.connect('buddy-left', self.__buddy_left_cb)

    def __list_tubes_reply_cb(self, tubes):

        for tube_info in tubes:
            self.__new_tube_cb(*tube_info)

    def __list_tubes_error_cb(self, e):
        self._logger.error('ListTubes() failed: %s', e)

    def __joined_cb(self, activity):
        """
        Callback for completion of joining the activity.
        """

        if not self.shared_activity:
            return

        self._logger.debug('Joined an existing shared activity')
        self.get_alert(_('Joined'), "")

        self.initiating = False
        self.__sharing_setup()

        self._logger.debug('This is not my activity: waiting for a tube...')
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
            reply_handler=self.__list_tubes_reply_cb,
            error_handler=self.__list_tubes_error_cb)

    def __new_tube_cb(self, id, initiator, type, service, params, state):
        """
        Callback for when we have a Tube.
        """

        self._logger.debug(
            'New tube: ID=%d initator=%d type=%d srv=%s params=%r state=%d',
            id, initiator, type, service, params, state)

        if (type == telepathy.TUBE_TYPE_DBUS and service == SERVICE):
            if state == telepathy.TUBE_STATE_LOCAL_PENDING:
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].AcceptDBusTube(
                    id)

            tube_conn = TubeConnection(
                self.conn,
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES],
                id,
                group_iface=self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP])

            self.poll_session = PollSession(tube_conn, self.initiating,
                                            self.__get_buddy, self)

    def __buddy_joined_cb(self, activity, buddy):

        self.get_alert(buddy.props.nick, _('Joined'))
        self._logger.debug('Buddy %s joined' % buddy.props.nick)

    def __buddy_left_cb(self, activity, buddy):

        self.get_alert(buddy.props.nick, _('Left'))
        self._logger.debug('Buddy %s left' % buddy.props.nick)

    def __get_buddy(self, cs_handle):
        """
        Get a Buddy from a channel specific handle.
        """

        self._logger.debug('Trying to find owner of handle %u...', cs_handle)
        group = self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP]
        my_csh = group.GetSelfHandle()

        SIGNAL_TELEPATHY = \
            telepathy.CHANNEL_GROUP_FLAG_CHANNEL_SPECIFIC_HANDLES
        self._logger.debug('My handle in that group is %u', my_csh)

        if my_csh == cs_handle:
            handle = self.conn.GetSelfHandle()
            self._logger.debug('CS handle %u belongs to me, %u', cs_handle,
                               handle)

        elif group.GetGroupFlags() & SIGNAL_TELEPATHY:
            handle = group.GetHandleOwners([cs_handle])[0]
            self._logger.debug('CS handle %u belongs to %u', cs_handle, handle)

        else:
            handle = cs_handle
            self._logger.debug('non-CS handle %u belongs to itself', handle)
            assert handle != 0

        return self.pservice.get_buddy_by_telepathy_handle(
            self.conn.service_name, self.conn.object_path, handle)
        # << COLABORATION
