import logging
import cairo
import math
from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import PangoCairo

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


CHART_TYPE_PIE = 1
CHART_TYPE_VERTICAL_BARS = 2


class Chart(Gtk.DrawingArea):

    def __init__(self, data, chart_type):
        # data is a dictionary, with the key (str) and the value (number)
        Gtk.DrawingArea.__init__(self)
        self._data = data
        self._chart_type = chart_type
        self.sorted_categories = self._data.keys()
        self.connect('draw', self.__chart_draw_cb)

    def set_data(self, data):
        self._data = data
        self.queue_draw()

    def set_chart_type(self, chart_type):
        self._chart_type = chart_type
        self.queue_draw()

    def __chart_draw_cb(self, widget, context):
        # Draw pie chart.
        bounds = widget.get_allocation()
        self.create_chart(context, bounds.width, bounds.height)

    def create_chart(self, context, image_width, image_height):

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

        # measure the descriptions
        max_width_desc = 0
        max_width_amount = 0
        max_height = 0
        context.select_font_face('Sans', cairo.FONT_SLANT_NORMAL,
                                 cairo.FONT_WEIGHT_NORMAL)
        context.set_font_size(26 * scale)

        for c in self.sorted_categories:
            description = c
            # If there is no category, display as Unknown
            if c is '':
                description = _('Unknown')

            # need measure the description width to align the amounts
            x_bearing, y_bearing, width, height, x_advance, y_advance = \
                context.text_extents(description)
            max_width_desc = max(max_width_desc, width)
            max_height = max(max_height, height)

            x_bearing, y_bearing, width, height, x_advance, y_advance = \
                context.text_extents(str(self._data[c]))
            max_height = max(max_height, height)
            max_width_amount = max(max_width_amount, width)

        # draw the labels
        y = margin_top
        context.save()
        context.translate(margin_left, 0)
        rectangles_width = max_width_desc + max_width_amount + padding * 3
        for c in self.sorted_categories:
            description = c
            if c is '':
                description = _('Unknown')
            context.save()
            context.translate(0, y)
            context.rectangle(0, 0, rectangles_width, max_height + padding)

            color = colors.get_category_color(c)
            context.set_source_rgb(color[0], color[1], color[2])
            context.fill()

            if colors.is_too_light(colors.get_category_color_str(c)):
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
            text = str(self._data[c])
            x_bearing, y_bearing, width, height, x_advance, y_advance = \
                context.text_extents(text)
            context.move_to(rectangles_width - x_advance - padding,
                            padding * 2.5 + y_bearing)
            context.show_text(text)
            context.restore()

            y += max_height + padding * 2
            context.restore()

        context.restore()

        if self._chart_type == CHART_TYPE_PIE:
            # draw the pie
            x = (image_width - rectangles_width) / 2 + rectangles_width
            y = image_height / 2
            r = min(image_width, image_height) / 2 - 10

            total = 0
            for c in self.sorted_categories:
                total += self._data[c]

            if total != 0:
                angle = 0.0

                for c in self.sorted_categories:
                    slice = 2 * math.pi * self._data[c] / total
                    color = colors.get_category_color(c)

                    context.move_to(x, y)
                    context.arc(x, y, r, angle, angle + slice)
                    context.close_path()

                    context.set_source_rgb(color[0], color[1], color[2])
                    context.fill()

                    angle += slice

        if self._chart_type == CHART_TYPE_VERTICAL_BARS:
            margin = 20
            graph_width = image_width - rectangles_width - margin * 2
            graph_height = image_height - margin * 2
            bar_width = graph_width / len(self.sorted_categories) - margin

            max_value = 0
            for c in self.sorted_categories:
                max_value = max(max_value, self._data[c])

            x_value = rectangles_width + margin
            for c in self.sorted_categories:
                bar_height = self._data[c] * graph_height / max_value
                context.rectangle(x_value + margin, graph_height - bar_height,
                                  bar_width, bar_height)
                color = colors.get_category_color(c)
                context.set_source_rgb(color[0], color[1], color[2])
                context.fill()
                x_value += bar_width + margin

            # add a shadow at the bottom
            context.rectangle(
                rectangles_width + 2 * margin, graph_height,
                (bar_width + margin) * len(self.sorted_categories) - margin,
                margin)
            gradient = cairo.LinearGradient(
                rectangles_width + 2 * margin, graph_height,
                rectangles_width + 2 * margin, graph_height + margin)
            gradient.add_color_stop_rgba(0, 0, 0, 0, 0.25)
            gradient.add_color_stop_rgba(1, 1, 1, 1, 0.25)
            context.set_source(gradient)
            context.fill()
