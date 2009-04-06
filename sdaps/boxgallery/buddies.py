# -*- coding: utf8 -*-
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

from sdaps import model
from sdaps import surface
from sdaps import matrix
import cairo

class Sheet (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'boxgallery'
	obj_class = model.sheet.Sheet

	def load (self) :
		for image in self.obj.images :
			image.surface.load()

	def clean (self) :
		for image in self.obj.images :
			image.surface.clean()


class Questionnaire (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'boxgallery'
	obj_class = model.questionnaire.Questionnaire
	
	def init (self) :
		self.checkboxes = list()

	def clean (self) :
		del self.checkboxes

	def get_checkbox_images (self) :
		self.obj.survey.sheet.boxgallery.load()
		for qobject in self.obj.qobjects:
			self.checkboxes.extend(qobject.boxgallery.get_checkbox_images())
		self.obj.survey.sheet.boxgallery.clean()


class QObject (model.buddy.Buddy) :
	
	__metaclass__ = model.buddy.Register
	name = 'boxgallery'
	obj_class = model.questionnaire.QObject
	
	def get_checkbox_images (self) :
		return []

class Question (QObject) :
	
	__metaclass__ = model.buddy.Register
	name = 'boxgallery'
	obj_class = model.questionnaire.Question
	
	def get_checkbox_images (self) :
		boxes = []

		for box in self.obj.boxes:
			new_box = box.boxgallery.get_checkbox_image()
			if new_box:
				boxes.append(new_box)
		return boxes
		
class Box (model.buddy.Buddy):
	__metaclass__ = model.buddy.Register
	name = 'boxgallery'
	obj_class = model.questionnaire.Box

	def get_checkbox_image (self):
		return None


class Checkbox (model.buddy.Buddy):
	__metaclass__ = model.buddy.Register
	name = 'boxgallery'
	obj_class = model.questionnaire.Checkbox

	def get_checkbox_image (self):
		image = self.obj.sheet.images[self.obj.page_number - 1]
		
		border = 1.5
		mm_to_px = image.matrix.mm_to_px()

		px_x, px_y = mm_to_px.transform_point(self.obj.data.x - border, self.obj.data.y - border)
		px_width, px_height = mm_to_px.transform_distance(self.obj.data.width + 2*border, self.obj.data.height + 2*border)

		dest = cairo.ImageSurface(cairo.FORMAT_RGB24, int(px_width), int(px_height))
		src = image.surface.surface
		
		cr = cairo.Context(dest)
		cr.set_source_rgb(1, 1, 1)
		cr.paint()
		
		cr.set_source_rgb(0, 0, 0)
		cr.mask_surface(src, -px_x, -px_y)
		
		return (self.obj.data.coverage, dest)



