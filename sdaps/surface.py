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

u"""
The surface module adds support for loading the scanned images. It adds a buddy
to the model.sheet.Image and provides the surface via
model.sheet.Image.surface.surface at runtime.
"""

import model
import image


class Image (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'surface'
	obj_class = model.sheet.Image

	def load (self) :
		self.surface = image.get_a1_from_tiff(
			self.obj.sheet.survey.path(self.obj.filename),
			self.obj.rotated
		)

	def clean (self) :
		if hasattr(self, 'surface') : del self.surface

