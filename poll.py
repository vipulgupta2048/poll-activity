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
#

# init gthreads before using abiword
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk

GObject.threads_init()

import os
import subprocess
import cPickle
import locale
import logging
import base64

#from hashlib import sha1
#from datetime import date
from gettext import gettext as _
'''
import telepathy
import telepathy.client

from dbus.service import method, signal
from dbus.gobject_service import ExportedGObject

from sugar3.presence.tubeconn import TubeConnection'''

from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbutton import ToolButton
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton

from sugar3.activity import activity
'''
from sugar3.graphics import style
from sugar3.graphics.alert import NotifyAlert

from sugar3.presence import presenceservice
from sugar3.graphics.objectchooser import ObjectChooser
from sugar3.datastore import datastore
from sugar3 import mime
from sugar3 import profile
from gi.repository import Abi
'''
'''
SERVICE = "org.worldwideworkshop.olpc.PollBuilder"
IFACE = SERVICE
PATH = "/org/worldwideworkshop/olpc/PollBuilder"

# Theme definitions - colors
LIGHT_GREEN = '#66CC00'
DARK_GREEN = '#027F01'
PINK = '#FF0198'
YELLOW = '#FFFF00'
GRAY = '#ACACAC'
LIGHT_GRAY = '#E2E2E3'
RED = '#FF0000'
PAD = 10

GRAPH_WIDTH = Gdk.Screen.width() / 3
GRAPH_TEXT_WIDTH = 50
RADIO_SIZE = 32
VIEW_ANSWER = True
REMEMBER_LAST_VOTE = True
PLAY_VOTE_SOUND = False
USE_IMAGE_IN_ANSWER = False
IMAGE_HEIGHT = 100
IMAGE_WIDTH = 100
IMAGE_THUMBNAIL_HEIGHT = 80
IMAGE_THUMBNAIL_WIDTH = 80
'''
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
        '''
        self._logger = logging.getLogger('poll-activity')
        self._logger.debug('Starting Poll activity')

        # get the Presence Service
        self.pservice = presenceservice.get_instance()
        self.initiating = False

        # Buddy object for you
        owner = self.pservice.get_owner()
        self.owner = owner
        self.nick = owner.props.nick
        self.nick_sha1 = sha1(self.nick).hexdigest()

        self._basepath = activity.get_bundle_path()
        #os.chdir(self._basepath)  # required for i18n.py to work

        # setup example poll
        self._polls = set()
        # Removed default polls since it creates too much noise
        # when shared with many on the mesh
        #self._make_default_poll()
        self._has_voted = False
        self._previewing = False
        self._current_view = None  # so we can switch back

        #This property allows result viewing while voting
        self._view_answer = VIEW_ANSWER

        #This property allows remember in the radio button options
        #the last vote
        self._remember_last_vote = REMEMBER_LAST_VOTE

        #This property allows play a sound when click in
        #the button to make a vote
        self._play_vote_sound = PLAY_VOTE_SOUND

        #This property allows use image in answer
        self._use_image = USE_IMAGE_IN_ANSWER

        #This property has the image size
        self._image_size = {'height': IMAGE_HEIGHT, 'width': IMAGE_WIDTH}

        # Lesson plan widget
        self._lessonplan_widget = None
        '''
        self.set_toolbar_box(self.get_toolbar())

        self._root = Gtk.VBox()
        self.set_canvas(self._root)

        #self.set_root(self._select_canvas())

        self.show_all()

        self.poll_session = None  # PollSession
        #self.connect('shared', self._shared_cb)
        #self.connect('joined', self._joined_cb)

    def get_toolbar(self):

        toolbar_box = ToolbarBox()
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        separator = Gtk.SeparatorToolItem()
        toolbar_box.toolbar.insert(separator, -1)

        choose_button = ToolButton('view-list')
        choose_button.set_tooltip(_('Choose a Poll'))
        #choose_button.connect('clicked', self.button_select_clicked)
        toolbar_box.toolbar.insert(choose_button, -1)

        create_button = ToolButton('view-source')
        create_button.set_tooltip(_('Build a Poll'))
        #create_button.connect('clicked', self.button_new_clicked)
        toolbar_box.toolbar.insert(create_button, -1)

        settings_button = ToolButton('preferences-system')
        settings_button.set_tooltip(_('Settings'))
        #settings_button.connect('clicked', self.button_options_clicked)
        toolbar_box.toolbar.insert(settings_button, -1)

        help_button = ToolButton('toolbar-help')
        help_button.set_tooltip(_('Lesson Plans'))
        #help_button.connect('clicked', self._button_lessonplan_cb)
        toolbar_box.toolbar.insert(help_button, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        toolbar_box.toolbar.insert(StopButton(self), -1)

        toolbar_box.show_all()

        return toolbar_box
    '''
    def set_root(self, widget):

        if self._root.get_children():
            self._root.remove(self._root.get_children()[0])

        self._root.pack_start(widget, True, True, 0)'''
    '''
    def _create_pixbufs(self, images_ds_object_id):

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

        return pixbufs'''
    '''
    def _get_images_ds_objects(self, images_ds_object_id):

        images_ds_objects = {}

        for index, ds_object_id in images_ds_object_id.iteritems():
            images_ds_objects[int(index)] = {}

            if not ds_object_id == '':
                images_ds_objects[int(index)]['id'] = ds_object_id
                images_ds_objects[int(index)]['file_path'] = \
                    datastore.get(ds_object_id).file_path

        return images_ds_objects'''
    '''
    def read_file(self, file_path):
        """
        Implement reading from journal

        This is called within sugar3.activity.Activity code
        which provides file_path.
        """

        self._logger.debug('Reading file from datastore via Journal: %s' %
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
            images = self._create_pixbufs(images_ds_objects_id)

            images_ds_object = self._get_images_ds_objects(
                images_ds_objects_id)

            poll = Poll(self, title, author, active,
                        date.fromordinal(int(createdate_i)),
                        maxvoters, question, number_of_options, options,
                        data, votes, images, images_ds_object)

            self._polls.add(poll)

        f.close()

        self.set_root(self._select_canvas())
        self.show_all()'''
    '''
    def write_file(self, file_path):
        """
        Implement writing to the journal

        This is called within sugar3.activity.Activity code
        which provides the file_path.
        """

        s = cPickle.dumps(len(self._polls))

        activity_settings = {
            'view_answer': self._view_answer,
            'remember_last_vote': self._remember_last_vote,
            'play_vote_sound': self._play_vote_sound,
            'use_image': self._use_image}

        s += cPickle.dumps(activity_settings)
        s += cPickle.dumps(self._image_size)

        for poll in self._polls:
            s += poll.dump()

        f = open(file_path, 'w')
        f.write(s)
        f.close()'''
    '''
    def alert(self, title, text=None):
        """
        Show an alert above the activity.
        """

        alert = NotifyAlert(timeout=10)
        alert.props.title = title
        alert.props.msg = text
        self.add_alert(alert)
        alert.connect('response', self._alert_cancel_cb)
        alert.show()'''
    '''
    def _alert_cancel_cb(self, alert, response_id):
        """
        Callback for alert events
        """

        self.remove_alert(alert)'''
    '''
    def _poll_canvas(self):
        """
        Show the poll canvas where children vote on an existing poll.
        """

        self._current_view = 'poll'
        canvasbox = Gtk.VBox()

        # pollbuilderbox is centered within canvasbox
        pollbuilderbox = Gtk.VBox()

        alignment = Gtk.Alignment.new(0.5, 0, 1, 0)
        alignment.add(pollbuilderbox)
        canvasbox.pack_start(alignment, True, True, 0)
        #canvasbox.pack_start(pollbuilderbox, True, True, 0)

        mainbox = Gtk.VBox()
        pollbuilderbox.pack_start(mainbox, True, True, 0)

        if not self._previewing:
            mainbox.pack_start(self._text_mainbox(_('VOTE!')), True, True, 0)

        else:
            mainbox.pack_start(self._text_mainbox(_('Poll Preview')),
                True, True, 0)

        poll_details_box = Gtk.VBox()
        mainbox.pack_start(poll_details_box, True, True, 0)

        self.poll_details_box_head = Gtk.VBox()
        poll_details_box.pack_start(self.poll_details_box_head, False,
            False, 0)

        self.poll_details_box = Gtk.VBox()

        poll_details_scroll = Gtk.ScrolledWindow()

        poll_details_scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.NEVER)

        poll_details_scroll.add_with_viewport(self.poll_details_box)
        poll_details_box.pack_start(poll_details_scroll, True, True, 0)

        self.poll_details_box_tail = Gtk.HBox()
        poll_details_box.pack_start(self.poll_details_box_tail, False, False, 0)

        self.current_vote = None
        self.draw_poll_details_box()

        return canvasbox'''
    '''
    def _select_canvas(self):
        """
        Show the select canvas where children choose an existing poll.
        """

        self._current_view = 'select'
        canvasbox = Gtk.VBox()

        # pollbuilderbox is centered within canvasbox
        pollbuilderbox = Gtk.VBox()
        canvasbox.pack_start(pollbuilderbox, True, True, 10)

        mainbox = Gtk.VBox()
        pollbuilderbox.pack_start(mainbox, True, True, 10)

        mainbox.pack_start(self._text_mainbox(_('Choose a Poll')), False, False, 0)

        poll_details_box = Gtk.VBox()
        mainbox.pack_start(poll_details_box, True, True, 10)

        # add scroll window
        scrolledwindow = Gtk.ScrolledWindow()

        scrolledwindow.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.NEVER)

        poll_selector_box = Gtk.VBox()
        scrolledwindow.add_with_viewport(poll_selector_box)
        poll_details_box.pack_start(scrolledwindow, True, True, 10)

        row_number = 0

        for poll in self._polls:
            sha = poll.sha

            if row_number % 2:
                row_bgcolor = style.COLOR_WHITE.get_int()

            else:
                row_bgcolor = style.COLOR_SELECTION_GREY.get_int()

            row_number += 1
            poll_row = Gtk.HBox()
            poll_selector_box.pack_start(poll_row, False, False, 10)

            title = Gtk.Label(label=poll.title + ' (' + poll.author + ')')
            align = Gtk.Alignment.new(0, 0.5, 0, 0)
            align.add(title)
            poll_row.pack_start(align, True, True, 10)

            if poll.active:
                button = Gtk.Button(_('VOTE'))

            else:
                button = Gtk.Button(_('SEE RESULTS'))

            button.connect('clicked', self._select_poll_button_cb, sha)
            poll_row.pack_start(button, False, False, 10)

            if poll.author == profile.get_nick_name():
                button = Gtk.Button(_('DELETE'))
                button.connect('clicked', self._delete_poll_button_cb, sha)
                poll_row.pack_start(button, False, False, 10)

            poll_row.pack_start(Gtk.Label(
                poll.createdate.strftime('%d/%m/%y')), False, False, 10)

        return canvasbox'''
    '''
    def _lessonplan_canvas(self):
        """
        Show the select canvas where children choose an existing poll.
        """

        previous_view = self._current_view
        self._current_view = 'lessonplan'
        canvasbox = Gtk.VBox()

        # pollbuilderbox is centered within canvasbox
        pollbuilderbox = Gtk.VBox()
        canvasbox.pack_start(pollbuilderbox, True, False, 0)

        mainbox = Gtk.VBox()
        pollbuilderbox.pack_start(mainbox, True, False, 0)

        mainbox.pack_start(self._text_mainbox(_('Lesson Plans')), True, True, 0)

        poll_details_box = Gtk.VBox()
        mainbox.pack_end(poll_details_box, True, True, 0)

        lessonplan = LessonPlanWidget(self._basepath)
        self._lessonplan_widget = lessonplan
        poll_details_box.pack_start(lessonplan, True, True, 0)

        return canvasbox'''
    '''
    def _select_poll_button_cb(self, button, sha=None):
        """
        A VOTE or SEE RESULTS button was clicked.
        """

        if not sha:
            self._logger.debug('Strange, which button was clicked?')
            return

        self._switch_to_poll(sha)
        self._has_voted = False
        self.set_root(self._poll_canvas())
        self.show_all()'''
    '''
    def _delete_poll_button_cb(self, button, sha=None):
        """
        A DELETE button was clicked.
        """

        if not sha:
            self._logger.debug('Strange, which button was clicked?')
            return

        self.delete_poll(sha)
        self.set_root(self._select_canvas())
        self.show_all()'''
    '''
    def delete_poll(self, sha=None, poll=None):
        """
        Delete a poll, either by passing sha or the actual poll object.
        sha -- string, sha property of the poll
        poll -- Poll
        """

        if poll:
            if self._poll == poll:
                self._make_blank_poll

            self._polls.remove(poll)

        if sha:
            if self._poll.sha == sha:
                self._logger.debug('delete_poll: removing current poll')
                self._make_blank_poll()

            for poll in self._polls.copy():
                if poll.sha == sha:
                    self._polls.remove(poll)'''
    '''
    def _load_image(self, pixbuf):
        """
        Load an image.
            @param  name -- string (image file path)
        """

        if not pixbuf == '':
            image = Gtk.Image()
            image.set_from_pixbuf(pixbuf)
            image.show()
            return image

        else:
            logging.exception("Image error")
            return ''
        '''
    '''
    def draw_poll_details_box(self):
        """
        (Re)draw the poll details box

        self.poll_details_box should be already defined on the canvas.
        """

        poll_details_box = self.poll_details_box
        #poll_details_box.remove_all()
        #self.poll_details_box_head.remove_all()
        #self.poll_details_box_tail.remove_all()

        votes_total = self._poll.vote_count

        title = Gtk.Label(label=self._poll.title)
        self.poll_details_box_head.pack_start(title, True, True, 10)
        question = Gtk.Label(label=self._poll.question)
        self.poll_details_box_head.pack_start(question, True, True, 10)

        answer_box = Gtk.VBox()

        answer_box = Gtk.VBox()
        poll_details_box.pack_end(answer_box, True, True, 10)

        group = Gtk.RadioButton()

        for choice in range(self._poll.number_of_options):
            self._logger.debug(self._poll.options[choice])

            answer_row = Gtk.HBox()

            if self._poll.active:
                button = Gtk.RadioButton.new_with_label_from_widget(
                    group, self._poll.options[choice])

                button.connect('toggled',
                    self.vote_choice_radio_button, choice)

                answer_box.pack_start(button, True, False, 10)

                if choice == self.current_vote:
                    button.set_active(True)

            if not self._poll.images[int(choice)] == '':
                hbox = Gtk.HBox()
                hbox.add(self._load_image(self._poll.images[choice]))
                hbox.show()
                answer_row.pack_start(hbox, True, True, 10)

            if not self._poll.active:
                answer_row.pack_start(Gtk.Label(self._poll.options[choice]),
                    True, False, 10)

            if self._view_answer or not self._poll.active:
                if votes_total > 0:
                    self._logger.debug(str(self._poll.data[choice] * 1.0 /
                        votes_total))

                    graph_box = Gtk.HBox()
                    answer_row.pack_start(graph_box, True, True, 10)

                    graph_box.pack_start(Gtk.Label(
                        justify(self._poll.data, choice)), True, True, 10)

                    graph_box.pack_start(Gtk.HBox(), True, True, 10)
                    graph_box.pack_start(Gtk.Label(str(self._poll.data[
                        choice] * 100 / votes_total) + '%'), True, True, 10)

            answer_box.pack_start(answer_row, True, True, 0)

        if self._view_answer or not self._poll.active:
            # Line above total
            line_box = Gtk.HBox()
            answer_box.pack_start(line_box, True, True, 10)

        # total votes
        totals_box = Gtk.HBox()
        answer_box.pack_start(totals_box, True, True, 10)

        spacer = Gtk.HBox()

        spacer.pack_start(Gtk.Label(str(votes_total)), True, True, 10)
        totals_box.pack_start(spacer, True, True, 10)

        totals_box.pack_start(Gtk.Label(' ' + _('votes')), True, True, 10)

        if votes_total < self._poll.maxvoters:
            totals_box.pack_start(
                Gtk.Label(_('(%d votes left to collect)') %
                    (self._poll.maxvoters - votes_total)), True, True, 10)

        # Button area
        if self._poll.active and not self._previewing:
            button_box = Gtk.HBox()
            button = Gtk.Button(_("Vote"))
            button.connect('clicked', self._button_vote_cb)
            button_box.pack_start(button, True, False, 10)
            self.poll_details_box_tail.pack_start(button_box, True, True, 10)

        elif self._previewing:
            button_box = Gtk.HBox()
            button = Gtk.Button(_("Edit Poll"))
            button.connect('clicked', self.button_edit_clicked)
            button_box.pack_start(button, True, True, 0)
            button = Gtk.Button(_("Save Poll"))
            button.connect('clicked', self._button_save_cb)
            button_box.pack_start(button, True, True, 0)
            self.poll_details_box_tail.pack_start(button_box, True, True, 0)
    '''
    '''
    def vote_choice_radio_button(self, widget, data=None):
        """
        Track which radio button has been selected

        This is connected to the vote choice radio buttons.
        data contains the choice (0 - 4) selected.
        """

        self.current_vote = data'''
    '''
    def _play_vote_button_sound(self):

        try:
            subprocess.Popen("aplay extras/vote-sound.wav", shell=True)

        except (OSError, ValueError), e:
            logging.exception(e)'''
    '''
    def _button_vote_cb(self, button):
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
            self._has_voted = True

            try:
                self._poll.register_vote(self.current_vote, self.nick_sha1)

            except OverflowError:
                self._logger.debug('Local vote failed: '
                    'maximum votes already registered.')

            except ValueError:
                self._logger.debug('Local vote failed: poll closed.')

            self._logger.debug('Results: ' + str(self._poll.data))

            if self._play_vote_sound:
                self._play_vote_button_sound()

            if not self._remember_last_vote:
                self.current_vote = None

            self.draw_poll_details_box()

        else:
            alert = NotifyAlert(timeout=3)
            alert.props.title = _('Poll Activity')
            alert.props.msg = _('To vote you have to select first one option')
            self.add_alert(alert)
            alert.connect('response', self._alert_cancel_cb)
            alert.show()'''
    '''
    def button_select_clicked(self, button):
        """
        Show Choose a Poll canvas
        """

        self.set_root(self._select_canvas())
        self.show_all()'''
    '''
    def button_new_clicked(self, button):
        """
        Show Build a Poll canvas.
        """

        # Reset vote data to 0
        self._make_blank_poll()
        self._poll.author = profile.get_nick_name()
        self._poll.active = False
        self.set_root(self._build_canvas())
        self.show_all()'''
    '''
    def button_edit_clicked(self, button):
        """
        Go back from preview to edit
        """

        self.set_root(self._build_canvas())
        self.show_all()'''
    '''
    def button_options_clicked(self, button):

        self.set_root(self._options_canvas())
        self.show_all()'''
    '''
    def _button_choose_image_cb(self, button, data=None, data2=None):

        if hasattr(mime, 'GENERIC_TYPE_IMAGE'):
            chooser = ObjectChooser(_('Choose image'), self,
                Gtk.DialogFlags.MODAL |
                Gtk.DialogFlags.DESTROY_WITH_PARENT,
                what_filter=mime.GENERIC_TYPE_IMAGE)

        else:
            chooser = ObjectChooser(_('Choose image'), self,
                Gtk.DialogFlags.MODAL |
                Gtk.DialogFlags.DESTROY_WITH_PARENT)

        try:
            result = chooser.run()

            if result == Gtk.ResponseType.ACCEPT:
                logging.debug('ObjectChooser: %r' %
                    chooser.get_selected_object())

                jobject = chooser.get_selected_object()

                images_mime_types = mime.get_generic_type(
                    mime.GENERIC_TYPE_IMAGE).mime_types

                if jobject and jobject.file_path and \
                   jobject.metadata.get('mime_type') in images_mime_types:

                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                        jobject.file_path, self._image_size['height'],
                        self._image_size['width'])

                    self._poll.images[int(data)] = pixbuf

                    self._poll.images_ds_objects[int(data)]['id'] = \
                        jobject.object_id

                    self._poll.images_ds_objects[int(data)]['file_path'] = \
                        jobject.file_path

                    self._show_image_thumbnail(data2, data)
                    button.set_label(_('Change Image'))

                else:
                    alert = NotifyAlert(timeout=3)
                    alert.props.title = _('Poll Activity')
                    alert.props.msg = _('Your selection is not an image')
                    self.add_alert(alert)
                    alert.connect('response', self._alert_cancel_cb)
                    alert.show()
        finally:
            chooser.destroy()
            del chooser'''
    '''
    def _show_image_thumbnail(self, parent_box, answer_number):

        hbox = Gtk.HBox()

        image_file_path = self._poll.images_ds_objects[int(answer_number)][
            'file_path']

        pixbuf_thumbnail = GdkPixbuf.Pixbuf.new_from_file_at_size(
            image_file_path, IMAGE_THUMBNAIL_HEIGHT, IMAGE_THUMBNAIL_WIDTH)

        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf_thumbnail)
        image.show()
        hbox.add(image)
        hbox.show()

        chl = parent_box.get_children()

        if len(chl) == 4:
            parent_box.remove(chl[len(chl) - 1])

        parent_box.pack_start(hbox, True, True, 0)'''
    '''
    def _already_loaded_image_in_answer(self, answer_number):

        if not self._poll.images_ds_objects[int(answer_number)] == {}:
            return True

        else:
            return False'''
    '''
    def _build_canvas(self, editing=False, highlight=[]):
        """
        Show the canvas to set up a new poll.

        editing is False to start a new poll, or
        True to edit the current poll

        highlight is a list of strings denoting items failing validation.
        """

        self._current_view = 'build'
        canvasbox = Gtk.VBox()

        canvasbox.pack_start(self._text_mainbox(_('Build a Poll')),
            False, False, 10)

        poll_details_box = Gtk.VBox()
        canvasbox.pack_start(poll_details_box, False, False, 10)

        buildbox = Gtk.VBox()
        poll_details_box.pack_start(buildbox, False, False, 10)

        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label(_('Poll Title:')), False, False, 10)
        entrybox = Gtk.Entry()
        entrybox.set_text(self._poll.title)
        entrybox.connect('changed', self._entry_activate_cb, 'title')
        hbox.pack_start(entrybox, True, True, 10)
        buildbox.pack_start(hbox, False, False, 10)

        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label(_('Question:')), False, False, 10)
        entrybox = Gtk.Entry()
        entrybox.set_text(self._poll.question)
        entrybox.connect('changed', self._entry_activate_cb, 'question')
        hbox.pack_start(entrybox, True, True, 10)
        buildbox.pack_start(hbox, False, False, 10)

        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label(_('Number of votes to collect:')),
            False, False, 10)

        entrybox = Gtk.Entry()
        entrybox.set_text(str(self._poll.maxvoters))
        entrybox.connect('changed', self._entry_activate_cb, 'maxvoters')
        hbox.pack_start(entrybox, True, True, 10)
        buildbox.pack_start(hbox, False, False, 10)

        for choice in self._poll.options.keys():
            hbox = Gtk.HBox()
            hbox.pack_start(Gtk.Label(_('Answer %d:') % (choice + 1)),
                False, False, 10)

            entrybox = Gtk.Entry()
            entrybox.set_text(self._poll.options[choice])
            entrybox.connect('changed', self._entry_activate_cb, str(choice))
            hbox.pack_start(entrybox, True, True, 10)

            if self._use_image:
                if self._already_loaded_image_in_answer(choice):
                    button = Gtk.Button(_("Change Image"))
                    hbox.pack_start(button, True, False, 10)
                    self._show_image_thumbnail(hbox, choice)

                else:
                    button = Gtk.Button(_("Add Image"))
                    hbox.pack_start(button, True, False, 10)

                button.connect('clicked', self._button_choose_image_cb,
                    str(choice), hbox)

            buildbox.pack_start(hbox, False, False, 10)

        # PREVIEW & SAVE buttons
        hbox = Gtk.HBox()
        button = Gtk.Button(_("Step 1: Preview"))
        button.connect('clicked', self._button_preview_cb)
        hbox.pack_start(button, True, True, 10)
        button = Gtk.Button(_("Step 2: Save"))
        button.connect('clicked', self._button_save_cb)
        hbox.pack_start(button, True, True, 10)

        buildbox.pack_start(hbox, False, False, 10)

        return canvasbox'''
    '''
    def _options_canvas(self, editing=False, highlight=[]):
        """
        Show the options canvas.
        """

        self._current_view = 'options'
        canvasbox = Gtk.VBox()
        alignment = Gtk.Alignment.new(0.5, 0, 0, 0)
        # optionsbox is centered within canvasbox
        optionsbox = Gtk.VBox()

        alignment.add(optionsbox)
        canvasbox.pack_start(alignment, True, True, 0)

        mainbox = Gtk.VBox()

        optionsbox.pack_start(mainbox, True, False, 0)

        mainbox.pack_start(self._text_mainbox(_('Settings')), True, True, 10)

        options_details_box = Gtk.VBox()
        mainbox.pack_start(options_details_box, True, False, 10)

        #options widgets
        options_widgets = []

        viewResultCB = Gtk.CheckButton(label=_('Show answers while voting'))
        viewResultCB.set_active(self._view_answer)
        viewResultCB.connect('toggled', self._view_result_checkbox_cb)
        options_details_box.pack_start(viewResultCB, True, True, 10)

        rememberVoteCB = Gtk.CheckButton(label=_('Remember last vote'))
        rememberVoteCB.set_active(self._remember_last_vote)
        rememberVoteCB.connect('toggled', self._remember_last_vote_checkbox_cb)
        options_details_box.pack_start(rememberVoteCB, True, True, 10)

        playVoteSoundCB = Gtk.CheckButton(
            label=_('Play a sound when make a vote'))
        playVoteSoundCB.set_active(self._play_vote_sound)
        playVoteSoundCB.connect('toggled', self._play_vote_sound_checkbox_cb)
        options_details_box.pack_start(playVoteSoundCB, True, True, 10)

        vbox = Gtk.VBox()
        useImageCB = Gtk.CheckButton(label=_('Use image in answer'))
        useImageCB.set_active(self._use_image)
        options_details_box.pack_start(useImageCB, True, True, 10)

        hbox2 = Gtk.HBox()
        hbox2.pack_start(Gtk.Label(_('Image Size: ')), True, True, 10)
        entrybox = Gtk.Entry(max_length=3)

        entrybox.modify_bg(Gtk.StateType.INSENSITIVE,
            style.COLOR_WHITE.get_gdk_color())

        entrybox.set_text(str(self._image_size['height']))
        entrybox.connect('changed', self._entry_image_size_cb, 'height')
        hbox2.pack_start(entrybox, True, True, 10)
        hbox2.pack_start(Gtk.Label('x'), True, True, 10)
        entrybox = Gtk.Entry(max_length=3)

        entrybox.modify_bg(Gtk.StateType.INSENSITIVE,
            style.COLOR_WHITE.get_gdk_color())

        entrybox.set_text(str(self._image_size['width']))
        entrybox.connect('changed', self._entry_image_size_cb, 'width')
        hbox2.pack_start(entrybox, True, True, 10)
        useImageCB.connect('toggled', self._use_image_checkbox_cb, vbox, hbox2)

        if self._use_image:
            vbox.pack_start(hbox2, True, True, 10)

        options_details_box.pack_start(vbox, True, True, 0)

        hbox = Gtk.HBox()
        # SAVE button
        button = Gtk.Button(_("Save"))
        button.connect('clicked', self._button_save_options_cb)
        hbox.pack_start(button, True, True, 10)

        options_details_box.pack_end(hbox, True, True, 10)

        return canvasbox'''
    '''
    def _view_result_checkbox_cb(self, checkbox, data=None):
        self._view_answer = checkbox.get_active()

    def _remember_last_vote_checkbox_cb(self, checkbox, data=None):
        self._remember_last_vote = checkbox.get_active()

    def _play_vote_sound_checkbox_cb(self, checkbox, data=None):
        self._play_vote_sound = checkbox.get_active()

    def _use_image_checkbox_cb(self, checkbox, data=None, data2=None):

        self._use_image = checkbox.get_active()

        if checkbox.get_active():
            data.add(data2)

        else:
            data.remove(data2)'''
    '''
    def _button_preview_cb(self, button, data=None):
        """
        Preview button clicked.
        """

        # Validate data
        failed_items = self._validate()

        if failed_items:
            self.set_root(self._build_canvas(highlight=failed_items))
            self.show_all()
            return

        # Data OK
        self._poll.active = True  # Show radio buttons
        self._previewing = True
        self.set_root(self._poll_canvas())

        self.show_all()'''
    '''
    def _button_save_cb(self, button, data=None):
        """
        Save button clicked.
        """

        # Validate data
        failed_items = self._validate()

        if failed_items:
            self.set_root(self._build_canvas(highlight=failed_items))
            self.show_all()
            return

        # Data OK
        self._previewing = False
        self._poll.active = True
        self._polls.add(self._poll)
        self._poll.broadcast_on_mesh()
        self.set_root(self._poll_canvas())
        self.show_all()'''
    '''
    def _button_save_options_cb(self, button, data=None):

        alert = NotifyAlert(timeout=3)
        alert.props.title = _('Poll Activity')
        alert.props.msg = _('The settings have been saved')
        self.add_alert(alert)
        alert.connect('response', self._alert_cancel_cb)
        alert.show()'''
    '''
    def _entry_activate_cb(self, entrycontrol, data=None):

        text = entrycontrol.props.text

        if data:
            if text:
                if data == 'title':
                    self._poll.title = text

                elif data == 'question':
                    self._poll.question = text

                elif data == 'maxvoters':
                    try:
                        self._poll.maxvoters = int(text)

                    except ValueError:
                        self._poll.maxvoters = 0  # invalid, will be trapped

                else:
                    self._poll.options[int(data)] = text'''
    '''
    def _entry_image_size_cb(self, entrycontrol, data=None):

        text = entrycontrol.props.text

        if data:
            if text:
                self._image_size[data] = int(text)'''
    '''
    def _make_blank_poll(self):
        """
        Initialize the poll state.
        """

        self._poll = Poll(activity=self)
        self.current_vote = None'''
    '''
    def _make_default_poll(self):
        """
        A hardcoded poll for first time launch.
        """

        self._poll = Poll(
            activity=self, title=self.nick + ' ' + _('Favorite Color'),
            author=self.nick, active=True,
            question=_('What is your favorite color?'),
            options={0: ('Green'),
                     1: ('Red'),
                     2: ('Blue'),
                     3: _('Orange'),
                     4: _('None of the above')})

        self.current_vote = None
        self._polls.add(self._poll)'''
    '''
    def _validate(self):

        failed_items = []

        if self._poll.title == '':
            failed_items.append('title')

        if self._poll.question == '':
            failed_items.append('question')

        if self._poll.maxvoters == 0:
            failed_items.append('maxvoters')

        if self._poll.options[0] == '':
            failed_items.append('0')

        if self._poll.options[1] == '':
            failed_items.append('1')

        if self._poll.options[3] != '' and self._poll.options[2] == '':
            failed_items.append('2')

        if self._poll.options[4] != '' and self._poll.options[3] == '':
            failed_items.append('3')

        if self._poll.options[2] == '':
            self._poll.number_of_options = 2

        elif self._poll.options[3] == '':
            self._poll.number_of_options = 3

        elif self._poll.options[4] == '':
            self._poll.number_of_options = 4

        else:
            self._poll.number_of_options = 5

        return failed_items'''
    '''
    def _get_sha(self):
        """
        Return a sha1 hash of something about this poll.

        Currently we sha1 the poll title and author.
        This is used for the filename of the saved poll.
        It will probably be used for the mesh networking too.
        """

        return self._poll.sha'''
    '''
    def _switch_to_poll(self, sha):
        """
        Set self._poll to the specified poll with sha

        sha -- string
        """

        for poll in self._polls:
            if poll.sha == sha:
                self._poll = poll'''
    '''
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
                    self.alert(_('Vote'),
                        _('Somebody voted on %s') % title)

                except OverflowError:
                    self._logger.debug('Ignored mesh vote %u from %s:'
                        ' poll reached maximum votes.',
                        choice, votersha)

                except ValueError:
                    self._logger.debug('Ignored mesh vote %u from %s:'
                        ' poll closed.',
                        choice, votersha)'''
    '''
    def _canvas_lessonplanbox(self, lesson_return=None):
        """
        Render the lessonplanbox.

        disconnect_lp True does not connect the button.
        """

        lessonplanbox = Gtk.VBox()

        if lesson_return:
            highlight = True
            button = Gtk.Button(_("Close Lessons"))

        else:
            highlight = False
            button = Gtk.Button(_("Lesson Plans"))

        if lesson_return:
            button.connect('clicked', self._button_closelessonplan_cb,
                lesson_return)

        else:
            button.connect('clicked', self._button_lessonplan_cb)

        lessonplanbox.pack_start(button, True, True, 0)
        #, highlight=highlight)))
        return lessonplanbox'''
    '''
    def _button_lessonplan_cb(self, button):
        """
        Lesson Plan button clicked.
        """

        self._logger.debug('%s -> Lesson Plan' % self._current_view)
        self.set_root(self._lessonplan_canvas())
        self.show_all()'''
    '''
    def _button_closelessonplan_cb(self, button, lesson_return):
        """
        Lesson Plan button clicked in Lesson Plan view.

        Go back to the view we had previously.
        """

        self._logger.debug('Lesson plans -> %s' % lesson_return)

        if lesson_return == 'poll':
            self.set_root(self._poll_canvas())

        elif lesson_return == 'select':
            self.set_root(self._select_canvas())

        elif lesson_return == 'build':
            self.set_root(self._build_canvas())

        self.show_all()

        del self._lessonplan_widget
        self._lessonplan_widget = None'''
    '''
    def _text_mainbox(self, text, warn=False):
        """
        Main text style.

        warn=True makes the text color RED and appends ???.
        """

        title_box = Gtk.VBox()
        label = Gtk.Label()
        label.set_markup('<big><b>%s</b></big>' % text)
        title_box.add(label)

        return title_box'''
    '''
    def _shared_cb(self, activity):
        """
        Callback for completion of sharing this activity.
        """

        self._logger.debug('My activity was shared')
        self.initiating = True
        self._sharing_setup()

        self._logger.debug('This is my activity: making a tube...')

        id = self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(
            SERVICE, {})'''
    '''
    def _sharing_setup(self):
        """
        Setup my Tubes channel.

        Called from _shared_cb or _joined_cb.
        """

        if self._shared_activity is None:
            self._logger.error('Failed to share or join activity')
            return

        self.conn = self._shared_activity.telepathy_conn
        self.tubes_chan = self._shared_activity.telepathy_tubes_chan
        self.text_chan = self._shared_activity.telepathy_text_chan

        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal(
            'NewTube', self._new_tube_cb)

        self._shared_activity.connect('buddy-joined', self._buddy_joined_cb)
        self._shared_activity.connect('buddy-left', self._buddy_left_cb)'''
    '''
    def _list_tubes_reply_cb(self, tubes):

        for tube_info in tubes:
            self._new_tube_cb(*tube_info)

    def _list_tubes_error_cb(self, e):
        self._logger.error('ListTubes() failed: %s', e)

    def _joined_cb(self, activity):
        """
        Callback for completion of joining the activity.
        """

        if not self._shared_activity:
            return

        self._logger.debug('Joined an existing shared activity')
        self.alert(_('Joined'))
        self.initiating = False
        self._sharing_setup()

        self._logger.debug('This is not my activity: waiting for a tube...')
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
            reply_handler=self._list_tubes_reply_cb,
            error_handler=self._list_tubes_error_cb)'''
    '''
    def _new_tube_cb(self, id, initiator, type, service, params, state):
        """
        Callback for when we have a Tube.
        """

        self._logger.debug('New tube: ID=%d initator=%d type=%d service=%s '
           'params=%r state=%d', id, initiator, type, service,
           params, state)

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
                self._get_buddy, self)'''
    '''
    def _buddy_joined_cb(self, activity, buddy):

        self.alert(buddy.props.nick, _('Joined'))
        self._logger.debug('Buddy %s joined' % buddy.props.nick)

    def _buddy_left_cb(self, activity, buddy):

        self.alert(buddy.props.nick, _('Left'))
        self._logger.debug('Buddy %s left' % buddy.props.nick)'''
    '''
    def _get_buddy(self, cs_handle):
        """
        Get a Buddy from a channel specific handle.
        """

        self._logger.debug('Trying to find owner of handle %u...', cs_handle)
        group = self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP]
        my_csh = group.GetSelfHandle()

        SIGNAL_TELEPATHY = telepathy.CHANNEL_GROUP_FLAG_CHANNEL_SPECIFIC_HANDLES
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
            self.conn.service_name, self.conn.object_path, handle)'''
'''
class Poll():
    """
    Represent the data of one poll.
    """

    def __init__(self, activity=None, title='', author='', active=False,
        createdate=date.today(), maxvoters=20, question='',
        number_of_options=5, options=None, data=None, votes=None,
        images=None, images_ds_objects=None):

        ### Create the Poll.
        self.activity = activity
        self.title = title
        self.author = author
        self.active = active
        self.createdate = createdate
        self.maxvoters = maxvoters
        self.question = question
        self.number_of_options = number_of_options
        self.options = (options or {0: '', 1: '', 2: '', 3: '', 4: ''})
        self.images = (images or {0: '', 1: '', 2: '', 3: '', 4: ''})

        self.images_ds_objects = (images_ds_objects or {0: {}, 1: {}, 2: {},
            3: {}, 4: {}})

        self.data = (data or {0: 0, 1: 0, 2: 0, 3: 0, 4: 0})
        self.votes = (votes or {})
        self._logger = logging.getLogger('poll-activity.Poll')
        self._logger.debug('Creating Poll(%s by %s)' % (title, author))

    def dump(self):
        """
        Dump a pickled version for the journal.
            The attributes may be dbus types. These are not serialisable
            with pickle at the moment, so convert them to builtin types.
            Pay special attention to dicts - we need to convert the keys
            and values too.
        """

        s = cPickle.dumps(str(self.title))
        s += cPickle.dumps(str(self.author))
        s += cPickle.dumps(bool(self.active))
        s += cPickle.dumps(self.createdate.toordinal())
        s += cPickle.dumps(int(self.maxvoters))
        s += cPickle.dumps(str(self.question))
        s += cPickle.dumps(int(self.number_of_options))

        options = {}

        for key in self.options:
            value = self.options[key]
            options[int(key)] = str(value)

        data = {}

        for key in self.data:
            value = self.data[key]
            data[int(key)] = int(value)

        votes = {}

        for key in self.votes:
            value = self.votes[key]
            votes[str(key)] = int(value)

        images_objects_id = {}

        for key in self.images_ds_objects:
            if not self.images_ds_objects[key] == {}:
                value = self.images_ds_objects[key]['id']
                images_objects_id[int(key)] = str(value)

            else:
                images_objects_id[int(key)] = ''

        s += cPickle.dumps(options)
        s += cPickle.dumps(data)
        s += cPickle.dumps(votes)
        s += cPickle.dumps(images_objects_id)

        return s

    @property
    def vote_count(self):
        """
        Return the total votes cast.
        """

        total = 0

        for choice in self.options.keys():
            total += self.data[choice]

        return total

    @property
    def sha(self):
        """
        Return a sha1 hash of something about this poll.

        Currently we sha1 the poll title and author.
        """

        return sha1(self.title + self.author).hexdigest()

    def register_vote(self, choice, votersha):
        """
        Register a vote on the poll.

        votersha -- string
          sha1 of the voter nick
        """

        self._logger.debug('In Poll.register_vote')

        if self.active:
            if self.vote_count < self.maxvoters:
                self._logger.debug('About to vote')
                # XXX 27/10/07 Morgan: Allowing multiple votes per XO
                #                      per Shannon's request.
                ## if voter already voted, change their vote:
                #if votersha in self.votes:
                #    self._logger.debug('%s already voted, decrementing their '
                #        'old choice %d' % (votersha, self.votes[votersha]))
                #    self.data[self.votes[votersha]] -= 1

                self.votes[votersha] = choice
                self.data[choice] += 1
                self._logger.debug(
                    'Recording vote %d by %s on %s by %s' %
                    (choice, votersha, self.title, self.author))

                ### Close poll:
                if self.vote_count >= self.maxvoters:
                    self.active = False
                    self._logger.debug('Poll hit maxvoters, closing')

                if self.activity.poll_session:
                    # We are shared so we can send the Vote signal if I voted
                    if votersha == self.activity.nick_sha1:
                        self._logger.debug(
                            'Shared, I voted so sending signal')

                        self.activity.poll_session.Vote(
                            self.author, self.title, choice, votersha)

            else:
                raise OverflowError('Poll reached maxvoters')

        else:
            raise ValueError('Poll closed')

    def _pixbuf_save_cb(self, buf, data):

        data[0] += buf

        return True

    def get_buffer(self, pixbuf):

        data = [""]
        pixbuf.save_to_callback(self._pixbuf_save_cb, "png", {}, data)

        return str(data[0])

    def broadcast_on_mesh(self):

        if self.activity.poll_session:
            images_buf = {}

            for img_number, img_pixbuf in self.images.iteritems():
                if not img_pixbuf == '':
                    images_buf[img_number] = base64.b64encode(
                        self.get_buffer(img_pixbuf))

                else:
                    images_buf[img_number] = img_pixbuf

            # We are shared so we can broadcast this poll
            self.activity.poll_session.UpdatedPoll(
                self.title, self.author, self.active,
                self.createdate.toordinal(),
                self.maxvoters, self.question, self.number_of_options,
                self.options, self.data, self.votes, images_buf)'''
'''
class PollSession(ExportedGObject):
    """
    The bit that talks over the TUBES!!!
    """

    def __init__(self, tube, is_initiator, get_buddy, activity):
        """
        Initialise the PollSession.

        tube -- TubeConnection
        is_initiator -- boolean, True = we are sharing, False = we are joining
        get_buddy -- function
        activity -- PollBuilder (sugar3.activity.Activity)
        """

        super(PollSession, self).__init__(tube, PATH)
        self._logger = logging.getLogger('poll-activity.PollSession')
        self.tube = tube
        self.is_initiator = is_initiator
        self.entered = False  # Have we set up the tube?
        self._get_buddy = get_buddy  # Converts handle to Buddy object
        self.activity = activity  # PollBuilder
        self.tube.watch_participants(self.participant_change_cb)

    def participant_change_cb(self, added, removed):
        """
        Callback when tube participants change.
        """

        self._logger.debug('In participant_change_cb')

        if added:
            self._logger.debug('Adding participants: %r' % added)

        if removed:
            self._logger.debug('Removing participants: %r' % removed)

        for handle, bus_name in added:
            buddy = self._get_buddy(handle)

            if buddy is not None:
                self._logger.debug('Buddy %s was added' % buddy.props.nick)

        for handle in removed:
            buddy = self._get_buddy(handle)

            if buddy is not None:
                self._logger.debug('Buddy %s was removed' % buddy.props.nick)
                # Set buddy's polls to not active so I can't vote on them

                for poll in self.activity._polls:
                    if poll.author == buddy.props.nick:
                        poll.active = False

                        self._logger.debug(
                            'Closing poll %s of %s who just left.' %
                            (poll.title, poll.author))

        if not self.entered:
            if self.is_initiator:
                self._logger.debug("I'm initiating the tube")

            else:
                self._logger.debug('Joining, sending Hello')
                self.Hello()

            self.tube.add_signal_receiver(
                self.hello_cb, 'Hello', IFACE,
                path=PATH,
                sender_keyword='sender')

            self.tube.add_signal_receiver(
                self.vote_cb, 'Vote', IFACE,
                path=PATH,
                sender_keyword='sender')

            self.tube.add_signal_receiver(
                self.helloback_cb, 'HelloBack',
                IFACE, path=PATH,
                sender_keyword='sender')

            self.tube.add_signal_receiver(
                self.updatedpoll_cb, 'UpdatedPoll',
                IFACE, path=PATH,
                sender_keyword='sender')

            self.my_bus_name = self.tube.get_unique_name()

            self.entered = True

    @signal(dbus_interface=IFACE, signature='')
    def Hello(self):
        """
        Request that my UpdatePoll method is called to let me know about
        other known polls.
        """

    @signal(dbus_interface=IFACE, signature='ssus')
    def Vote(self, author, title, choice, votersha):
        """
        Send my vote on author's poll.

        author -- string, buddy name
        title -- string, poll title
        choice -- integer 0-4, selected vote
        votersha -- string, sha1 of voter's nick
        """

    @signal(dbus_interface=IFACE, signature='s')
    def HelloBack(self, recipient):
        """
        Respond to Hello.

        recipient -- string, sender of Hello.
        """

    @signal(dbus_interface=IFACE, signature='ssuuusua{us}a{uu}a{su}a{us}')
    def UpdatedPoll(self, title, author, active, createdate, maxvoters,
        question, number_of_options, options, data, votes,
        images_buf):
        """
        Broadcast a new poll to the mesh.
        """

    def hello_cb(self, sender=None):
        """
        Tell the newcomer what's going on.
        """

        assert sender is not None

        self._logger.debug('Newcomer %s has joined and sent Hello', sender)
        # sender is a bus name - check if it's me:
        if sender == self.my_bus_name:
            # then I don't want to respond to my own Hello
            return

        # Send my polls
        for poll in self.activity.get_my_polls():
            self._logger.debug('Telling %s about my %s' %
                (sender, poll.title))

            #images_properties = poll.simplify_images_dictionary()
            images_buf = {}

            for img_number, img_pixbuf in poll.images.iteritems():
                if not img_pixbuf == '':
                    images_buf[img_number] = base64.b64encode(
                        poll.get_buffer(img_pixbuf))

                else:
                    images_buf[img_number] = img_pixbuf

            self.tube.get_object(sender, PATH).UpdatePoll(
                poll.title, poll.author, int(poll.active),
                poll.createdate.toordinal(),
                poll.maxvoters, poll.question, poll.number_of_options,
                poll.options, poll.data, poll.votes, images_buf,
                dbus_interface=IFACE)

        # Ask for other's polls back
        self.HelloBack(sender)

    def helloback_cb(self, recipient, sender):
        """
        Reply to Hello.

        recipient -- string, the XO who send the original Hello.

        Other XOs should ignore this signal.
        """

        self._logger.debug('*** In helloback_cb: recipient: %s, sender: %s' %
            (recipient, sender))

        if sender == self.my_bus_name:
            # Ignore my own signal
            return

        if recipient != self.my_bus_name:
            # This is not for me
            return

        self._logger.debug('*** It was for me, so sending my polls back.')

        for poll in self.activity.get_my_polls():
            self._logger.debug('Telling %s about my %s' %
                (sender, poll.title))

            images_buf = {}

            for img_number, img_pixbuf in poll.images.iteritems():
                if not img_pixbuf == '':
                    images_buf[img_number] = base64.b64encode(
                        poll.get_buffer(img_pixbuf))

                else:
                    images_buf[img_number] = img_pixbuf

            self.tube.get_object(sender, PATH).UpdatePoll(
                poll.title, poll.author, int(poll.active),
                poll.createdate.toordinal(),
                poll.maxvoters, poll.question, poll.number_of_options,
                poll.options, poll.data, poll.votes, images_buf,
                dbus_interface=IFACE)

    def get_pixbuf(self, img_encode_buf):

        decode_img_buf = base64.b64decode(img_encode_buf)
        loader = GdkPixbuf.PixbufLoader()
        loader.write(decode_img_buf)
        loader.close()
        pixbuf = loader.get_pixbuf()

        return pixbuf

    def updatedpoll_cb(self, title, author, active, createdate, maxvoters,
        question, number_of_options, options_d, data_d,
        votes_d, images_buf_d, sender):
        """
        Handle an UpdatedPoll signal by creating a new Poll.
        """

        self._logger.debug('Received UpdatedPoll from %s' % sender)

        if sender == self.my_bus_name:
            # Ignore my own signal
            return

        # We get the parameters as dbus types. These are not serialisable
        # with pickle at the moment, so convert them to builtin types.
        # Pay special attention to dicts - we need to convert the keys
        # and values too.

        title = str(title)
        author = str(author)
        active = bool(active)
        createdate = date.fromordinal(int(createdate))
        maxvoters = int(maxvoters)
        question = str(question)
        number_of_options = int(number_of_options)
        options = {}

        for key in options_d:
            value = options_d[key]
            options[int(key)] = str(value)

        data = {}

        for key in data_d:
            value = data_d[key]
            data[int(key)] = int(value)

        votes = {}

        for key in votes_d:
            value = votes_d[key]
            votes[str(key)] = int(value)

        images = {}

        for key in images_buf_d:
            if not images_buf_d[key] == '':
                images[int(key)] = self.get_pixbuf(images_buf_d[key])

            else:
                images[int(key)] = ''

        poll = Poll(self.activity, title, author, active,
            createdate, maxvoters, question, number_of_options,
            options, data, votes, images)

        self.activity._polls.add(poll)

        self.activity.alert(
            _('New Poll'),
            _("%(author)s shared a poll "
            "'%(title)s' with you.") % {'author': author,
            'title': title})

    def vote_cb(self, author, title, choice, votersha, sender=None):
        """
        Receive somebody's vote signal.

        author -- string, buddy name
        title -- string, poll title
        choice -- integer 0-4, selected vote
        votersha -- string, sha1 hash of voter nick
        """

        # FIXME: validate the choices, set the vote.
        # XXX We could possibly get the nick of sender and sha1 it
        #     to verify the vote is coming from the voter.
        if sender == self.my_bus_name:
            # Don't respond to my own Vote signal
            return

        self._logger.debug('In vote_cb. sender: %r' % sender)
        self._logger.debug('%s voted %d on %s by %s' % (votersha, choice,
            title, author))

        self.activity.vote_on_poll(author, title, choice, votersha)

    @method(dbus_interface=IFACE, in_signature='ssuuusua{us}a{uu}a{su}a{us}',
        out_signature='')
    def UpdatePoll(self, title, author, active, createdate, maxvoters,
        question, number_of_options, options_d, data_d, votes_d,
        images_buf_d):
        """
        To be called on the incoming buddy by the other participants
        to inform you of their polls and state.

            We get the parameters as dbus types. These are not serialisable
            with pickle at the moment, so convert them to builtin types.
            Pay special attention to dicts - we need to convert the keys
            and values too.
        """

        title = str(title)
        author = str(author)
        active = bool(active)
        createdate = date.fromordinal(int(createdate))
        maxvoters = int(maxvoters)
        question = str(question)
        number_of_options = int(number_of_options)

        options = {}

        for key in options_d:
            value = options_d[key]
            options[int(key)] = str(value)

        data = {}

        for key in data_d:
            value = data_d[key]
            data[int(key)] = int(value)

        votes = {}

        for key in votes_d:
            value = votes_d[key]
            votes[str(key)] = int(value)

        images = {}

        for key in images_buf_d:
            if not images_buf_d[key] == '':
                images[int(key)] = self.get_pixbuf(images_buf_d[key])

            else:
                images[int(key)] = ''

        poll = Poll(self.activity, title, author, active,
            createdate, maxvoters, question, number_of_options,
            options, data, votes, images)

        self.activity._polls.add(poll)
        self.activity.alert(
            _('New Poll'),
            _("%(author)s shared a poll "
            "'%(title)s' with you.") % {'author': author,
            'title': title})

    @method(dbus_interface=IFACE, in_signature='s', out_signature='')
    def PollsWanted(self, sender):
        """
        Notification to send my polls to sender.
        """

        for poll in self.activity.get_my_polls():
            images_buf = {}

            for img_number, img_pixbuf in poll.images.iteritems():
                if not img_pixbuf == '':
                    images_buf[img_number] = base64.b64encode(
                        poll.get_buffer(img_pixbuf))

                else:
                    images_buf[img_number] = img_pixbuf

            self.tube.get_object(sender, PATH).UpdatePoll(
                poll.title, poll.author, int(poll.active),
                poll.createdate.toordinal(),
                poll.maxvoters, poll.question, poll.number_of_options,
                poll.options, poll.data, poll.votes, images_buf,
                dbus_interface=IFACE)'''
'''
def justify(textdict, choice):
    """
    Take a {} of numbers, and right justify the chosen item.

    textdict is a dict of {n: m} where n and m are integers.
    choice is one of textdict.keys()

    Returns a string of '   m' with m right-justified
    so that the longest value in the dict can fit.
    """

    max_len = 0

    for num in textdict.values():
        if len(str(num)) > max_len:
            max_len = len(str(num))

    value = str(textdict[choice])
    return value.rjust(max_len)'''
'''
class LessonPlanWidget(Gtk.Notebook):
    """
    Create a Notebook widget for displaying lesson plans in tabs.

    basepath -- string, path of directory containing lesson plans.
    """

    def __init__(self, basepath):
        super(LessonPlanWidget, self).__init__()

        lessons = filter(
            lambda x: os.path.isdir(os.path.join(basepath,
            'lessons', x)),
            os.listdir(os.path.join(basepath, 'lessons')))

        lessons.sort()

        for lesson in lessons:
            self._load_lesson(
                os.path.join(basepath,
                'lessons', lesson),
                _(lesson))

    def _load_lesson(self, path, name):
        """
        Load the lesson content from a .abw, taking l10n into account.

        path -- string, path of lesson plan file, e.g. lessons/Introduction
        lesson -- string, name of lesson
        """

        code, encoding = locale.getdefaultlocale()
        canvas = Abi.Widget()
        canvas.show()
        files = map(
            lambda x: os.path.join(path, '%s.abw' % x),
            ('_' + code.lower(), '_' + code.split('_')[0].lower(),
             'default'))

        files = filter(lambda x: os.path.exists(x), files)
        canvas.load_file('file://%s' % files[0], '')
        canvas.view_online_layout()
        canvas.zoom_width()
        canvas.set_show_margin(False)
        self.append_page(canvas, Gtk.Label(label=name))'''
