# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2007-2008, Christoph Simon <christoph.simon@gmx.eu>
# Copyright (C) 2007-2008, Benjamin Berg <benjamin@sipsolutions.net>
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
import gtk
import cairo
import gobject
from sdaps import utils
import copy
import os
from sdaps import defs

from sdaps import model

from sdaps import matrix


class SheetWidget(gtk.DrawingArea):
	__gtype_name__ = "SDAPSSheetWidget"

	__gproperties__ = {
		'zoom'          : (float, None, None, 0.001, 1024.0, 1.0,
						   gobject.PARAM_READWRITE),
	}

	def __init__(self, provider) :
		gtk.DrawingArea.__init__(self)
		self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK|
						gtk.gdk.MOTION_NOTIFY | gtk.gdk.SCROLL |
						gtk.gdk.KEY_PRESS_MASK)
		self.hadj = None
		self.vadj = None

		self.provider = provider

		self._old_scroll_x = 0
		self._old_scroll_y = 0
		self._edge_drag_active = False

		self._zoom = 1.0

		self.props.can_focus = True

		gobject.signal_new('set_scroll_adjustments', SheetWidget,
						   gobject.SIGNAL_NO_HOOKS, None, (gtk.Adjustment, gtk.Adjustment))
		self.set_set_scroll_adjustments_signal("set_scroll_adjustments")
		self.connect("set_scroll_adjustments", self.do_set_scroll_adjustments)

		self._update_matrices()
		self._cs_image = None
		self._ss_image = None

	def update_state(self):
		# Cancel any dragging operation
		self._edge_drag_active = False
		self._update_matrices()
		self.queue_draw()

	def _update_matrices(self):
		xoffset = 0
		yoffset = 0
		if self.hadj:
			xoffset = int(self.hadj.value)
		if self.vadj:
			yoffset = int(self.vadj.value)

		m = cairo.Matrix(self._zoom, 0,
		                 0, self._zoom,
		                 -xoffset, -yoffset)
		form_matrix = self.provider.image.matrix.mm_to_px()
		m = form_matrix.multiply(m)

		self._mm_to_widget_matrix = m
		self._widget_to_mm_matrix = \
			cairo.Matrix(*m)
		self._widget_to_mm_matrix.invert()

	def invalidate_question_area(self, question):
		# Just invalidate the bounding box of all boxes for now
		bbox = question_utils.get_question_bounding_box(question)

		x, y = self._mm_to_widget_matrix.transform_point(bbox[0], bbox[1])
		width, height = self._mm_to_widget_matrix.transform_distance(bbox[2], bbox[3])

		width = int(math.ceil(width + x - int(x)))+20
		height = int(math.ceil(height + y - int(y)))+20
		x = int(x)-10
		y = int(y)-10

		self.queue_draw_area(x, y, width, height)

	def invalidate_area (self, x_mm, y_mm, width_mm, height_mm) :
		x, y = self._mm_to_widget_matrix.transform_point(x_mm, y_mm)
		width, height = self._mm_to_widget_matrix.transform_distance(width_mm, height_mm)

		width = int(math.ceil(width + x - int(x)))+20
		height = int(math.ceil(height + y - int(y)))+20
		x = int(x)-10
		y = int(y)-10

		self.queue_draw_area(x, y, width, height)

	def do_set_scroll_adjustments(dummy, self, hadj, vadj):
		self.hadj = hadj
		self.vadj = vadj

		if hadj:
			hadj.connect('value-changed', self._adjustment_changed_cb)
			self._old_scroll_x = hadj.value
		if vadj:
			vadj.connect('value-changed', self._adjustment_changed_cb)
			self._old_scroll_y = vadj.value
		return True

	def _adjustment_changed_cb(self, adjustment):
		dx = int(self._old_scroll_x) - int(self.hadj.value)
		dy = int(self._old_scroll_y) - int(self.vadj.value)

		self.window.scroll(dx, dy)

		self._old_scroll_x = self.hadj.value
		self._old_scroll_y = self.vadj.value

		# Update the transformation matrices
		self._update_matrices ()

	def do_button_press_event(self, event):
		# Pass everything except normal clicks down
		if event.button != 1 and event.button != 2:
			return False

		if event.button == 2:
			self._drag_start_x = event.x
			self._drag_start_y = event.y
			cursor = gtk.gdk.Cursor(gtk.gdk.HAND2)
			self.window.set_cursor(cursor)
			return True

		# button 1
		self.grab_focus()

		mm_x, mm_y = self._widget_to_mm_matrix.transform_point(event.x, event.y)

		# Look for edges to drag first (on a 4x4px target)
		tollerance_x, tollerance_y = self._widget_to_mm_matrix.transform_distance(4.0, 4.0)
		result = self.provider.survey.questionnaire.gui.find_edge(self.provider.image.page_number, mm_x, mm_y,
		                                                          tollerance_x, tollerance_y)
		if result:
			self._edge_drag_active = True
			self._edge_drag_obj = result[0]
			self._edge_drag_data = result[1]
			return True

		box = self.provider.survey.questionnaire.gui.find_box(self.provider.image.page_number, mm_x, mm_y)

		if box is not None :
			box.data.state = not box.data.state
			self.invalidate_area(box.data.x, box.data.y, box.data.width, box.data.height)
			return True


	def do_button_release_event(self, event):
		if event.button != 1 and event.button != 2:
			return False

		self.window.set_cursor(None)

		if event.button == 1:
			self._edge_drag_active = False

		return True

	def do_motion_notify_event(self, event):
		if event.state & gtk.gdk.BUTTON2_MASK:
			x = int(event.x)
			y = int(event.y)

			dx = self._drag_start_x - x
			dy = self._drag_start_y - y

			if self.hadj:
				value = self.hadj.value + dx
				value = min(value, self.hadj.upper - self.hadj.page_size)
				self.hadj.set_value(value)
			if self.vadj:
				value = self.vadj.value + dy
				value = min(value, self.vadj.upper - self.vadj.page_size)
				self.vadj.set_value(value)

			self._drag_start_x = event.x
			self._drag_start_y = event.y

			return True
		elif event.state & gtk.gdk.BUTTON1_MASK:
			if self._edge_drag_active:
				mm_x, mm_y = self._widget_to_mm_matrix.transform_point(event.x, event.y)

				self._edge_drag_obj.gui.move_edge(self._edge_drag_data, mm_x, mm_y)

				self.queue_draw()
				return True

		return False


	def do_size_request(self, requisition):
		requisition[0] = self._render_width
		requisition[1] = self._render_height

		if self.hadj:
			self.hadj.props.upper = self._render_width
		if self.vadj:
			self.vadj.props.upper = self._render_height
		self.queue_draw()

	def do_size_allocate(self, allocation):
		if self.hadj:
			self.hadj.page_size = allocation.width
			self.hadj.page_increment = allocation.width * 0.9
			self.hadj.step_increment = allocation.width * 0.1
		if self.vadj:
			self.vadj.page_size = allocation.height
			self.vadj.page_increment = allocation.height * 0.9
			self.vadj.step_increment = allocation.height * 0.1

		self._update_matrices ()

		gtk.DrawingArea.do_size_allocate(self, allocation)

	def do_expose_event(self, event):
		cr = event.window.cairo_create()
		cr = gtk.gdk.CairoContext(cr)

		event.window.clear()
		# For the image
		xoffset = -int(self.hadj.value)
		yoffset = -int(self.vadj.value)

		# In theory we could get the region of the ExposeEvent, and only
		# draw on that area. The same goes for the image blitting.
		# However, pygtk does not expose the region attribute :-(
		#cr.region(event.region)
		rect = event.area
		cr.rectangle(rect.x, rect.y, rect.width, rect.height)
		cr.clip()

		image = self.provider.image.surface.surface

		if image != self._cs_image or self._ss_image is None:
			self._cs_image = image
			target = cr.get_target()
			self._ss_image = target.create_similar(cairo.CONTENT_COLOR, image.get_width(), image.get_height())
			subcr = cairo.Context(self._ss_image)
			subcr.set_source_rgb(1, 1, 1)
			subcr.paint()
			subcr.set_source_rgb(0, 0, 0)
			subcr.mask_surface(image)

		# Draw the image in the background
		cr.translate(xoffset, yoffset)
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

		# Draw the overlay stuff.
		self.provider.survey.questionnaire.gui.draw(cr, self.provider.image.page_number)

		def inner_box(cr, x, y, width, height):
			line_width = cr.get_line_width()

			cr.rectangle(x + line_width/2.0, y + line_width/2.0,
						 width - line_width, height - line_width)

		half_pt = 0.5 / 72.0 * 25.4
		pt = 1.0 / 72.0 * 25.4
		inner_box(cr, 13.0 - half_pt, 15.0 - half_pt, 3.5 + pt, 3.5 + pt)
		inner_box(cr, 193.5 - half_pt, 15.0 - half_pt, 3.5 + pt, 3.5 + pt)
		inner_box(cr, 13.0 - half_pt, 278.5 - half_pt, 3.5 + pt, 3.5 + pt)
		inner_box(cr, 193.5 - half_pt, 278.5 - half_pt, 3.5 + pt, 3.5 + pt)
		cr.stroke()
		
		return True

	def do_key_press_event(self, event):
		if self.vadj:
			if event.keyval == gtk.gdk.keyval_from_name("Up"):
				value = self.vadj.value - self.vadj.step_increment
				value = min(value, self.vadj.upper - self.vadj.page_size)
				self.vadj.set_value(value)
				return True
			if event.keyval == gtk.gdk.keyval_from_name("Down"):
				value = self.vadj.value + self.vadj.step_increment
				value = min(value, self.vadj.upper - self.vadj.page_size)
				self.vadj.set_value(value)
				return True

		if self.hadj:
			if event.keyval == gtk.gdk.keyval_from_name("Left"):
				value = self.hadj.value - self.hadj.step_increment
				value = min(value, self.hadj.upper - self.hadj.page_size)
				self.hadj.set_value(value)
				return True
			if event.keyval == gtk.gdk.keyval_from_name("Right"):
				value = self.hadj.value + self.hadj.step_increment
				value = min(value, self.hadj.upper - self.hadj.page_size)
				self.hadj.set_value(value)
				return True
		return False

	def do_set_property(self, pspec, value):
		if pspec.name == 'zoom':
			self._zoom = value
			self.queue_resize()
		else:
			raise AssertionError

	def do_get_property(self, pspec):
		if pspec.name == 'zoom':
			return self._zoom
		else:
			raise AssertionError

	def _get_render_width(self):
		image = self.provider.image.surface.surface
		if image:
			width = image.get_width()
		else:
			width = 400
		width = int(math.ceil(self._zoom * width))
		return width

	def _get_render_height(self):
		image = self.provider.image.surface.surface
		if image:
			height = image.get_height()
		else:
			height= 400

		height = int(math.ceil(self._zoom * height))
		return height

	_render_width = property(_get_render_width)
	_render_height = property(_get_render_height)



