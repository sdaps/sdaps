# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <christoph.simon@gmx.eu>
# Copyright (C) 2008,2011, Benjamin Berg <benjamin@sipsolutions.net>
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

import cairo
import random

from sdaps import model
from sdaps import matrix
from sdaps import surface
from sdaps import image
from sdaps import defs

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

class Sheet (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'recognize'
	obj_class = model.sheet.Sheet

	def recognize (self) :
		self.obj.valid = 1
		try :
			for image in self.obj.images :
				image.recognize.recognize()
		except RecognitionError :
			self.obj.valid = 0
			raise
		self.obj.images.sort(key = lambda image : image.page_number)

	def clean (self) :
		for image in self.obj.images :
			image.recognize.clean()


class RecognitionError (Exception) :

	pass


class Image (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'recognize'
	obj_class = model.sheet.Image

	def recognize (self) :
		self.obj.rotated = 0
		self.obj.surface.load()
		try :
			self.calculate_matrix()
		except RecognitionError :
			print _('%s: Matrix not recognized. Cancelling recognition of that image.') % self.obj.filename
			raise RecognitionError

		# The coordinates in defs are the center of the line, not the bounding box of the box ...
		# Its a bug im stamp
		# So we need to adjust them
		half_pt = 0.5 / 72.0 * 25.4
		pt = 1.0 / 72.0 * 25.4

		width = defs.corner_box_width
		height = defs.corner_box_height
		padding = defs.corner_box_padding
		survey = self.obj.sheet.survey
		corner_boxes_positions = [
			(defs.corner_mark_left + padding, defs.corner_mark_top + padding),
			(survey.defs.paper_width - defs.corner_mark_right - padding - width, defs.corner_mark_top + padding),
			(defs.corner_mark_left + padding, survey.defs.paper_height - defs.corner_mark_bottom - padding - height),
			(survey.defs.paper_width - defs.corner_mark_right - padding - width,
			 survey.defs.paper_height - defs.corner_mark_bottom - padding - height)
		]
		corners = [
			int(image.get_coverage(
				self.obj.surface.surface, self.matrix,
				corner[0] - half_pt,
				corner[1] - half_pt,
				width + pt,
				height + pt
			) > 0.7)
			for corner in corner_boxes_positions
		]

		try :
			self.obj.page_number = defs.corner_boxes.index(corners) + 1
		except ValueError :
			try :
				self.obj.page_number = defs.corner_boxes.index(corners[::-1]) + 1
			except ValueError :
				print _('%s: Page number not recognized. Cancelling recognition of that image.') % self.obj.filename
				raise RecognitionError
			else :
				self.obj.rotated = 1
				self.obj.surface.load()
				try :
					self.calculate_matrix()
				except RecognitionError :
					print _('%s: Matrix not recognized. Cancelling recognition of that image.') % self.obj.filename
					raise RecognitionError
		else :
			self.obj.rotated = 0

		if self.obj.page_number % 2 == 0 or \
		   self.obj.sheet.survey.questionnaire.page_count == 1 :
			# read ids if they are printed on the page
			if self.obj.sheet.survey.defs.print_survey_id :
				pos = self.obj.sheet.survey.defs.get_survey_id_pos()

				self.obj.sheet.survey_id = self.read_codebox(
					pos[0], pos[2]
				)
				self.obj.sheet.survey_id = self.read_codebox(
					pos[1], pos[2],
					self.obj.sheet.survey_id
				)
				if not self.obj.sheet.survey_id == self.obj.sheet.survey.survey_id :
					print _('%s: Wrong survey_id. Cancelling recognition of that image.') % self.obj.filename
					raise RecognitionError
			else:
				self.obj.sheet.survey_id = self.obj.sheet.survey.survey_id

			if self.obj.sheet.survey.defs.print_questionnaire_id :
				pos = self.obj.sheet.survey.defs.get_questionnaire_id_pos()

				self.obj.sheet.questionnaire_id = self.read_codebox(
					pos[0], pos[2]
				)
				print self.obj.sheet.questionnaire_id
			else:
				self.obj.sheet.questionnaire_id = -1

	def clean (self) :
		self.obj.surface.clean()
		if hasattr(self, 'matrix') : del self.matrix

	def read_codebox (self, x, y, code = 0) :
		for i in range(defs.codebox_length) :
			code <<= 1
			coverage = image.get_coverage(
				self.obj.surface.surface,
				self.matrix,
				x + (i * defs.codebox_step) + defs.codebox_offset,
				y + defs.codebox_offset,
				defs.codebox_step - 2 * defs.codebox_offset,
				defs.codebox_height - 2 * defs.codebox_offset
			)
			if coverage > 0.7 : code += 1
		return code

	def calculate_matrix (self) :
		try :
			matrix = image.calculate_matrix(
				self.obj.surface.surface,
				defs.corner_mark_left, defs.corner_mark_top,
				self.obj.sheet.survey.defs.paper_width - defs.corner_mark_left - defs.corner_mark_right,
				self.obj.sheet.survey.defs.paper_height - defs.corner_mark_top - defs.corner_mark_bottom,
			)
		except AssertionError :
			self.matrix = self.obj.matrix.mm_to_px()
			raise RecognitionError
		else :
			self.obj.raw_matrix = tuple(matrix)
			self.matrix = self.obj.matrix.mm_to_px()

	def get_coverage (self, x, y, width, height) :
		return image.get_coverage(
			self.obj.surface.surface,
			self.matrix,
			x, y, width, height
		)

	def correction_matrix(self, x, y, width, height):
		return image.calculate_correction_matrix(
			self.obj.surface.surface,
			self.matrix,
			x, y,
			width, height
		)

	def find_box_corners(self, x, y, width, height):
		tl, tr, br, bl = image.find_box_corners(
			self.obj.surface.surface,
			self.matrix,
			x, y,
			width, height)

		tolerance = 1.5
		if (abs(x - tl[0]) > tolerance or
		    abs(y - tl[1]) > tolerance or
		    abs(x + width - tr[0]) > tolerance or
		    abs(y - tr[1]) > tolerance or
		    abs(x + width - br[0]) > tolerance or
		    abs(y + height - br[1]) > tolerance or
		    abs(x - bl[0]) > tolerance or
		    abs(y + height - bl[1]) > tolerance
		   ):
			raise AssertionError("The found values differ too much from where the box should be.")
		return tl, tr, br, bl


class Questionnaire (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'recognize'
	obj_class = model.questionnaire.Questionnaire

	def recognize (self) :
		# recognize image
		try :
			self.obj.sheet.recognize.recognize()
		except RecognitionError :
			pass
		else :
			# iterate over qobjects
			for qobject in self.obj.qobjects :
				qobject.recognize.recognize()
		# clean up
		self.obj.sheet.recognize.clean()


class QObject (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'recognize'
	obj_class = model.questionnaire.QObject

	def recognize (self) :
		pass


class Question (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'recognize'
	obj_class = model.questionnaire.Question

	def recognize (self) :
		# iterate over boxes
		for box in self.obj.boxes :
			box.recognize.recognize()


#class Choice (Question) :

	#__metaclass__ = model.buddy.Register
	#name = 'recognize'
	#obj_class = model.questionnaire.Choice


#class Mark (Question) :

	#__metaclass__ = model.buddy.Register
	#name = 'recognize'
	#obj_class = model.questionnaire.Mark


class Box (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'recognize'
	obj_class = model.questionnaire.Box

	def recognize (self) :
		pass


class Checkbox (Box) :

	__metaclass__ = model.buddy.Register
	name = 'recognize'
	obj_class = model.questionnaire.Checkbox

	BORDER_WIDTH = 0.45

	def recognize (self) :
		image = self.obj.sheet.images[self.obj.page_number - 1]
		matrix = image.recognize.correction_matrix(
			self.obj.x, self.obj.y,
			self.obj.width, self.obj.height
		)
		x, y = matrix.transform_point(self.obj.x, self.obj.y)
		width, height = matrix.transform_distance(self.obj.width, self.obj.height)
		self.obj.data.x = x
		self.obj.data.y = y
		self.obj.data.width = width
		self.obj.data.height = height

		coverage = image.recognize.get_coverage(x - self.BORDER_WIDTH, y - self.BORDER_WIDTH, width + 2*self.BORDER_WIDTH, height + 2*self.BORDER_WIDTH)
		self.obj.data.coverage = coverage
		self.obj.data.state = 0.32 < coverage < 0.55


class Textbox (Box) :

	__metaclass__ = model.buddy.Register
	name = 'recognize'
	obj_class = model.questionnaire.Textbox

	def recognize (self) :
		class Quadrilateral():
			"""This class iterates through small box areas in a quadriliteral.
			This is usefull because some scanners have trapezoidal distortions."""
			# Assumes top left, top right, bottom right, bottom left
			# corner.
			def __init__(self, p0, p1, p2, p3):
				self.x0 = p0[0]
				self.y0 = p0[1]
				self.x1 = p1[0]
				self.y1 = p1[1]
				self.x2 = p2[0]
				self.y2 = p2[1]
				self.x3 = p3[0]
				self.y3 = p3[1]

				# 0 -> 1
				self.m0 = (self.y1 - self.y0) / (self.x1 - self.x0)
				self.m1 = (self.x2 - self.x1) / (self.y2 - self.y1)
				self.m2 = (self.y3 - self.y2) / (self.x3 - self.x2)
				self.m3 = (self.x0 - self.x3) / (self.y0 - self.y3)

				self.top = min(self.y0, self.y1)
				self.bottom = max(self.y2, self.y3)
				self.left = min(self.x0, self.x3)
				self.right = max(self.x1, self.x2)

			def iterate_bb(self, step_x, step_y, test_width, test_height, padding):
				y = self.top
				while y + test_height < self.bottom:
					x = self.left
					while x + test_width < self.right:
						yield x, y
						x += step_x

					y += step_y

			def iterate_outline(self, step_x, step_y, test_width, test_height, padding):
				x = self.left
				while x + test_width < self.right:
					y = self.y0 + self.m0 * (x - self.x0)
					yield x, y

					y = self.y2 + self.m2 * (x - self.x2)
					yield x, y

					x += step_x

				y = self.top
				while y + test_width < self.bottom:
					x = self.x1 + self.m1 * (y - self.y1)
					yield x, y

					x = self.x3 + self.m3 * (y - self.y3)
					yield x, y

					y += step_y



			def iterate_all(self, step_x, step_y, test_width, test_height, padding):
				for x, y in self.iterate_bb(step_x, step_y, test_width, test_height, padding):
					yield x, y
				for x, y in self.iterate_outline(step_x, step_y, test_width, test_height, padding):
					yield x, y

			def iterate(self, step_x, step_y, test_width, test_height, padding):
				for x, y in self.iterate_bb(step_x, step_y, test_width, test_height, padding):
					ly = self.y0 + self.m0 * (x - self.x0)
					if not ly + padding < y:
						continue

					ly = self.y2 + self.m2 * (x - self.x2)
					if not ly - padding > y + test_height:
						continue

					lx = self.x1 + self.m1 * (y - self.y1)
					if not lx - padding > x + test_width:
						continue

					lx = self.x3 + self.m3 * (y - self.y3)
					if not lx + padding < x:
						continue

					yield x, y

		bbox = None
		image = self.obj.sheet.images[self.obj.page_number - 1]

		x = self.obj.x
		y = self.obj.y
		width = self.obj.width
		height = self.obj.height

		# Always test a 2x2 mm area, so that every pixel is tested 4 times ...
		step_x = 1.0
		step_y = 1.0
		test_width = 2.0
		test_height = 2.0
		# extra_padding is always added to the box side at the end.
		# It should be large enough so that the bounding box is visible
		# if the user wrote outside the box
		extra_padding = 0.5
		scan_padding = 1.5

		quad = Quadrilateral((x, y), (x + width, y), (x + width, y + height), (x, y + height))
		try:
			quad = Quadrilateral(*image.recognize.find_box_corners(x, y, width, height))
			# Lower padding, as we found the corners and are therefore more acurate
			scan_padding = 0.3
		except AssertionError:
			print "Did not find corners."

		for x, y in quad.iterate(step_x, step_y, test_width, test_height, scan_padding):
			coverage = image.recognize.get_coverage(x, y, test_width, test_height)
			if coverage > 0.06:
				if not bbox:
					bbox = [x, y, test_width, test_height]
				else:
					bbox_x = min(bbox[0], x)
					bbox_y = min(bbox[1], y)
					bbox[2] = max(bbox[0] + bbox[2], x + test_width) - bbox_x
					bbox[3] = max(bbox[1] + bbox[3], y + test_height) - bbox_y
					bbox[0] = bbox_x
					bbox[1] = bbox_y

		if bbox and (bbox[2] > 7 or bbox[3] > 7) :
			# Do not accept very small bounding boxes.
			self.obj.data.state = True

			self.obj.data.x = bbox[0] - (scan_padding + extra_padding)
			self.obj.data.y = bbox[1] - (scan_padding + extra_padding)
			self.obj.data.width = bbox[2] + 2*(scan_padding + extra_padding)
			self.obj.data.height = bbox[3] + 2*(scan_padding + extra_padding)
		else:
			self.obj.data.state = False

			self.obj.data.x = self.obj.x
			self.obj.data.y = self.obj.y
			self.obj.data.width = self.obj.width
			self.obj.data.height = self.obj.height

