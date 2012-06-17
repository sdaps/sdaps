# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <post@christoph-simon.eu>
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

import buddy


class Sheet (buddy.Object) :
	
	def __init__ (self) :
		self.survey = None
		self.data = dict()
		self.images = list()
		self.survey_id = 0
		self.questionnaire_id = 0
		self.valid = 1
		self.quality = 1
	
	def add_image (self, image) :
		self.images.append(image)
		image.sheet = self


class Image (buddy.Object) :
	
	def __init__ (self) :
		self.sheet = None
		self.filename = str()
		self.tiff_page = 0
		self.rotated = 0
		self.raw_matrix = (0.0833, 0, 0, 0.0833, 0, 0)
		self.page_number = 1

