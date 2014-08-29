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
import logging

from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import Gdk
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
from sugar3.graphics.radiotoolbutton import RadioToolButton
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics import style
from sugar3.graphics.icon import Icon

from graphics import Chart, CHART_TYPE_PIE

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

        self.create_button = ToolButton('new-poll')
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

        self.toolbar.insert(Gtk.SeparatorToolItem(), -1)

        self.pie_chart_button = RadioToolButton('pie-chart')
        self.pie_chart_button.set_tooltip(_('Pie chart'))
        self.toolbar.insert(self.pie_chart_button, -1)
        charts_group = self.pie_chart_button

        self.vbar_chart_button = RadioToolButton('vbar-chart')
        self.vbar_chart_button.set_tooltip(_('Vertical bar chart'))
        self.toolbar.insert(self.vbar_chart_button, -1)
        self.vbar_chart_button.props.group = charts_group

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

        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self._box)

        self._box.pack_start(HeaderBar(_('Build a poll')), False, False, 0)

        self._notebook = Gtk.Notebook()
        self._notebook.set_show_tabs(False)
        self._notebook.show()

        self._box.pack_start(self._notebook, True, True, 0)

        # first page

        self._first_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._notebook.append_page(self._first_page, None)
        self._first_page.show()

        item_poll = ItemNewPoll(_('What is the title?'), self._poll, 'title')
        self._first_page.pack_start(item_poll, False, False, 10)

        item_poll = ItemNewPoll(_('What is the question?'), self._poll,
                                'question')
        self._first_page.pack_start(item_poll, False, False, 10)

        item_poll = ItemNewPoll(_('How many votes you want collect?'),
                                self._poll, 'maxvoters')
        self._first_page.pack_start(item_poll, False, False, 10)

        # second page

        self._second_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._notebook.append_page(self._second_page, None)
        self._second_page.show()

        label = Gtk.Label()
        label.set_markup('<span size="x-large">%s</span>' %
                         _('What are the choices?'))
        label.set_halign(Gtk.Align.CENTER)
        label.props.margin = style.GRID_CELL_SIZE / 2
        self._second_page.pack_start(label, False, False, 0)

        self._image_widgets = []
        for choice in self._poll.options.keys():
            hbox = Gtk.HBox()
            item_poll = ItemOptionNewPoll(_('Answer %s:') % (choice + 1),
                                          self._poll, str(choice))
            self._second_page.pack_start(item_poll, False, False, 10)

            button = Gtk.Button()
            button.set_image(Icon(icon_name='insert-picture'))
            hbox.pack_start(button, True, False, 10)
            self._image_widgets.append(button)
            if self.__already_loaded_image_in_answer(choice):
                image = self.__show_image_thumbnail(hbox, choice)
                self._image_widgets.append(image)

            button.connect('clicked', self.__button_choose_image_cb,
                           int(choice), hbox)

            item_poll.pack_end(hbox, False, False, 0)

        # 3 page, summary
        third_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._notebook.append_page(third_page, None)

        label = Gtk.Label()
        label.set_markup('<span size="x-large">%s</span>' %
                         _('Is this correct?'))
        label.set_halign(Gtk.Align.CENTER)
        label.props.margin = style.GRID_CELL_SIZE
        third_page.pack_start(label, False, False, 0)

        columns_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        columns_box.set_homogeneous(True)
        first_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        second_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        columns_box.pack_start(first_column, False, False, 10)
        columns_box.pack_start(second_column, False, False, 10)

        label = Gtk.Label()
        label.set_markup('<b>%s</b>' % _('Title'))
        first_column.pack_start(label, False, True, 10)

        self._title_label = Gtk.Label()
        first_column.pack_start(self._title_label, False, False, 10)

        label = Gtk.Label()
        label.set_markup('<b>%s</b>' % _('Question'))
        first_column.pack_start(label, False, False, 10)

        self._question_label = Gtk.Label()
        first_column.pack_start(self._question_label, False, False, 10)

        label = Gtk.Label()
        label.set_markup('<b>%s</b>' % _('How many votes'))
        first_column.pack_start(label, False, False, 10)

        self._maxvoters_label = Gtk.Label()
        first_column.pack_start(self._maxvoters_label, False, False, 10)

        label = Gtk.Label()
        label.set_markup('<b>%s</b>' % _('Answers'))
        second_column.pack_start(label, False, False, 10)

        self._option_labels = {}
        for choice in self._poll.options.keys():
            label = Gtk.Label()
            self._option_labels[int(choice)] = label
            second_column.pack_start(label, False, False, 10)

        logging.error(self._option_labels)

        third_page.pack_start(columns_box, True, True, 10)

        save_button = Gtk.Button(_('Make the poll'))
        save_button.set_halign(Gtk.Align.CENTER)
        save_button.set_valign(Gtk.Align.START)
        save_button.props.margin = style.GRID_CELL_SIZE
        save_button.connect('clicked', self._button_save_cb)
        third_page.pack_start(save_button, False, False, 0)

        third_page.show_all()

        # buttons
        hbox = Gtk.ButtonBox()
        hbox.props.margin = style.GRID_CELL_SIZE

        self._back_button = Gtk.Button(_("Back"))
        self._back_button.set_image(Icon(icon_name='go-left'))
        self._back_button.connect('clicked', self.__button_back_cb)
        hbox.pack_start(self._back_button, True, True, 10)

        self._next_button = Gtk.Button(_("Next"))
        self._next_button.set_image(Icon(icon_name='go-right'))
        self._next_button.connect('clicked', self.__button_next_cb)
        hbox.pack_start(self._next_button, True, True, 10)

        self._box.pack_start(hbox, False, False, 10)

        self.show_all()
        self.set_image_widgets_visible(self._poll.activity.get_use_image())

    def __button_back_cb(self, button):
        self._notebook.prev_page()

    def __button_next_cb(self, button):
        logging.error('current page %s', self._notebook.get_current_page())
        if self._notebook.get_current_page() < 2:
            errors = self._validate(self._notebook.get_current_page())
            if not errors:
                self._notebook.next_page()
        if self._notebook.get_current_page() == 2:
            self._title_label.set_text(self._poll.title)
            self._question_label.set_text(self._poll.question)
            self._maxvoters_label.set_text(str(self._poll.maxvoters))
            logging.error(self._poll.options.keys())
            for choice in self._poll.options.keys():
                self._option_labels[int(choice)].set_text(
                    self._poll.options[int(choice)])
            self._notebook.next_page()

    def set_image_widgets_visible(self, visible):
        for widget in self._image_widgets:
            widget.set_visible(visible)

    def __already_loaded_image_in_answer(self, answer_number):

        if not self._poll.images_ds_objects[int(answer_number)] == {}:
            return True

        else:
            return False

    def __button_choose_image_cb(self, button, choice, hbox):
        """
        choice: int
        hbox: the container where the image will be displayed
        """

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

                    self._poll.images[choice] = pixbuf

                    self._poll.images_ds_objects[choice]['id'] = \
                        jobject.object_id

                    self._poll.images_ds_objects[choice]['file_path'] = \
                        jobject.file_path

                    self.__show_image_thumbnail(hbox, choice)

                else:
                    self._poll.activity.get_alert(
                        _('Poll Activity'),
                        _('Your selection is not an image'))

        finally:
            chooser.destroy()
            del chooser

    def __show_image_thumbnail(self, parent_box, answer_number):

        image_file_path = self._poll.images_ds_objects[answer_number][
            'file_path']

        pixbuf_thumbnail = GdkPixbuf.Pixbuf.new_from_file_at_size(
            image_file_path, 80, 80)

        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf_thumbnail)
        image.show()
        self._image_widgets.append(image)

        chl = parent_box.get_children()

        if len(chl) == 2:
            parent_box.remove(chl[len(chl) - 1])

        parent_box.pack_start(image, True, True, 10)
        return pixbuf_thumbnail

    def _button_save_cb(self, button):
        """
        Save button clicked.
        """
        # Data OK
        self._poll.active = True
        self._poll.activity._polls.add(self._poll)
        self._poll.broadcast_on_mesh()
        self._poll.activity.set_canvas(self._poll.activity._poll_canvas())
        self._poll.activity.show_all()

    def _validate(self, page):

        failed_items = []

        if page == 0:
            box = self._first_page
            if self._poll.title == '':
                failed_items.append('title')

            if self._poll.question == '':
                failed_items.append('question')

            if self._poll.maxvoters == 0:
                failed_items.append('maxvoters')
        if page == 1:
            box = self._second_page
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

        for child in box:
            if (type(child) is ItemNewPoll or
                type(child) is ItemOptionNewPoll) \
                    and child.field in failed_items:
                child.entry.modify_bg(Gtk.StateType.NORMAL,
                                      style.Color('#FFFF00').get_gdk_color())

        return failed_items


class ItemNewPoll(Gtk.Box):

    def __init__(self, label_text, poll, field):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self._poll = poll
        self.field = field

        label = Gtk.Label()
        label.set_markup('<span size="x-large">%s</span>' % label_text)
        label.set_halign(Gtk.Align.CENTER)
        label.props.margin = style.GRID_CELL_SIZE / 2
        self.pack_start(label, False, False, 0)

        self.entry = Gtk.Entry()
        margin = style.GRID_CELL_SIZE

        if field == 'maxvoters':
            self.entry.props.xalign = 1
            margin = Gdk.Screen.width() / 2 - (style.GRID_CELL_SIZE * 2)

        self.entry.props.margin_left = margin
        self.entry.props.margin_right = margin

        self.entry.set_text(str(getattr(poll, field)))

        self.entry.connect('changed', self.__entry_changed_cb)

        self.pack_start(self.entry, False, False, 0)

        self.show_all()

    def __entry_changed_cb(self, entry):
        logging.error(entry.get_text())
        text = entry.get_text()
        if text:
            if self.field == 'title':
                self._poll.title = text
            elif self.field == 'question':
                self._poll.question = text
            elif self.field == 'maxvoters':
                self._poll.maxvoters = int(text)
        entry.modify_bg(Gtk.StateType.NORMAL, None)


class ItemOptionNewPoll(Gtk.Box):

    def __init__(self, label_text, poll, field):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self._poll = poll
        self.field = field
        self.set_border_width(style.GRID_CELL_SIZE / 2)

        label = Gtk.Label()
        label.set_markup('<span size="x-large">%s</span>' % label_text)
        label.set_halign(Gtk.Align.CENTER)
        self.pack_start(label, False, False, 10)

        self.entry = Gtk.Entry()
        self.entry.set_text(poll.options[int(field)])
        self.entry.connect('changed', self.__entry_changed_cb)
        self.pack_start(self.entry, True, True, 0)

        self.show_all()

    def __entry_changed_cb(self, entry):
        logging.error(entry.get_text())
        text = entry.get_text()
        if text:
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
            self._poll_activity.get_view_answer())
        self._remember_vote_checkbutton.set_active(
            self._poll_activity._remember_last_vote)
        self._play_vote_sound_checkbutton.set_active(
            self._poll_activity._play_vote_sound)
        self._use_image_checkbox.set_active(
            self._poll_activity.get_use_image())
        self._image_height_entry.set_sensitive(
            self._poll_activity.get_use_image())
        self._image_width_entry.set_sensitive(
            self._poll_activity.get_use_image())

    def __view_result_checkbox_cb(self, checkbox):
        self._poll_activity.set_view_answer(checkbox.get_active())

    def __remember_last_vote_checkbox_cb(self, checkbox):
        self._poll_activity._remember_last_vote = checkbox.get_active()

    def __play_vote_sound_checkbox_cb(self, checkbox):
        self._poll_activity._play_vote_sound = checkbox.get_active()

    def __entry_image_size_cb(self, entrycontrol, data):
        text = entrycontrol.get_text()
        if text:
            self._poll_activity._image_size[data] = int(text)

    def __use_image_checkbox_cb(self, checkbox):
        self._poll_activity.set_use_image(checkbox.get_active())
        self._image_height_entry.set_sensitive(checkbox.get_active())
        self._image_width_entry.set_sensitive(checkbox.get_active())


class SelectCanvas(Gtk.Box):

    def __init__(self, poll_activity):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.pack_start(HeaderBar(_('Choose a Poll')), False, False, 0)

        poll_selector_box = Gtk.VBox()
        poll_selector_box.props.margin = style.GRID_CELL_SIZE

        scroll = Gtk.ScrolledWindow()
        scroll.modify_bg(Gtk.StateType.NORMAL,
                         style.COLOR_WHITE.get_gdk_color())

        scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.NEVER)

        scroll.add_with_viewport(poll_selector_box)

        self.pack_start(scroll, True, True, 0)

        size_group = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)

        for poll in poll_activity._polls:
            sha = poll.sha

            poll_row = Gtk.HBox()
            poll_row.props.margin = 10
            poll_selector_box.pack_start(poll_row, False, False, 0)
            poll_selector_box.pack_start(Gtk.HSeparator(), False, False, 0)

            title = Gtk.Label()
            title.set_markup('<span size="large">%s (%s)</span>' %
                             (poll.title, poll.author))
            align = Gtk.Alignment.new(0, 0.5, 0, 0)
            align.add(title)
            poll_row.pack_start(align, True, True, 10)

            if poll.active:
                button = Gtk.Button(_('Vote'))
                button.set_image(Icon(icon_name='dialog-ok'))
            else:
                button = Gtk.Button(_('See Results'))
                button.set_image(Icon(icon_name='toolbar-view'))
            size_group.add_widget(button)

            button.connect('clicked', poll_activity._select_poll_button_cb,
                           sha)
            poll_row.pack_start(button, False, False, 10)

            if poll.author == profile.get_nick_name():
                button = Gtk.Button(_('Delete'))
                button.set_image(Icon(icon_name='basket'))
                button.connect('clicked',
                               poll_activity._delete_poll_button_cb, sha)
                poll_row.pack_start(button, False, False, 10)

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

    def __init__(self, poll, current_vote, view_answer):

        Gtk.EventBox.__init__(self)
        self.modify_bg(Gtk.StateType.NORMAL,
                       style.COLOR_WHITE.get_gdk_color())

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)

        self._poll = poll

        header = _('VOTE!')
        if self._poll.active:
            header = _('VOTE')
        else:
            header = _('RESULTS')

        box.pack_start(HeaderBar(_(header)), False, False, 0)

        self._grid = Gtk.Grid()
        box.pack_start(self._grid, True, True, 0)

        self.title = Gtk.Label()
        self.title.set_markup('<span size="large">%s</span>' % poll.title)
        self.title.props.margin = style.GRID_CELL_SIZE / 2
        self.title.set_halign(Gtk.Align.START)
        self._grid.attach(self.title, 0, 0, 1, 1)

        self.question = Gtk.Label()
        self.question.set_markup('<span size="large"><b>%s</b></span>' %
                                 poll.question)
        self.question.props.margin = style.GRID_CELL_SIZE / 2
        self.question.set_halign(Gtk.Align.CENTER)
        self._grid.attach(self.question, 0, 1, 2, 1)

        counter_label = Gtk.Label()
        counter_label.set_markup(
            '<span size="x-large">%s from %s votes collected</span>' %
            (poll.vote_count, poll.maxvoters))
        counter_label.props.margin = style.GRID_CELL_SIZE / 2
        counter_label.set_halign(Gtk.Align.END)
        self._grid.attach(counter_label, 1, 0, 1, 1)

        tabla = Gtk.Table(rows=6, columns=6)
        tabla.set_border_width(style.GRID_CELL_SIZE)

        scroll = Gtk.ScrolledWindow()

        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        scroll.add_with_viewport(tabla)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)

        group = Gtk.RadioButton()

        row = 0
        self._results_widgets = []
        data = {}
        for choice in range(poll.number_of_options):
            # data is used by the chart
            data[poll.options[choice]] = poll.data[choice]

            if poll.active:
                button = Gtk.RadioButton.new_with_label_from_widget(
                    group, poll.options[choice])

                button.connect(
                    'toggled', poll.activity.vote_choice_radio_button, choice)

                tabla.attach(button, 0, 1, row, row + 1)

                if choice == current_vote:
                    button.set_active(True)

                if poll.images[int(choice)]:
                    image = Gtk.Image()
                    image.set_from_pixbuf(poll.images[choice])
                    image.set_halign(Gtk.Align.START)
                    tabla.attach(image, 1, 2, row, row + 1)

            row += 1

        logging.error('poll options %s data %s', poll.options, poll.data)

        self.chart = Chart(data, CHART_TYPE_PIE)
        self.chart.set_hexpand(True)
        self.chart.set_vexpand(True)

        # TODO: just showing/hiding one widget now
        self._results_widgets.append(self.chart)

        # Button area
        if poll.active:
            self._grid.attach(scroll, 0, 2, 1, 1)
            self._grid.attach(self.chart, 1, 2, 1, 1)

            button = Gtk.Button(_("Vote"))
            button.set_image(Icon(icon_name='dialog-ok',
                                  pixel_size=style.MEDIUM_ICON_SIZE))
            theme = 'GtkButton {background-color: %s;' \
                'font-size:%s;' \
                'padding: 5px 35px 5px 35px;}' % \
                ('#ff0000', style.FONT_SIZE * 2)
            css_provider = Gtk.CssProvider()
            css_provider.load_from_data(theme)
            style_context = button.get_style_context()
            style_context.add_provider(css_provider,
                                       Gtk.STYLE_PROVIDER_PRIORITY_USER)

            button.connect('clicked', poll.activity.button_vote_cb)
            button.props.margin = style.GRID_CELL_SIZE / 2
            button.set_hexpand(False)
            button.set_halign(Gtk.Align.END)

            self._grid.attach(button, 1, 3, 1, 1)
        else:
            logging.error('poll not active')
            self._grid.attach(self.chart, 0, 2, 1, 1)

        self.show_all()
        # hide or show the results if needed
        self.set_view_answer(view_answer or not poll.active)

    def set_view_answer(self, visible):
        for widget in self._results_widgets:
            widget.set_visible(visible)

    def _button_save_cb(self, button):
        """
        Save button clicked.
        """
        # Data OK
        self._poll.active = True
        self._poll.activity._polls.add(self._poll)
        self._poll.broadcast_on_mesh()
        self._poll.activity.set_canvas(self._poll.activity._poll_canvas())
        self._poll.activity.show_all()
