import logging
import cairo
import math
from gettext import gettext as _
import StringIO

from gi.repository import Gtk
from gi.repository import PangoCairo
from gi.repository import Pango

from sugar3.graphics import style
from sugar3.activity import activity

import colors


def _get_screen_dpi():
    xft_dpi = Gtk.Settings.get_default().get_property('gtk-xft-dpi')
    dpi = float(xft_dpi / 1024)
    logging.error('Setting dpi to: %f', dpi)
    return dpi


def _set_screen_dpi():
    dpi = _get_screen_dpi()
    font_map_default = PangoCairo.font_map_get_default()
    font_map_default.set_resolution(dpi)


def draw_round_rect(context, x, y, w, h, r):
    # Copiado de http://www.steveanddebs.org/PyCairoDemo/
    # "Draw a rounded rectangle"

    context.move_to(x + r, y)
    context.line_to(x + w - r, y)
    context.curve_to(x + w, y, x + w, y, x + w, y + r)
    context.line_to(x + w, y + h - r)
    context.curve_to(x + w, y + h, x + w, y + h, x + w - r, y + h)
    context.line_to(x + r, y + h)
    context.curve_to(x, y + h, x, y + h, x, y + h - r)
    context.line_to(x, y + r)
    context.curve_to(x, y, x, y, x + r, y)
    return


def top_rounded_rect(context, x, y, w, h, r):
    # Copiado de http://www.steveanddebs.org/PyCairoDemo/
    # "Draw a rounded rectangle"

    context.move_to(x + r, y)
    context.line_to(x + w - r, y)
    context.curve_to(x + w, y, x + w, y, x + w, y + r)
    context.line_to(x + w, y + h)
    context.line_to(x, y + h)
    context.line_to(x, y + r)
    context.curve_to(x, y, x, y, x + r, y)
    return


CHART_TYPE_PIE = 1
CHART_TYPE_VERTICAL_BARS = 2


class Chart(Gtk.DrawingArea):

    def __init__(self, data, chart_type, show_labels=True, title=None,
                 title_color=None):
        """
            data: array
                every item in the array is a dict with keys 'label', 'value',
                and color (color is a str with format "#rrggbb")
            chart_type: CHART_TYPE_PIE or CHART_TYPE_VERTICAL_BARS
            show_labels: bool
            title: str
            title_color: str with format "#rrggbb"
        """
        Gtk.DrawingArea.__init__(self)
        self._data = data
        self._chart_type = chart_type
        self._show_labels = show_labels
        self._title = title
        self._title_color = title_color
        self.connect('draw', self.__chart_draw_cb)

    def set_data(self, data):
        self._data = data
        self.queue_draw()

    def set_chart_type(self, chart_type):
        self._chart_type = chart_type
        self.queue_draw()

    def set_show_labels(self, show_labels):
        self._show_labels = show_labels
        self.queue_draw()

    def set_title(self, title):
        self._title = title
        self.queue_draw()

    def set_title_color(self, title_color):
        self._title_color = title_color
        self.queue_draw()

    def __chart_draw_cb(self, widget, context):
        # Draw pie chart.
        bounds = widget.get_allocation()
        self.create_chart(context, bounds.width, bounds.height)

    def save_image(self, image_file, width, height):
        image_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

        context = cairo.Context(image_surface)
        self.create_chart(context, width, height)
        image_surface.flush()
        image_surface.write_to_png(image_file)

        # generate the preview str
        preview_image_surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, activity.PREVIEW_SIZE[0],
            activity.PREVIEW_SIZE[1])
        preview_context = cairo.Context(preview_image_surface)
        scale = min(activity.PREVIEW_SIZE[0] / float(width),
                    activity.PREVIEW_SIZE[1] / float(height))
        preview_context.rectangle(
            0, 0, activity.PREVIEW_SIZE[0], activity.PREVIEW_SIZE[1])
        preview_context.scale(scale, scale)
        preview_context.set_source_surface(image_surface)
        preview_context.paint()
        preview_image_surface.flush()

        preview_str = StringIO.StringIO()
        preview_image_surface.write_to_png(preview_str)
        return preview_str

    def create_chart(self, context, image_width, image_height):
        if self._chart_type == CHART_TYPE_PIE:
            self._create_pie_chart(context, image_width, image_height)
        if self._chart_type == CHART_TYPE_VERTICAL_BARS:
            self._create_bars_chart(context, image_width, image_height)

    def _measure_text(self, text, font_size, max_width=0):
        if text is None:
            return 0, 0
        layout = self.create_pango_layout(text)
        if max_width > 0:
            layout.set_width(max_width * Pango.SCALE)
            layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        font_desc = Pango.FontDescription("Sans %s" % font_size)
        layout.set_font_description(font_desc)
        return layout.get_pixel_size()

    def _print_text(self, context, x, y, text, font_size, max_width=0,
                    alignment=None, color=None):
        if text is None:
            return
        context.save()
        context.translate(x, y)
        layout = self.create_pango_layout(text)
        if max_width > 0:
            layout.set_width(max_width * Pango.SCALE)
            layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        if alignment is not None:
            layout.set_alignment(alignment)
        font_desc = Pango.FontDescription("Sans %s" % font_size)
        layout.set_font_description(font_desc)

        if color is None:
            context.set_source_rgb(0, 0, 0)
        else:
            context.set_source_rgba(*style.Color(color).get_rgba())

        PangoCairo.update_layout(context, layout)
        PangoCairo.show_layout(context, layout)
        context.fill()

        context.restore()

    def _calculate_title_font_size(self, scale):
        title_font_size = 30 * scale
        if title_font_size < 7:
            title_font_size = 7
        if title_font_size > 12:
            title_font_size = 12
        return title_font_size

    def _create_pie_chart(self, context, image_width, image_height):

        _set_screen_dpi()

        scale = image_width / 1600.
        context.rectangle(0, 0, image_width, image_height)
        logging.debug('canvas size %s x %s - scale %s', image_width,
                      image_height, scale)
        context.set_source_rgb(1, 1, 1)
        context.fill()

        margin_left = (style.GRID_CELL_SIZE / 2) * scale
        margin_top = (style.GRID_CELL_SIZE / 2) * scale
        padding = 20 * scale

        title_font_size = self._calculate_title_font_size(scale)

        title_width, title_height = self._measure_text(
            self._title, title_font_size,
            max_width=image_width - margin_left * 2)
        logging.error('measure text pie %s %s', title_width, title_height)

        rectangles_width = 0
        if self._show_labels:
            # measure the descriptions
            max_width_desc = 0
            max_width_amount = 0
            max_height = 0
            label_font_size = 14 * scale
            for data in self._data:
                description = data['label']
                # If there is no category, display as Unknown
                if description is '':
                    description = _('Unknown')
                if len(description) > 30:
                    description = description[:30] + '...'

                # need measure the description width to align the amounts
                width, height = self._measure_text(description,
                                                   label_font_size)

                max_width_desc = max(max_width_desc, width)
                max_height = max(max_height, height)

                width, height = self._measure_text(str(data['value']),
                                                   label_font_size)

                max_height = max(max_height, height)
                max_width_amount = max(max_width_amount, width)

            # draw the labels
            labels_height = (max_height * 2.5) * len(self._data)
            y = (image_height - labels_height) / 2
            context.save()
            context.translate(margin_left, 0)
            rectangles_width = max_width_desc + max_width_amount + padding * 3
            for data in self._data:
                description = data['label']
                if description is '':
                    description = _('Unknown')
                if len(description) > 30:
                    description = description[:30] + '...'

                context.save()
                context.translate(0, y)
                draw_round_rect(context, 0, 0,
                                rectangles_width, max_height * 2, 10)

                color = style.Color(data['color'])
                context.set_source_rgba(*color.get_rgba())
                context.fill()

                if colors.is_too_light(data['color']):
                    context.set_source_rgb(0, 0, 0)
                else:
                    context.set_source_rgb(1, 1, 1)

                width, height = self._measure_text(description,
                                                   label_font_size)

                self._print_text(context, padding, height * .5, description,
                                 label_font_size)

                text = str(data['value'])
                width, height = self._measure_text(text, label_font_size)

                self._print_text(context, rectangles_width - width - padding,
                                 height * .5, text, label_font_size)

                y += max_height * 2.5
                context.restore()

            context.restore()

        self._print_text(
            context,
            0, margin_top,
            self._title, title_font_size,
            max_width=image_width - margin_left * 2,
            alignment=Pango.Alignment.CENTER, color=self._title_color)
        margin_top += title_height + margin_top * 2

        # draw the pie
        r = min(image_width - rectangles_width - margin_left * 3,
                image_height - margin_top - margin_left) / 2
        y = max(r + margin_top,
                image_height / 2)
        if rectangles_width == 0:
            x = image_width / 2
        else:
            x = image_width - margin_left - r

        total = 0
        for data in self._data:
            total += data['value']

        if total != 0:
            angle = 0.0

            for data in self._data:
                value = data['value']
                slice = 2 * math.pi * value / total
                color = style.Color(data['color'])

                context.move_to(x, y)
                context.arc(x, y, r, angle, angle + slice)
                context.close_path()

                context.set_source_rgba(*color.get_rgba())
                context.fill()

                angle += slice

    def _create_bars_chart(self, context, image_width, image_height):

        _set_screen_dpi()

        scale = image_width / 1600.
        context.rectangle(0, 0, image_width, image_height)
        logging.debug('canvas size %s x %s - scale %s', image_width,
                      image_height, scale)
        context.set_source_rgb(1, 1, 1)
        context.fill()

        margin_top = (style.GRID_CELL_SIZE / 2) * scale
        padding = 20 * scale
        margin = padding * 2

        title_font_size = self._calculate_title_font_size(scale)
        title_width, title_height = self._measure_text(
            self._title, title_font_size,
            max_width=image_width - margin * 2)
        logging.error('measure text bars %s %s', title_width, title_height)

        margin_top += title_height + margin

        graph_width = image_width - margin * 2
        graph_height = image_height - margin_top - margin * 3
        bar_width = graph_width / len(self._data) - margin
        max_bar_height = graph_height

        if self._show_labels:
            # measure the descriptions
            max_height = 0

            for data in self._data:
                description = data['label']
                # If there is no category, display as Unknown
                if description is '':
                    description = _('Unknown')

                width, height = self._measure_text(
                    description, (12 * scale), max_width=bar_width)
                max_height = max(max_height, height)

            max_bar_height = graph_height - max_height

            # draw the labels
            y = max_bar_height + margin * 2 + margin_top
            x = margin * 2
            for data in self._data:
                description = data['label']
                if description is '':
                    description = _('Unknown')

                self._print_text(context, x, y, description, (12 * scale),
                                 max_width=bar_width,
                                 alignment=Pango.Alignment.CENTER)
                x += bar_width + margin

        self._print_text(
            context, 0, margin,
            self._title, title_font_size,
            max_width=image_width - margin * 2,
            alignment=Pango.Alignment.CENTER, color=self._title_color)

        max_value = 0
        for data in self._data:
            max_value = max(max_value, data['value'])

        x_value = margin
        for data in self._data:
            value = data['value']
            bar_height = value * max_bar_height / max_value
            bar_top = max_bar_height - bar_height + margin + margin_top
            top_rounded_rect(context, x_value + margin, bar_top,
                             bar_width, bar_height, 10)
            color = style.Color(data['color'])
            context.set_source_rgba(*color.get_rgba())
            context.fill()

            # draw the value
            width, height = self._measure_text(str(value), (22 * scale))

            x_label = x_value + margin + bar_width / 2 - width / 2
            if height * 2 < bar_height:
                y_label = bar_top + height
            else:
                y_label = bar_top - height * 2

            self._print_text(context, x_label, y_label, str(value),
                             (22 * scale),
                             alignment=Pango.Alignment.CENTER)

            x_value += bar_width + margin

        # add a shadow at the bottom
        context.rectangle(
            2 * margin,
            max_bar_height + margin + margin_top,
            (bar_width + margin) * len(self._data) - margin,
            margin)
        gradient = cairo.LinearGradient(
            2 * margin,
            max_bar_height + margin + margin_top,
            2 * margin,
            max_bar_height + margin * 1.5 + margin_top)
        gradient.add_color_stop_rgba(0, 0, 0, 0, 0.10)
        gradient.add_color_stop_rgba(1, 1, 1, 1, 0.10)
        context.set_source(gradient)
        context.fill()
