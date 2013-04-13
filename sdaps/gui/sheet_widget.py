# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2007-2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2007-2008, Benjamin Berg <benjamin@sipsolutions.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
import cairo
import copy
import os
from sdaps import defs

from sdaps import model

from sdaps import matrix


class SheetWidget(Gtk.DrawingArea, Gtk.Scrollable):
    __gtype_name__ = "SDAPSSheetWidget"

    def __init__(self, provider, handle=None):
        Gtk.DrawingArea.__init__(self)
        events = Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | \
            Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_MOTION_MASK | \
            Gdk.EventMask.SCROLL_MASK | Gdk.EventMask.KEY_PRESS_MASK
        try:
            events = events | Gdk.EventMask.SMOOTH_SCROLL_MASK
        except AttributeError:
            # Does only work for GTK+ >=3.4
            pass
        self.add_events(events)

        self._handle = handle

        self.hadj = None
        self.vadj = None
        self._hadj_value_changed_cb_id = None
        self._vadj_value_changed_cb_id = None

        self.provider = provider

        self._old_scroll_x = 0
        self._old_scroll_y = 0
        self._edge_drag_active = False

        self._zoom = 1.0
        self._bbox = None

        self.props.can_focus = True

        self._update_matrices()
        self._cs_image = None
        self._ss_image = None

        self.provider.survey.questionnaire.connect_data_changed(self.partial_update)

    def update_state(self):
        # Cancel any dragging operation
        self._edge_drag_active = False
        self._update_matrices()
        self.queue_resize()
        self.queue_draw()

    def partial_update(self, questionnaire, qobj, obj, name, old_value):
        if not isinstance(obj, model.data.Box):
            return

        if not self.provider.is_handle_active(self._handle):
            return

        if self.image is None:
            return

        if self.image.page_number != qobj.page_number:
            return

        self.invalidate_area(obj.x, obj.y, obj.width, obj.height)

    def _get_px_bbox(self):
        if self._bbox is None:
            return None

        if self.image is None:
            return None

        matrix = self.image.matrix.mm_to_px()
        x0, y0 = matrix.transform_point(self._bbox[0], self._bbox[1])
        x1, y1 = matrix.transform_point(self._bbox[0] + self._bbox[2], self._bbox[1])
        x2, y2 = matrix.transform_point(self._bbox[0], self._bbox[1] + self._bbox[3])
        x3, y3 = matrix.transform_point(self._bbox[0] + self._bbox[2], self._bbox[1] + self._bbox[3])

        x = min(x0, x2)
        y = min(y0, y1)

        x = x * self._zoom
        y = y * self._zoom

        x = int(math.floor(x))
        y = int(math.floor(y))

        width = max(x1, x3) - x / self._zoom
        height = max(y2, y3) - y / self._zoom

        width = width * self._zoom
        height = height * self._zoom

        width = int(math.ceil(width))
        height = int(math.ceil(height))

        return x, y, width, height

    def _update_matrices(self):
        if self.image is None:
            self._mm_to_widget_matrix = cairo.Matrix()
            self._widget_to_mm_matrix = cairo.Matrix()

            return

        pxbbox = self._get_px_bbox()

        xoffset = 0
        yoffset = 0
        if self.hadj:
            xoffset = int(self.hadj.props.value)
        if self.vadj:
            yoffset = int(self.vadj.props.value)

        if pxbbox:
            xoffset += pxbbox[0]
            yoffset += pxbbox[1]

        m = cairo.Matrix(self._zoom, 0,
                         0, self._zoom,
                         -xoffset, -yoffset)
        form_matrix = self.image.matrix.mm_to_px()
        m = form_matrix.multiply(m)

        self._mm_to_widget_matrix = m
        self._widget_to_mm_matrix = \
            cairo.Matrix(*m)
        self._widget_to_mm_matrix.invert()

    def invalidate_area(self, x_mm, y_mm, width_mm, height_mm):
        x, y = self._mm_to_widget_matrix.transform_point(x_mm, y_mm)
        width, height = self._mm_to_widget_matrix.transform_distance(width_mm, height_mm)

        width = int(math.ceil(width + x - int(x))) + 20
        height = int(math.ceil(height + y - int(y))) + 20
        x = int(x) - 10
        y = int(y) - 10

        self.queue_draw_area(x, y, width, height)

    def _adjustment_changed_cb(self, adjustment):
        dx = int(self._old_scroll_x) - int(self.hadj.props.value)
        dy = int(self._old_scroll_y) - int(self.vadj.props.value)

        if self.get_window() is not None:
            self.get_window().scroll(dx, dy)

        self._old_scroll_x = self.hadj.props.value
        self._old_scroll_y = self.vadj.props.value

        # Update the transformation matrices
        self._update_matrices()

    def do_button_press_event(self, event):
        if self.image is None:
            return False

        self.provider.ensure_handle_active(self._handle)

        # Pass everything except normal clicks down
        if event.button != 1 and event.button != 2 and event.button != 3:
            return False

        if event.button == 2:
            self._drag_start_x = event.x
            self._drag_start_y = event.y
            cursor = Gdk.Cursor(Gdk.CursorType.HAND2)
            self.get_window().set_cursor(cursor)
            return True

        mm_x, mm_y = self._widget_to_mm_matrix.transform_point(event.x, event.y)

        if event.button == 3:
            # Give the corresponding widget the focus.
            box = self.provider.survey.questionnaire.gui.find_box(self.image.page_number, mm_x, mm_y)
            if hasattr(box, "widget"):
                box.widget.focus()

            return True

        # button 1
        self.grab_focus()

        # Look for edges to drag first(on a 4x4px target)
        tollerance_x, tollerance_y = self._widget_to_mm_matrix.transform_distance(4.0, 4.0)
        result = self.provider.survey.questionnaire.gui.find_edge(self.image.page_number, mm_x, mm_y,
                                                                  tollerance_x, tollerance_y)
        if result:
            self._edge_drag_active = True
            self._edge_drag_obj = result[0]
            self._edge_drag_data = result[1]
            return True

        box = self.provider.survey.questionnaire.gui.find_box(self.image.page_number, mm_x, mm_y)

        if box is not None:
            box.data.state = not box.data.state

            return True

    def do_button_release_event(self, event):
        if self.image is None:
            return False

        self.provider.ensure_handle_active(self._handle)

        if event.button != 1 and event.button != 2 and event.button != 3:
            return False

        self.get_window().set_cursor(None)

        if event.button == 1:
            self._edge_drag_active = False

        return True

    def do_motion_notify_event(self, event):
        if self.image is None:
            return False

        self.provider.ensure_handle_active(self._handle)

        if event.state & Gdk.ModifierType.BUTTON2_MASK:
            x = int(event.x)
            y = int(event.y)

            dx = self._drag_start_x - x
            dy = self._drag_start_y - y

            if self.hadj:
                value = self.hadj.props.value + dx
                value = min(value, self.hadj.props.upper - self.hadj.props.page_size)
                self.hadj.set_value(value)
            if self.vadj:
                value = self.vadj.props.value + dy
                value = min(value, self.vadj.props.upper - self.vadj.props.page_size)
                self.vadj.set_value(value)

            self._drag_start_x = event.x
            self._drag_start_y = event.y

            return True
        elif event.state & Gdk.ModifierType.BUTTON1_MASK:
            if self._edge_drag_active:
                mm_x, mm_y = self._widget_to_mm_matrix.transform_point(event.x, event.y)

                self._edge_drag_obj.gui.move_edge(self._edge_drag_data, mm_x, mm_y)

                self.queue_draw()
                return True

        return False

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE

    def do_get_preferred_height(self):
        if self.vadj:
            self.vadj.props.upper = self._render_height

            return min(self._render_height, 300), self._render_height
        else:
            return self._render_height, self._render_height

    def do_get_preferred_width(self):
        if self.hadj:
            self.hadj.props.upper = self._render_width

            return min(self._render_width, 300), self._render_width
        else:
            return self._render_width, self._render_width

    def do_size_allocate(self, allocation):
        # WTF? Why does this happen?
        if allocation.x < 0 or allocation.y < 0:
            GObject.idle_add(self.queue_resize)

        if self.hadj:
            self.hadj.props.page_size = min(self._render_width, allocation.width)
            if self.hadj.props.value > self._render_width - allocation.width:
                self.hadj.props.value = self._render_width - allocation.width
            self.hadj.props.page_increment = allocation.width * 0.9
            self.hadj.props.step_increment = allocation.width * 0.1
        if self.vadj:
            self.vadj.props.page_size = min(self._render_height, allocation.height)
            if self.vadj.props.value > self._render_height - allocation.height:
                self.vadj.props.value = self._render_height - allocation.height
            self.vadj.props.page_increment = allocation.height * 0.9
            self.vadj.props.step_increment = allocation.height * 0.1

        self._update_matrices()

        Gtk.DrawingArea.do_size_allocate(self, allocation)

    def do_draw(self, cr):
        xoffset = 0
        yoffset = 0

        image = self.surface
        # If we don't have a surface, just give up (and paint an ugly red color)
        if image is None:
            cr.set_source_rgb(1, 0.8, 0.8)
            cr.paint()

            return

        if self.hadj:
            xoffset += int(self.hadj.props.value)
        if self.vadj:
            yoffset += int(self.vadj.props.value)

        pxbbox = self._get_px_bbox()
        if pxbbox:
            xoffset += pxbbox[0]
            yoffset += pxbbox[1]

            cr.rectangle(0, 0, math.ceil(pxbbox[2]), math.ceil(pxbbox[3]))
            cr.clip()

        if image != self._cs_image or self._ss_image is None:
            self._cs_image = image
            target = cr.get_target()
            self._ss_image = target.create_similar(cairo.CONTENT_COLOR, image.get_width(), image.get_height())
            subcr = cairo.Context(self._ss_image)
            subcr.set_source_surface(self._cs_image)
            subcr.paint()

        # Draw the image in the background
        cr.translate(-xoffset, -yoffset)
        cr.scale(self._zoom, self._zoom)

        cr.set_source_surface(self._ss_image, 0, 0)
        cr.paint()

        # Set the matrix _after_ drawing the background pixbuf.
        cr.set_matrix(self._mm_to_widget_matrix)

        cr.set_source_rgba(1.0, 0.0, 0.0, 0.6)
        cr.set_line_width(1.0 * 25.4 / 72.0)
        cr.rectangle(defs.corner_mark_left, defs.corner_mark_top,
                     self.provider.survey.defs.paper_width - defs.corner_mark_left - defs.corner_mark_right,
                     self.provider.survey.defs.paper_height - defs.corner_mark_top - defs.corner_mark_bottom)
        cr.stroke()

        self.provider.ensure_handle_active(self._handle)

        # Draw the overlay stuff.
        self.provider.survey.questionnaire.gui.draw(cr, self.image.page_number)

        def inner_box(cr, x, y, width, height):
            line_width = cr.get_line_width()

            cr.rectangle(x + line_width / 2.0, y + line_width / 2.0,
                         width - line_width, height - line_width)

        if self.provider.survey.defs.style == 'classic':
            half_pt = 0.5 / 72.0 * 25.4
            pt = 1.0 / 72.0 * 25.4
            inner_box(cr,
                      defs.corner_mark_left + defs.corner_box_padding - half_pt,
                      defs.corner_mark_top + defs.corner_box_padding - half_pt,
                      defs.corner_box_width + pt,
                      defs.corner_box_height + pt)
            inner_box(cr,
                      self.provider.survey.defs.paper_width
                          - defs.corner_mark_right
                          - defs.corner_box_padding
                          - defs.corner_box_width - half_pt,
                      defs.corner_mark_top + defs.corner_box_padding - half_pt,
                      defs.corner_box_width + pt,
                      defs.corner_box_height + pt)
            inner_box(cr,
                      defs.corner_mark_left + defs.corner_box_padding - half_pt,
                      self.provider.survey.defs.paper_height
                          - defs.corner_mark_bottom
                          - defs.corner_box_padding
                          - defs.corner_box_height
                          - half_pt,
                      defs.corner_box_width + pt,
                      defs.corner_box_height + pt)
            inner_box(cr,
                      self.provider.survey.defs.paper_width
                          - defs.corner_mark_right
                          - defs.corner_box_padding
                          - defs.corner_box_width
                          - half_pt,
                      self.provider.survey.defs.paper_height
                          - defs.corner_mark_bottom
                          - defs.corner_box_padding
                          - defs.corner_box_height
                          - half_pt,
                      defs.corner_box_width + pt,
                      defs.corner_box_height + pt)
            cr.stroke()

        return True

    def do_key_press_event(self, event):
        if self.image is None:
            return False

        if self.vadj:
            if event.keyval == Gdk.keyval_from_name("Up"):
                value = self.vadj.props.value - self.vadj.props.step_increment
                value = min(value, self.vadj.props.upper - self.vadj.props.page_size)
                self.vadj.set_value(value)
                return True
            if event.keyval == Gdk.keyval_from_name("Down"):
                value = self.vadj.props.value + self.vadj.props.step_increment
                value = min(value, self.vadj.props.upper - self.vadj.props.page_size)
                self.vadj.set_value(value)
                return True

        if self.hadj:
            if event.keyval == Gdk.keyval_from_name("Left"):
                value = self.hadj.props.value - self.hadj.props.step_increment
                value = min(value, self.hadj.props.upper - self.hadj.props.page_size)
                self.hadj.set_value(value)
                return True
            if event.keyval == Gdk.keyval_from_name("Right"):
                value = self.hadj.props.value + self.hadj.props.step_increment
                value = min(value, self.hadj.props.upper - self.hadj.props.page_size)
                self.hadj.set_value(value)
                return True
        return False

    def _get_image(self):
        return self.provider.get_image(self._handle)

    image = property(_get_image)

    def _get_surface(self):
        image = self.image
        if image is None:
            return None

        return image.surface.surface_rgb

    surface = property(_get_surface)

    def _get_render_width(self):
        if self._bbox:
            return self._get_px_bbox()[2]

        image = self.surface
        if image:
            width = image.get_width()
        else:
            width = 400
        width = int(math.ceil(self._zoom * width))
        return width

    def _get_render_height(self):
        if self._bbox:
            return self._get_px_bbox()[3]

        image = self.surface
        if image:
            height = image.get_height()
        else:
            height = 400

        height = int(math.ceil(self._zoom * height))
        return height

    _render_width = property(_get_render_width)
    _render_height = property(_get_render_height)

    def get_hscroll_policy(self):
        # Does not matter, we don't support natural sizes
        return Gtk.ScrollablePolicy.NATURAL
    hscroll_policy = \
        GObject.property(get_hscroll_policy,
                         type=Gtk.ScrollablePolicy,
                         default=Gtk.ScrollablePolicy.NATURAL)

    def get_vscroll_policy(self):
        # Does not matter, we don't support natural sizes
        return Gtk.ScrollablePolicy.NATURAL
    vscroll_policy = \
        GObject.property(get_vscroll_policy,
                         type=Gtk.ScrollablePolicy,
                         default=Gtk.ScrollablePolicy.NATURAL)

    def get_vadjustment(self):
        return self.vadj

    def set_vadjustment(self, value):
        if self._vadj_value_changed_cb_id is not None:
            self.vadj.disconnect(self._vadj_value_changed_cb_id)
            self._vadj_value_changed_cb_id = None
        self.vadj = value

        if self.vadj is not None:
            self._vadj_value_changed_cb_id = self.vadj.connect('value-changed', self._adjustment_changed_cb)

        self._update_matrices()

    vadjustment = GObject.property(get_vadjustment, set_vadjustment, type=Gtk.Adjustment)

    def get_hadjustment(self):
        return self.hadj

    def set_hadjustment(self, value):
        if self._hadj_value_changed_cb_id is not None:
            self.hadj.disconnect(self._hadj_value_changed_cb_id)
            self._hadj_value_changed_cb_id = None
        self.hadj = value

        if self.hadj is not None:
            self._hadj_value_changed_cb_id = self.hadj.connect('value-changed', self._adjustment_changed_cb)

        self._update_matrices()

    hadjustment = GObject.property(get_hadjustment, set_hadjustment, type=Gtk.Adjustment)

    def set_zoom(self, value):
        self._zoom = value
        self.queue_resize()

    def get_zoom(self):
        return self._zoom

    zoom = GObject.property(get_zoom, set_zoom, float, minimum=0.001, maximum=1024.0, default=1.0)

