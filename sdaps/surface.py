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
The surface module adds support for loading the scanned images. It adds a buddy
to the model.sheet.Image and provides the surface via
model.sheet.Image.surface.surface at runtime.
"""

from . import model
from . import image


class Image(model.buddy.Buddy, metaclass=model.buddy.Register):
    """
    Buddy to load and cache image data. Do not forget to call :py:meth:`clean`
    when you are done (ie. before moving to the next sheet) or else the
    surface will be cached indefinately.

    :ivar surface: The cairo A1 surface, after it has been loaded using :py:meth:`load`.
    :ivar surface_rgb: The cairo RGB24 surface, after it has been loaded using :py:meth:`load_rgb`.
    """
    name = 'surface'
    obj_class = model.sheet.Image

    def load(self):
        """Load the A1 cairo surface, which is accessible using the surface
        attribute.
        :py:meth`clean` needs to be called when the surface is
        no longer needed."""
        self.surface = image.get_a1_from_tiff(
            self.obj.sheet.survey.path(self.obj.filename),
            self.obj.tiff_page,
            True if self.obj.rotated else False
        )

    def load_rgb(self):
        """Load the RGB24 cairo surface, which is accessible using the
        surface_rgb attribute.
        :py:meth:`clean` needs to be called when the surface is
        no longer needed."""
        self.surface_rgb = image.get_rgb24_from_tiff(
            self.obj.sheet.survey.path(self.obj.filename),
            self.obj.tiff_page,
            True if self.obj.rotated else False
        )

    def load_uncached(self):
        """Load the A1 surface and directly return it. It will not be cached,
        so using this function may result repeated reloads from file."""
        if hasattr(self, 'surface'):
            return self.surface
        else:
            return image.get_a1_from_tiff(
                self.obj.sheet.survey.path(self.obj.filename),
                self.obj.tiff_page,
                True if self.obj.rotated else False)

    def get_size(self):
        """Read the size of the surface. If the surface is already loaded, it
        will read the size from that. If it is not loaded, an uncached load will
        be done, which may be rather slow."""
        # Load uncached does not check the rgb surface
        if hasattr(self, 'surface_rgb'):
            s = self.surface_rgb
        else:
            s = self.load_uncached()
        return s.get_width(), s.get_height()

    def clean(self):
        """Call when you are done handling a specific sheet to free any cached
        cairo surface."""
        if hasattr(self, 'surface'):
            del self.surface
        if hasattr(self, 'surface_rgb'):
            del self.surface_rgb

