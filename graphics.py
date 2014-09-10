import logging
import cairo
import math
from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import PangoCairo
from gi.repository import Pango

from sugar3.graphics import style

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
                every item in the array is a dict with keys 'label' and 'value'
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

    def create_chart(self, context, image_width, image_height):
        if self._chart_type == CHART_TYPE_PIE:
            self._create_pie_chart(context, image_width, image_height)
        if self._chart_type == CHART_TYPE_VERTICAL_BARS:
            self._create_bars_chart(context, image_width, image_height)

    def _measure_title(self, context, title_font_size):
        title_width = 0
        # change the top margin
        title_height = 0
        if self._title is not None:
            # measure the title
            context.save()
            context.select_font_face('Sans', cairo.FONT_SLANT_NORMAL,
                                     cairo.FONT_WEIGHT_NORMAL)
            context.set_font_size(title_font_size)
            x_bearing, y_bearing, width, height, x_advance, y_advance = \
                context.text_extents(self._title)
            title_width = width
            context.restore()
            title_height = height
        return title_width, title_height

    def _print_title(self, context, title_x, title_y, title_font_size):
        if self._title is not None:
            # print the title
            logging.error('Printing title %s', self._title)
            context.save()
            context.set_font_size(title_font_size)
            context.move_to(title_x, title_y)

            if self._title_color is None:
                context.set_source_rgb(0, 0, 0)
            else:
                context.set_source_rgba(*style.Color(
                    self._title_color).get_rgba())

            context.show_text(self._title)
            context.restore()

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

        title_font_size = int(40 * scale)
        title_width, title_height = self._measure_title(context,
                                                        title_font_size)
        margin_top += title_height * 1.5

        rectangles_width = 0
        if self._show_labels:
            # measure the descriptions
            max_width_desc = 0
            max_width_amount = 0
            max_height = 0
            context.select_font_face('Sans', cairo.FONT_SLANT_NORMAL,
                                     cairo.FONT_WEIGHT_NORMAL)
            context.set_font_size(26 * scale)

            for data in self._data:
                description = data['label']
                # If there is no category, display as Unknown
                if description is '':
                    description = _('Unknown')
                if len(description) > 30:
                    description = description[:30] + '...'

                # need measure the description width to align the amounts
                x_bearing, y_bearing, width, height, x_advance, y_advance = \
                    context.text_extents(description)
                max_width_desc = max(max_width_desc, width)
                max_height = max(max_height, height)

                x_bearing, y_bearing, width, height, x_advance, y_advance = \
                    context.text_extents(str(data['value']))
                max_height = max(max_height, height)
                max_width_amount = max(max_width_amount, width)

            # draw the labels
            labels_height = (max_height + padding * 2) * len(self._data)
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
                                rectangles_width, max_height + padding, 10)

                color = colors.get_category_color(description)
                context.set_source_rgb(color[0], color[1], color[2])
                context.fill()

                if colors.is_too_light(colors.get_category_color_str(
                        description)):
                    context.set_source_rgb(0, 0, 0)
                else:
                    context.set_source_rgb(1, 1, 1)

                context.save()
                x_bearing, y_bearing, width, height, x_advance, y_advance = \
                    context.text_extents(description)
                context.move_to(padding, padding * 2.5 + y_bearing)
                context.show_text(description)
                context.restore()

                context.save()
                text = str(data['value'])
                x_bearing, y_bearing, width, height, x_advance, y_advance = \
                    context.text_extents(text)
                context.move_to(rectangles_width - x_advance - padding,
                                padding * 2.5 + y_bearing)
                context.show_text(text)
                context.restore()

                y += max_height + padding * 2
                context.restore()

            context.restore()

        self._print_title(
            context,
            (image_width + rectangles_width) / 2 - title_width / 2,
            margin_top, title_font_size)

        # draw the pie
        x = (image_width - rectangles_width) / 2 + rectangles_width
        y = image_height / 2 + margin_top
        r = min(image_width, image_height - margin_top * 2) / 2

        total = 0
        for data in self._data:
            total += data['value']

        if total != 0:
            angle = 0.0

            for data in self._data:
                value = data['value']
                label = data['label']
                slice = 2 * math.pi * value / total
                color = colors.get_category_color(label)

                context.move_to(x, y)
                context.arc(x, y, r, angle, angle + slice)
                context.close_path()

                context.set_source_rgb(color[0], color[1], color[2])
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

        title_font_size = int(40 * scale)
        title_width, title_height = self._measure_title(context,
                                                        title_font_size)
        margin_top += title_height * 1.5

        margin = padding * 2
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

                layout = self.create_pango_layout(description)
                layout.set_width(bar_width)
                layout.set_wrap(Pango.WrapMode.WORD)
                layout.set_alignment(Pango.Alignment.CENTER)
                font_desc = Pango.FontDescription("Sans %s" % (12 * scale))
                layout.set_font_description(font_desc)
                width, height = layout.get_pixel_size()
                max_height = max(max_height, height)

            max_bar_height = graph_height - max_height

            # draw the labels
            y = max_bar_height + margin * 2 + margin_top
            x = margin * 2.5 + bar_width / 2
            for data in self._data:
                description = data['label']
                if description is '':
                    description = _('Unknown')

                context.save()
                context.translate(x, y)
                logging.error('Printing %s at %s, %s', description, x, y)
                layout = self.create_pango_layout(description)
                layout.set_width(bar_width)
                layout.set_wrap(Pango.WrapMode.WORD)
                layout.set_alignment(Pango.Alignment.CENTER)
                font_desc = Pango.FontDescription("Sans %s" % (12 * scale))
                layout.set_font_description(font_desc)

                context.set_source_rgb(0, 0, 0)
                PangoCairo.update_layout(context, layout)
                PangoCairo.show_layout(context, layout)
                context.fill()

                x += bar_width + margin
                context.restore()

        self._print_title(
            context,
            image_width / 2 - title_width / 2,
            margin_top, title_font_size)

        max_value = 0
        for data in self._data:
            max_value = max(max_value, data['value'])

        x_value = margin * 1.5
        for data in self._data:
            value = data['value']
            label = data['label']
            bar_height = value * max_bar_height / max_value
            top_rounded_rect(
                context,
                x_value + margin,
                max_bar_height - bar_height + margin + margin_top,
                bar_width, bar_height, 10)
            color = colors.get_category_color(label)
            context.set_source_rgb(color[0], color[1], color[2])
            context.fill()
            x_value += bar_width + margin

        # add a shadow at the bottom
        context.rectangle(
            2.5 * margin,
            max_bar_height + margin + margin_top,
            (bar_width + margin) * len(self._data) - margin,
            margin)
        gradient = cairo.LinearGradient(
            2.5 * margin,
            max_bar_height + margin + margin_top,
            2.5 * margin,
            max_bar_height + margin * 1.5 + margin_top)
        gradient.add_color_stop_rgba(0, 0, 0, 0, 0.10)
        gradient.add_color_stop_rgba(1, 1, 1, 1, 0.10)
        context.set_source(gradient)
        context.fill()
