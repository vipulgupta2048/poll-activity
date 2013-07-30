#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Widgets.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   CeibalJAM! - Uruguay

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

#import os
from gettext import gettext as _

from gi.repository import Gtk

class NewPollCanvas(Gtk.Box):

    def __init__(self, poll, editing=False, highlight=[]):

        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)

        """
        Show the canvas to set up a new poll.

        editing is False to start a new poll, or
        True to edit the current poll

        highlight is a list of strings denoting items failing validation.
        """

        #self._current_view = 'build'

        label = Gtk.Label()
        label.set_markup('<big><b>%s</b></big>' % _('Build a Poll'))
        self.pack_start(label, False, False, 10)

        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label(_('Poll Title:')), False, False, 10)
        entrybox = Gtk.Entry()
        entrybox.set_text(poll.title)
        #entrybox.connect('changed', self._entry_activate_cb, 'title')
        hbox.pack_start(entrybox, True, True, 10)
        self.pack_start(hbox, False, False, 10)

        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label(_('Question:')), False, False, 10)
        entrybox = Gtk.Entry()
        entrybox.set_text(poll.question)
        #entrybox.connect('changed', self._entry_activate_cb, 'question')
        hbox.pack_start(entrybox, True, True, 10)
        self.pack_start(hbox, False, False, 10)

        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label(_('Number of votes to collect:')),
            False, False, 10)
        entrybox = Gtk.Entry()
        entrybox.set_text(str(poll.maxvoters))
        #entrybox.connect('changed', self._entry_activate_cb, 'maxvoters')
        hbox.pack_start(entrybox, True, True, 10)
        self.pack_start(hbox, False, False, 10)

        for choice in poll.options.keys():
            hbox = Gtk.HBox()
            hbox.pack_start(Gtk.Label(_('Answer %d:') % (choice + 1)),
                False, False, 10)
            entrybox = Gtk.Entry()
            entrybox.set_text(poll.options[choice])
            #entrybox.connect('changed', self._entry_activate_cb, str(choice))
            hbox.pack_start(entrybox, True, True, 10)
            '''
            if self._use_image:
                if self._already_loaded_image_in_answer(choice):
                    button = Gtk.Button(_("Change Image"))
                    hbox.pack_start(button, True, False, 10)
                    self._show_image_thumbnail(hbox, choice)

                else:
                    button = Gtk.Button(_("Add Image"))
                    hbox.pack_start(button, True, False, 10)

                button.connect('clicked', self._button_choose_image_cb,
                    str(choice), hbox)'''

            self.pack_start(hbox, False, False, 10)

        # PREVIEW & SAVE buttons
        hbox = Gtk.HBox()
        button = Gtk.Button(_("Step 1: Preview"))
        #button.connect('clicked', self._button_preview_cb)
        hbox.pack_start(button, True, True, 10)
        button = Gtk.Button(_("Step 2: Save"))
        #button.connect('clicked', self._button_save_cb)
        hbox.pack_start(button, True, True, 10)

        self.pack_start(hbox, False, False, 10)

        self.show_all()
