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

from gettext import gettext as _

from gi.repository import Gtk

from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbutton import ToolButton
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton

class Toolbar(ToolbarBox):

    def __init__(self, activity):

        ToolbarBox.__init__(self)

        toolbar_box = ToolbarBox()
        activity_button = ActivityToolbarButton(activity)
        self.toolbar.insert(activity_button, 0)
        activity_button.show()

        separator = Gtk.SeparatorToolItem()
        self.toolbar.insert(separator, -1)

        self.choose_button = ToolButton('view-list')
        self.choose_button.set_tooltip(_('Choose a Poll'))
        self.toolbar.insert(self.choose_button, -1)

        self.create_button = ToolButton('view-source')
        self.create_button.set_tooltip(_('Build a Poll'))
        self.toolbar.insert(self.create_button, -1)

        self.settings_button = ToolButton('preferences-system')
        self.settings_button.set_tooltip(_('Settings'))
        self.toolbar.insert(self.settings_button, -1)

        self.help_button = ToolButton('toolbar-help')
        self.help_button.set_tooltip(_('Lesson Plans'))
        self.toolbar.insert(self.help_button, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        self.toolbar.insert(separator, -1)
        separator.show()

        self.toolbar.insert(StopButton(activity), -1)

        self.show_all()

class NewPollCanvas(Gtk.Box):
    """
    widgets to set up a new poll or editing existing poll.
        editing is False to start a new poll.
        editing is True to edit the current poll.

    highlight is a list of strings denoting items failing validation.
    """

    def __init__(self, poll, editing=False, highlight=[]):

        # FIXME: El parámetro highlight nunca se utilizó, la idea era
        # resaltar el texto en las etiquetas para aquellas opciones no
        # validadas en la encuesta.
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)

        self._poll = poll

        self._poll.activity._current_view = 'build'

        label = Gtk.Label()
        label.set_markup('<big><b>%s</b></big>' % _('Build a poll'))
        self.pack_start(label, False, False, 10)

        item_poll = ItemNewPoll(_('poll Title:'), self._poll.title)
        item_poll.entry.connect('changed', self.__entry_activate_cb, 'title')
        self.pack_start(item_poll, False, False, 10)

        item_poll = ItemNewPoll(_('Question:'), self._poll.question)
        item_poll.entry.connect('changed', self.__entry_activate_cb, 'question')
        self.pack_start(item_poll, False, False, 10)

        item_poll = ItemNewPoll(_('Number of votes to collect:'), str(self._poll.maxvoters))
        item_poll.entry.connect('changed', self.__entry_activate_cb, 'maxvoters')
        self.pack_start(item_poll, False, False, 10)

        for choice in self._poll.options.keys():
            hbox = Gtk.HBox()
            item_poll = ItemNewPoll(_('Answer %d:'), self._poll.options[choice])
            item_poll.entry.connect('changed', self.__entry_activate_cb, str(choice))
            self.pack_start(item_poll, False, False, 10)

            if self._poll.activity._use_image:
                if self._poll.activity._already_loaded_image_in_answer(choice):
                    button = Gtk.Button(_("Change Image"))
                    hbox.pack_start(button, True, False, 10)
                    self._poll.activity._show_image_thumbnail(hbox, choice)

                else:
                    button = Gtk.Button(_("Add Image"))
                    hbox.pack_start(button, True, False, 10)

                button.connect('clicked', self._poll.activity._button_choose_image_cb,
                    str(choice), hbox)

        # PREVIEW & SAVE buttons
        hbox = Gtk.HBox()

        button = Gtk.Button(_("Step 1: Preview"))
        button.connect('clicked', self.__button_preview_cb)
        hbox.pack_start(button, True, True, 10)

        button = Gtk.Button(_("Step 2: Save"))
        button.connect('clicked', self.button_save_cb)
        hbox.pack_start(button, True, True, 10)

        self.pack_start(hbox, False, False, 10)

        self.show_all()

    def button_save_cb(self, button):
        """
        Save button clicked.
        """

        ### Validate data
        failed_items = self.__validate()

        if failed_items:
            print "*** failed_items:", failed_items
            # FIXME: El parámetro highlight nunca se utilizó, la idea era
            # resaltar el texto en las etiquetas para aquellas opciones no
            # validadas en la encuesta. (Modificar para que suceda al perder el foco el entry)
            #self.set_root(self._build_canvas(highlight=failed_items))
            #self.show_all()
            return

        # Data OK
        self._poll.activity._previewing = False
        self._poll.active = True
        self._poll.activity._polls.append(self._poll)
        #self._poll.broadcast_on_mesh() FIXME: Falta Activar
        self._poll.activity.set_canvas(self._poll.activity._poll_canvas())
        self._poll.activity.show_all()

    def __button_preview_cb(self, button):
        """
        Preview button clicked.
        """

        # Validate data
        failed_items = self.__validate()

        if failed_items:
            print "*** failed_items:", failed_items
            # FIXME: El parámetro highlight nunca se utilizó, la idea era
            # resaltar el texto en las etiquetas para aquellas opciones no
            # validadas en la encuesta. (Modificar para que suceda al perder el foco el entry)
            #self.set_root(self._build_canvas(highlight=failed_items))
            #self.show_all()
            return

        # Data OK
        self._poll.active = True  # Show radio buttons
        self._poll.activity._previewing = True
        self._poll.activity.set_canvas(self._poll.activity._poll_canvas())
        self._poll.activity.show_all()

    def __validate(self):

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

        return failed_items

    def __entry_activate_cb(self, entry, data):

        text = entry.get_text()

        if text:
            if data == 'title':
                self._poll.title = text

            elif data == 'question':
                self._poll.question = text

            elif data == 'maxvoters':
                try:
                    self._poll.maxvoters = int(text)

                except ValueError:
                    self._poll.maxvoters = 0 # invalid, will be trapped

            else:
                self._poll.options[int(data)] = text

class ItemNewPoll(Gtk.Box):

    def __init__(self, label_text, entry_text):

        Gtk.Box.__init__(self, orientation = Gtk.Orientation.HORIZONTAL)

        self.entry = Gtk.Entry()
        self.entry.set_text(entry_text)

        self.pack_start(Gtk.Label(label_text), False, False, 10)
        self.pack_start(self.entry, True, True, 10)

        self.show_all()
