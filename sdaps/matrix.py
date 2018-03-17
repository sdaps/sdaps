# -*- coding: utf-8 -*-
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

"""
The matrix module adds support to find out rotation matrix for a scanned
page. After loading this module you can access the transformation matrices
(cairo.Martrix instances) via two functions:

  :py:meth:`model.sheet.Image.matrix.mm_to_px` and
  :py:meth:`model.sheet.Image.matrix.px_to_mm`

The return value of :py:meth:`mm_to_px` can be used to convert millimeter
values to pixel on the scanned page. :py:meth:`px_to_mm` returns the inverse
matrix to convert on page pixels to millimeter values of the original document.

Both the millimeter and pixel spaces start at the top left corner of the page.

Warning: The correct values are only available after "recognize" has been run!
"""

import cairo

from sdaps import model
from sdaps import surface
from sdaps import image


class Image(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'matrix'
    obj_class = model.sheet.Image

    def mm_to_px(self, fallback=True):
        """Return the matrix to convert mm to pixel space. If no matrix
        information is available and `fallback` is set to `True` then a matrix
        will be calculated from the size of the image."""
        matrix = self.px_to_mm(fallback)
        if matrix is not None:
            matrix.invert()
        return matrix

    def px_to_mm(self, fallback=True):
        """Return the matrix to convert pixel to mm space. If no matrix
        information is available and `fallback` is set to `True` then a matrix
        will be calculated from the size of the image."""
        if self.obj.raw_matrix is not None:
            return cairo.Matrix(*self.obj.raw_matrix)
        elif fallback:
            # Return a dummy matrix ... that maps the image to the page size
            width, height = self.obj.surface.get_size()
            xres, yres = image.get_tiff_resolution(
                self.obj.sheet.survey.path(self.obj.filename),
                self.obj.tiff_page)

            if xres == 0 or yres == 0:
                xres = width / self.obj.sheet.survey.defs.paper_width
                yres = height / self.obj.sheet.survey.defs.paper_height

            scan_width = width / xres
            scan_height = height / yres

            dx = (self.obj.sheet.survey.defs.paper_width - scan_width) / 2.0
            dy = (self.obj.sheet.survey.defs.paper_height - scan_height) / 2.0

            matrix = cairo.Matrix()

            # Center the image
            matrix.translate(dx, dy)
            matrix.scale(1.0 / xres, 1.0 / yres)

            return matrix
        else:
            return None

    def matrix_valid(self):
        """Checks whether the proper transformation matrix is known."""
        return self.obj.raw_matrix != None

    def set_px_to_mm(self, matrix):
        """Set the stored matrix for the image. You need to pass in the pixel
        to mm space conversion matrix. Unsetting can be done by passing `None`.
        """
        if matrix is not None:
            self.obj.raw_matrix = tuple(matrix)
        else:
            self.obj.raw_matrix = None

