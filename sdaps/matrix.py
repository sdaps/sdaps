# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
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
The matrix module adds support to find out the rotation matrix for a scanned
page. After loading the(cairo) matrixes can be accessed via two functions:

  model.sheet.Image.matrix.mm_to_px() and
  model.sheet.Image.matrix.px_to_mm()

The return value of mm_to_px() can be used to convert milimeter values to pixel
on the scanned page. px_to_mm() returns the inverse matrix to convert on page
pixels to milimiter values of the original document.

Warning: The correct values are only available after "recognize" has been run!
"""

import cairo

import model
import surface


class Image(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    name = 'matrix'
    obj_class = model.sheet.Image

    def mm_to_px(self, fallback=True):
        matrix = self.px_to_mm(fallback)
        if matrix is not None:
            matrix.invert()
        return matrix

    def px_to_mm(self, fallback=True):
        if self.obj.raw_matrix is not None:
            return cairo.Matrix(*self.obj.raw_matrix)
        elif fallback:
            # Return a dummy matrix ... that maps the image to the page size
            surface = self.obj.surface.load_uncached()

            width = surface.get_width()
            height = surface.get_height()

            matrix = cairo.Matrix()

            matrix.scale(1.0 / width, 1.0 / height)
            matrix.scale(self.obj.sheet.survey.defs.paper_width, self.obj.sheet.survey.defs.paper_height)

            return matrix
        else:
            return None

    def matrix_valid(self):
        return self.obj.raw_matrix != None

    def set_px_to_mm(self, matrix):
        if matrix is not None:
            self.obj.raw_matrix = tuple(matrix)
        else:
            self.obj.raw_matrix = None

class Test(object):
    test = Image

