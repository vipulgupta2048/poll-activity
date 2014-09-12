#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import os
import logging
import base64

from datetime import date
from gettext import gettext as _

from gi.repository import GdkPixbuf

from hashlib import sha1

from dbus.service import method, signal
from dbus.gobject_service import ExportedGObject

SERVICE = "org.worldwideworkshop.olpc.PollBuilder"
IFACE = SERVICE
PATH = "/org/worldwideworkshop/olpc/PollBuilder"


class Poll():
    """
    Represent the data of one poll.
    """

    def __init__(
            self, activity=None, title='', author='', active=False,
            createdate=date.today(), maxvoters=20, question='',
            number_of_options=5, options=None, data=None, votes=None,
            images=None, images_ds_objects=None):

        # Create the Poll.
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
        self.last_vote = None

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
        data = {}
        data['title'] = str(self.title)
        data['author'] = str(self.author)
        data['active'] = bool(self.active)
        data['createdate'] = self.createdate.toordinal()
        data['maxvoters'] = int(self.maxvoters)
        data['question'] = str(self.question)
        data['number_of_options'] = int(self.number_of_options)
        data['options'] = self.options
        data['data'] = self.data
        data['votes'] = self.votes

        images_objects_id = {}

        for key in self.images_ds_objects:
            if not self.images_ds_objects[key] == {}:
                value = self.images_ds_objects[key]['id']
                images_objects_id[int(key)] = str(value)
            else:
                images_objects_id[int(key)] = ''

        data['images_ds_objects'] = images_objects_id
        return data

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
                # if voter already voted, change their vote:
                # if votersha in self.votes:
                #    self._logger.debug('%s already voted, decrementing their '
                #        'old choice %d' % (votersha, self.votes[votersha]))
                #    self.data[self.votes[votersha]] -= 1

                self.votes[votersha] = choice
                self.data[choice] += 1
                self.last_vote = choice
                self._logger.debug(
                    'Recording vote %d by %s on %s by %s' %
                    (choice, votersha, self.title, self.author))

                # Close poll:
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

    def get_buffer(self, pixbuf):

        path = "/dev/shm/pix.png"
        pixbuf.savev(path, "png", [], [])

        pixbuf_file = open(path, 'rb')
        image_string = base64.b64encode(pixbuf_file.read())
        pixbuf_file.close()

        os.remove(path)

        return image_string

    def broadcast_on_mesh(self):

        if self.activity.poll_session:
            images_buf = {}

            for img_number, img_pixbuf in self.images.iteritems():
                if not img_pixbuf == '':
                    images_buf[img_number] = self.get_buffer(img_pixbuf)

                else:
                    images_buf[img_number] = img_pixbuf

            # We are shared so we can broadcast this poll
            self.activity.poll_session.UpdatedPoll(
                self.title, self.author, self.active,
                self.createdate.toordinal(),
                self.maxvoters, self.question, self.number_of_options,
                self.options, self.data, self.votes, images_buf)


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
        self.tube.watch_participants(self.__participant_change_cb)

    def __participant_change_cb(self, added, removed):
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
                self.__hello_cb, 'Hello', IFACE,
                path=PATH,
                sender_keyword='sender')

            self.tube.add_signal_receiver(
                self.__vote_cb, 'Vote', IFACE,
                path=PATH,
                sender_keyword='sender')

            self.tube.add_signal_receiver(
                self.__helloback_cb, 'HelloBack',
                IFACE, path=PATH,
                sender_keyword='sender')

            self.tube.add_signal_receiver(
                self.__updatedpoll_cb, 'UpdatedPoll',
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

    def __hello_cb(self, sender=None):
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

            # images_properties = poll.simplify_images_dictionary()
            images_buf = {}

            for img_number, img_pixbuf in poll.images.iteritems():
                if not img_pixbuf == '':
                    images_buf[img_number] = poll.get_buffer(img_pixbuf)

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

    def __helloback_cb(self, recipient, sender):
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
                    images_buf[img_number] = poll.get_buffer(img_pixbuf)

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

    def __updatedpoll_cb(self, title, author, active, createdate, maxvoters,
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

        self.activity.get_alert(('New Poll'),
                                _("%(author)s shared a poll "
                                  "'%(title)s' with you.") %
                                {'author': author, 'title': title})

    def __vote_cb(self, author, title, choice, votersha, sender=None):
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

        self.activity.get_alert(_('New Poll'),
                                _("%(author)s shared a poll "
                                  "'%(title)s' with you.") %
                                {'author': author, 'title': title})

    @method(dbus_interface=IFACE, in_signature='s', out_signature='')
    def PollsWanted(self, sender):
        """
        Notification to send my polls to sender.
        """

        for poll in self.activity.get_my_polls():
            images_buf = {}

            for img_number, img_pixbuf in poll.images.iteritems():
                if not img_pixbuf == '':
                    images_buf[img_number] = poll.get_buffer(img_pixbuf)

                else:
                    images_buf[img_number] = img_pixbuf

            self.tube.get_object(sender, PATH).UpdatePoll(
                poll.title, poll.author, int(poll.active),
                poll.createdate.toordinal(),
                poll.maxvoters, poll.question, poll.number_of_options,
                poll.options, poll.data, poll.votes, images_buf,
                dbus_interface=IFACE)
