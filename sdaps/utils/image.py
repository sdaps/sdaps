# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008, 2011, 2014, Benjamin Berg <benjamin@sipsolutions.net>
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

# Ensure the matrix buddy is loaded
from sdaps import matrix

from sdaps import image

import cairo
import math

import os
import os.path

def get_box_surface(box, format=cairo.FORMAT_RGB24):
    img = box.sheet.get_page_image(box.question.page_number)

    filename = box.question.questionnaire.survey.path(img.filename)

    mm_to_px = img.matrix.mm_to_px()
    x0, y0 = mm_to_px.transform_point(box.data.x, box.data.y)
    x1, y1 = mm_to_px.transform_point(box.data.x + box.data.width, box.data.y)
    x2, y2 = mm_to_px.transform_point(box.data.x, box.data.y + box.data.height)
    x3, y3 = mm_to_px.transform_point(box.data.x + box.data.width, box.data.y + box.data.height)

    x = int(min(x0, x1, x2, x3))
    y = int(min(y0, y1, y2, y3))
    width = int(math.ceil(max(x0, x1, x2, x3) - x))
    height = int(math.ceil(max(y0, y1, y2, y3) - y))

    img = image.get_a1_from_tiff(filename, img.tiff_page, img.rotated if img.rotated else False)

    # Not sure if this is correct for A1 ... probably not
    assert(format == cairo.FORMAT_RGB24)
    surf = cairo.ImageSurface(format, width, height)
    cr = cairo.Context(surf)
    cr.set_source_rgb(1, 1, 1)
    cr.paint()

    cr.set_source_surface(img, -x, -y)
    cr.paint()

    return surf

class ImageWriter:
    def __init__(self, path, prefix):
        # I am not qutie sure whether I like the params here.
        self.count = 0
        self.path = path
        self.prefix = prefix

        # Create directory if it does not exists. Assumes only one level
        # is missing.
        # In case the prefix contains further path components
        real_path = os.path.dirname(os.path.join(self.path, self.prefix))
        if not os.path.exists(real_path):
            os.mkdir(real_path)

    def output_box(self, box):
        surf = get_box_surface(box)

        filename = "%s%04d.png" % (self.prefix, self.count)
        full_path = os.path.join(self.path, filename)

        surf.write_to_png(full_path)

        self.count += 1

        return filename


