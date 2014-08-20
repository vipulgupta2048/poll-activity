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

import os

from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import GdkPixbuf

from sugar3 import mime
from sugar3 import profile
from sugar3.graphics.objectchooser import ObjectChooser
try:
    from sugar3.graphics.objectchooser import FILTER_TYPE_GENERIC_MIME
except:
    FILTER_TYPE_GENERIC_MIME = 'generic_mime'

from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbutton import ToolButton
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics import style

import colors

basepath = os.path.dirname(__file__)


class Toolbar(ToolbarBox):

    def __init__(self, activity):

        ToolbarBox.__init__(self)

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
        self.settings_button.palette_invoker.props.toggle_palette = True
        self.settings_button.palette_invoker.props.lock_palette = True
        self.settings_button.props.hide_tooltip_on_click = False

        palette = self.settings_button.get_palette()
        hbox = Gtk.HBox()
        self._options_palette = OptionsPalette(activity)
        hbox.pack_start(self._options_palette, True, True,
                        style.DEFAULT_SPACING)
        hbox.show_all()
        palette.set_content(hbox)
        self.toolbar.insert(self.settings_button, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        self.toolbar.insert(separator, -1)
        separator.show()

        self.toolbar.insert(StopButton(activity), -1)

        self.show_all()

    def update_configs(self):
        self._options_palette.update_configs()


class NewPollCanvas(Gtk.EventBox):
    """
    widgets to set up a new poll or editing existing poll.
        editing is False to start a new poll.
        editing is True to edit the current poll.
    """

    def __init__(self, poll, editing=False):

        Gtk.EventBox.__init__(self)
        self.modify_bg(Gtk.StateType.NORMAL, style.COLOR_WHITE.get_gdk_color())

        self._poll = poll

        self._poll.activity._current_view = 'build'

        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self._box)

        self._box.pack_start(HeaderBar(_('Build a poll')), False, False, 0)

        item_poll = ItemNewPoll(_('Poll Title:'), self._poll, 'title')
        self._box.pack_start(item_poll, False, False, 10)

        item_poll = ItemNewPoll(_('Question:'), self._poll, 'question')
        self._box.pack_start(item_poll, False, False, 10)

        item_poll = ItemNewPoll(_('Number of votes to collect:'),
                                self._poll, 'maxvoters')
        self._box.pack_start(item_poll, False, False, 10)

        for choice in self._poll.options.keys():
            hbox = Gtk.HBox()
            item_poll = ItemNewPoll(_('Answer %s:') % (choice + 1),
                                    self._poll, str(choice))
            self._box.pack_start(item_poll, False, False, 10)

            if self._poll.activity._use_image:
                if self.__already_loaded_image_in_answer(choice):
                    button = Gtk.Button(_("Change Image"))
                    hbox.pack_start(button, True, False, 10)
                    self.__show_image_thumbnail(hbox, choice)

                else:
                    button = Gtk.Button(_("Add Image"))
                    hbox.pack_start(button, True, False, 10)

                button.connect('clicked', self.__button_choose_image_cb,
                               str(choice), hbox)

            item_poll.pack_end(hbox, False, False, 0)

        # PREVIEW & SAVE buttons
        hbox = Gtk.HBox()

        button = Gtk.Button(_("Step 1: Preview"))
        button.connect('clicked', self.__button_preview_cb)
        hbox.pack_start(button, True, True, 10)

        button = Gtk.Button(_("Step 2: Save"))
        button.connect('clicked', self._button_save_cb)
        hbox.pack_start(button, True, True, 10)

        self._box.pack_start(hbox, False, False, 10)

        self.show_all()

    def __already_loaded_image_in_answer(self, answer_number):

        if not self._poll.images_ds_objects[int(answer_number)] == {}:
            return True

        else:
            return False

    def __button_choose_image_cb(self, button, data=None, data2=None):

        try:
            chooser = ObjectChooser(self, what_filter='Image',
                                    filter_type=FILTER_TYPE_GENERIC_MIME,
                                    show_preview=True)
        except:
            # for compatibility with older versions
            chooser = ObjectChooser(self, what_filter='Image')

        try:
            result = chooser.run()

            if result == Gtk.ResponseType.ACCEPT:

                jobject = chooser.get_selected_object()

                images_mime_types = mime.get_generic_type(
                    mime.GENERIC_TYPE_IMAGE).mime_types

                if jobject and jobject.file_path and \
                   jobject.metadata.get('mime_type') in images_mime_types:

                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                        jobject.file_path,
                        self._poll.activity._image_size['height'],
                        self._poll.activity._image_size['width'])

                    self._poll.images[int(data)] = pixbuf

                    self._poll.images_ds_objects[int(data)]['id'] = \
                        jobject.object_id

                    self._poll.images_ds_objects[int(data)]['file_path'] = \
                        jobject.file_path

                    self.__show_image_thumbnail(data2, data)
                    button.set_label(_('Change Image'))

                else:
                    self._poll.activity.get_alert(
                        _('Poll Activity'),
                        _('Your selection is not an image'))

        finally:
            chooser.destroy()
            del chooser

    def __show_image_thumbnail(self, parent_box, answer_number):

        hbox = Gtk.HBox()

        image_file_path = self._poll.images_ds_objects[int(answer_number)][
            'file_path']

        pixbuf_thumbnail = GdkPixbuf.Pixbuf.new_from_file_at_size(
            image_file_path, 80, 80)

        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf_thumbnail)
        image.show()
        hbox.add(image)
        hbox.show()

        chl = parent_box.get_children()

        if len(chl) == 4:
            parent_box.remove(chl[len(chl) - 1])

        parent_box.pack_start(hbox, True, True, 0)

    def _button_save_cb(self, button):
        """
        Save button clicked.
        """
        # Validate data
        if self.__validate():
            return

        # Data OK
        self._poll.activity._previewing = False
        self._poll.active = True
        self._poll.activity._polls.add(self._poll)
        self._poll.broadcast_on_mesh()
        self._poll.activity.set_canvas(self._poll.activity._poll_canvas())
        self._poll.activity.show_all()

    def __button_preview_cb(self, button):
        """
        Preview button clicked.
        """
        # Validate data
        if self.__validate():
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

        # paint the obligatory entries without value
        for child in self._box.get_children():
            if type(child) is ItemNewPoll and child.field in failed_items:
                child.entry.modify_bg(Gtk.StateType.NORMAL,
                                      style.Color('#FFFF00').get_gdk_color())

        return failed_items


class ItemNewPoll(Gtk.Box):

    def __init__(self, label_text, poll, field):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self._poll = poll
        self.field = field
        self.entry = Gtk.Entry()
        if field in ('title', 'question', 'maxvoters'):
            self.entry.set_text(str(getattr(poll, field)))
        else:
            self.entry.set_text(poll.options[int(field)])

        self.entry.connect('changed', self.__entry_changed_cb)

        self.pack_start(Gtk.Label(label_text), False, False, 10)
        self.pack_start(self.entry, True, True, 10)

        self.show_all()

    def __entry_changed_cb(self, entry):

        text = entry.get_text()
        if text:
            if self.field == 'title':
                self._poll.title = text
            elif self.field == 'question':
                self._poll.question = text
            elif self.field == 'maxvoters':
                try:
                    self._poll.maxvoters = int(text)
                except ValueError:
                    self._poll.maxvoters = 0  # invalid, will be trapped
            else:
                self._poll.options[int(self.field)] = text
        entry.modify_bg(Gtk.StateType.NORMAL, None)


class OptionsPalette(Gtk.Box):
    """
    Show the options palette.
    """

    def __init__(self, poll_activity):
        self._poll_activity = poll_activity
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self._view_results_checkbutton = Gtk.CheckButton(
            label=_('Show answers while voting'))
        self._view_results_checkbutton.connect(
            'toggled', self.__view_result_checkbox_cb)
        self.pack_start(self._view_results_checkbutton, True, True, 10)

        self._remember_vote_checkbutton = Gtk.CheckButton(
            label=_('Remember last vote'))
        self._remember_vote_checkbutton.connect(
            'toggled', self.__remember_last_vote_checkbox_cb)
        self.pack_start(self._remember_vote_checkbutton, True, True, 10)

        self._play_vote_sound_checkbutton = Gtk.CheckButton(
            label=_('Play a sound when make a vote'))
        self._play_vote_sound_checkbutton.connect(
            'toggled', self.__play_vote_sound_checkbox_cb)
        self.pack_start(self._play_vote_sound_checkbutton, True, True, 10)

        vbox = Gtk.VBox()
        self._use_image_checkbox = Gtk.CheckButton(
            label=_('Use image in answer'))
        self.pack_start(self._use_image_checkbox, True, True, 10)
        self._use_image_checkbox.connect('toggled',
                                         self.__use_image_checkbox_cb)

        hbox2 = Gtk.HBox()
        hbox2.pack_start(Gtk.Label(_('Image Size: ')), True, True, 10)

        self._image_width_entry = Gtk.Entry(max_length=3)
        self._image_width_entry.set_size_request(style.GRID_CELL_SIZE, -1)
        self._image_width_entry.set_text(
            str(self._poll_activity._image_size['width']))
        self._image_width_entry.connect(
            'changed', self.__entry_image_size_cb, 'width')
        hbox2.pack_start(self._image_width_entry, True, True, 10)

        hbox2.pack_start(Gtk.Label('x'), True, True, 10)

        self._image_height_entry = Gtk.Entry(max_length=3)
        self._image_height_entry.set_text(
            str(self._poll_activity._image_size['height']))
        self._image_height_entry.connect(
            'changed', self.__entry_image_size_cb, 'height')
        hbox2.pack_start(self._image_height_entry, True, True, 10)
        vbox.pack_start(hbox2, True, True, 10)
        self.pack_start(vbox, True, True, 0)

        self.show_all()

    def update_configs(self):
        self._view_results_checkbutton.set_active(
            self._poll_activity._view_answer)
        self._remember_vote_checkbutton.set_active(
            self._poll_activity._remember_last_vote)
        self._play_vote_sound_checkbutton.set_active(
            self._poll_activity._play_vote_sound)
        self._use_image_checkbox.set_active(self._poll_activity._use_image)
        self._image_height_entry.set_sensitive(self._poll_activity._use_image)
        self._image_width_entry.set_sensitive(self._poll_activity._use_image)

    def __view_result_checkbox_cb(self, checkbox):
        self._poll_activity._view_answer = checkbox.get_active()

    def __remember_last_vote_checkbox_cb(self, checkbox):
        self._poll_activity._remember_last_vote = checkbox.get_active()

    def __play_vote_sound_checkbox_cb(self, checkbox):
        self._poll_activity._play_vote_sound = checkbox.get_active()

    def __entry_image_size_cb(self, entrycontrol, data):
        text = entrycontrol.get_text()
        if text:
            self._poll_activity._image_size[data] = int(text)

    def __use_image_checkbox_cb(self, checkbox):
        self._poll_activity._use_image = checkbox.get_active()
        self._image_height_entry.set_sensitive(checkbox.get_active())
        self._image_width_entry.set_sensitive(checkbox.get_active())


class SelectCanvas(Gtk.Box):

    def __init__(self, poll_activity):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        poll_activity._current_view = 'select'

        self.pack_start(HeaderBar(_('Choose a Poll')), False, False, 0)

        poll_selector_box = Gtk.VBox()

        scroll = Gtk.ScrolledWindow()
        scroll.modify_bg(Gtk.StateType.NORMAL,
                         style.COLOR_WHITE.get_gdk_color())

        scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.NEVER)

        scroll.add_with_viewport(poll_selector_box)

        self.pack_start(scroll, True, True, 0)

        row_number = 0

        for poll in poll_activity._polls:
            sha = poll.sha

            if row_number % 2:
                row_bgcolor = style.COLOR_WHITE.get_gdk_color()
            else:
                row_bgcolor = style.COLOR_HIGHLIGHT.get_gdk_color()
            row_number += 1

            evbox = Gtk.EventBox()
            evbox.modify_bg(Gtk.StateType.NORMAL, row_bgcolor)

            poll_row = Gtk.HBox()
            evbox.add(poll_row)
            poll_row.props.margin = 10
            poll_selector_box.pack_start(evbox, False, False, 0)

            title = Gtk.Label()
            title.set_markup('<span size="large">%s (%s)</span>' %
                             (poll.title, poll.author))
            align = Gtk.Alignment.new(0, 0.5, 0, 0)
            align.add(title)
            poll_row.pack_start(align, True, True, 10)

            if poll.active:
                button = Gtk.Button(_('VOTE'))

            else:
                button = Gtk.Button(_('SEE RESULTS'))

            button.connect('clicked', poll_activity._select_poll_button_cb,
                           sha)
            poll_row.pack_start(button, False, False, 10)

            if poll.author == profile.get_nick_name():
                button = Gtk.Button(_('DELETE'))
                button.connect('clicked',
                               poll_activity._delete_poll_button_cb, sha)
                poll_row.pack_start(button, False, False, 10)

            poll_row.pack_start(Gtk.Label(
                poll.createdate.strftime('%d/%m/%y')), False, False, 10)

        self.show_all()


class HeaderBar(Gtk.EventBox):

    def __init__(self, title=None):

        Gtk.EventBox.__init__(self)
        self.modify_bg(Gtk.StateType.NORMAL,
                       style.Color('#666666').get_gdk_color())
        self.set_size_request(-1, style.GRID_CELL_SIZE)
        self.box = Gtk.HBox()
        self.add(self.box)

        if title is not None:
            self.title_label = Gtk.Label()
            self.title_label.set_markup(
                '<span size="x-large" foreground="white">%s</span>' % title)
            self.box.pack_start(self.title_label, False, False, 10)


class PollCanvas(Gtk.EventBox):

    def __init__(self, poll, current_vote, view_answer, previewing):

        Gtk.EventBox.__init__(self)
        self.modify_bg(Gtk.StateType.NORMAL,
                       style.COLOR_WHITE.get_gdk_color())

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)

        self._poll = poll

        if not previewing:
            header = _('VOTE!')
            if self._poll.active:
                header = _('VOTE')
            else:
                header = _('RESULTS')
        else:
            header = _('Poll Preview')

        box.pack_start(HeaderBar(_(header)), False, False, 0)

        self.title = Gtk.Label()
        self.title.set_markup('<span size="large">%s</span>' % poll.title)
        self.title.set_alignment(0.01, 0.5)
        box.pack_start(self.title, False, False, 10)

        self.question = Gtk.Label(poll.question)
        self.question.set_markup('<span size="large"><b>%s</b></span>' %
                                 poll.question)
        self.question.set_alignment(0.01, 0.5)
        box.pack_start(self.question, False, False, 10)

        frame = Gtk.AspectFrame()
        tabla = Gtk.Table(rows=6, columns=6)
        tabla.set_border_width(20)

        frame.add(tabla)

        scroll = Gtk.ScrolledWindow()

        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        scroll.add_with_viewport(frame)

        box.pack_start(scroll, True, True, 10)

        group = Gtk.RadioButton()

        row = 0
        for choice in range(poll.number_of_options):

            button = Gtk.RadioButton.new_with_label_from_widget(
                group, poll.options[choice])

            button.connect('toggled', poll.activity.vote_choice_radio_button,
                           choice)

            if poll.active:
                button.set_sensitive(True)
            else:
                button.set_sensitive(False)

            tabla.attach(button, 0, 1, row, row+1)

            if choice == current_vote:
                button.set_active(True)

            if not poll.images[int(choice)] == '':
                image = Gtk.Image()
                image.set_from_pixbuf(poll.images[choice])
                tabla.attach(image, 1, 2, row, row + 1)

            if view_answer or not poll.active:
                if poll.vote_count > 0:

                    # Total de votos
                    label = Gtk.Label(poll.data[choice])
                    label.set_size_request(100, -1)
                    tabla.attach(label, 3, 4, row, row + 1)

                    eventbox = Gtk.EventBox()
                    eventbox.set_size_request(300, -1)
                    tabla.attach(eventbox, 4, 5, row, row + 1)

                    color = colors.get_category_color(poll.options[choice])

                    eventbox.connect("draw",
                                     self.__draw_bar, poll.data[choice],
                                     poll.vote_count, color)

            row += 1

        if view_answer or not poll.active:
            if poll.vote_count > 0:
                # Barra para total
                separator = Gtk.HSeparator()
                tabla.attach(separator, 3, 5, row, row + 1)

        row += 1

        if view_answer or not poll.active:
            if poll.vote_count > 0:
                label = Gtk.Label("%s %s %s %s" % (str(poll.vote_count),
                                  _('votes'), _('(votes left to collect)'),
                                  poll.maxvoters - poll.vote_count))
                tabla.attach(label, 3, 5, row, row + 1)

        row += 1

        # Button area
        if poll.active and not previewing:
            button = Gtk.Button(_("Vote"))
            button.connect('clicked', poll.activity.button_vote_cb)
            button.props.margin = 10
            tabla.attach(button, 0, 1, row, row + 1)

        elif previewing:
            button = Gtk.Button(_("Edit Poll"))
            button.connect('clicked', poll.activity.button_edit_clicked)
            button.props.margin = 10
            tabla.attach(button, 0, 1, row, row + 1)

            button = Gtk.Button(_("Save Poll"))
            button.connect('clicked', self._button_save_cb)
            button.props.margin = 10
            tabla.attach(button, 1, 2, row, row + 1)

        self.show_all()

    def _button_save_cb(self, button):
        """
        Save button clicked.
        """
        # Data OK
        self._poll.activity._previewing = False
        self._poll.active = True
        self._poll.activity._polls.add(self._poll)
        self._poll.broadcast_on_mesh()
        self._poll.activity.set_canvas(self._poll.activity._poll_canvas())
        self._poll.activity.show_all()

    def __draw_bar(self, widget, context, votos, total, color):
        """
        Graphic the percent of votes from one option.
        """

        rect = widget.get_allocation()
        w, h = (rect.width, rect.height)
        percent = votos * 100 / total
        width = w * percent / 100

        context.rectangle(0, h / 2 - 10, width, 30)
        context.set_source_rgb(color[0], color[1], color[2])
        context.fill()

        return True
