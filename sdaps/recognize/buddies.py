# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <christoph.simon@gmx.eu>
# Copyright (C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
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

		if self.obj.page_number % 2 == 0 :
			# read ids
			self.obj.sheet.survey_id = self.read_codebox(
				defs.survey_id_msb_x,
				defs.survey_id_msb_y,
			)
			self.obj.sheet.survey_id = self.read_codebox(
				defs.survey_id_lsb_x,
				defs.survey_id_lsb_y,
				self.obj.sheet.survey_id
			)
			if not self.obj.sheet.survey_id == self.obj.sheet.survey.survey_id :
				print _('%s: Wrong survey_id. Cancelling recognition of that image.') % self.obj.filename
				raise RecognitionError
			self.obj.sheet.questionnaire_id = self.read_codebox(
				defs.questionnaire_id_lsb_x,
				defs.questionnaire_id_lsb_y,
			)

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
		bbox = None
		image = self.obj.sheet.images[self.obj.page_number - 1]

		x = self.obj.x
		y = self.obj.y
		width = self.obj.width
		height = self.obj.height

		# Always test a 2x2 mm area, so that every pixel is tested 4 times ...
		test_width = 2.0
		test_height = 2.0
		padding = 1.0

		steps_x = int(width)
		steps_y = int(height)

		# Test the inner part, leaving out the edge around the box.
		x_start = x + padding
		y_start = y + padding

		step_x = width / float(steps_x)
		step_y = height / float(steps_y)

		x_end = width + x_start - test_width - 2 * padding
		y_end = height + y_start - test_width - 2 * padding

		x = x_start
		while x <= x_end:
			y = y_start
			while y <= y_end:
				coverage = image.recognize.get_coverage(x, y, test_width, test_height)
				if coverage > 0.06:
					if not bbox:
						bbox = [x, y, test_width, test_height]
					else:
						bbox_x = min(bbox[0], x)
						bbox_y = min(bbox[1], y)
						bbox[2] = max(bbox[0] + bbox[2], x + 2.0) - bbox_x
						bbox[3] = max(bbox[1] + bbox[3], y + 2.0) - bbox_y
						bbox[0] = bbox_x
						bbox[1] = bbox_y

				y += step_y
			x += step_x

		if bbox and (bbox[2] > 7 or bbox[3] > 7) :
			# Do not accept very small bounding boxes.
			self.obj.data.state = True

			self.obj.data.x = bbox[0] - 1.0
			self.obj.data.y = bbox[1] - 1.0
			self.obj.data.width = bbox[2] + 2.0
			self.obj.data.height = bbox[3] + 2.0
		else:
			self.obj.data.state = False

			self.obj.data.x = self.obj.x
			self.obj.data.y = self.obj.y
			self.obj.data.width = self.obj.width
			self.obj.data.height = self.obj.height

