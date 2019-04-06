# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2012, Benjamin Berg <benjamin@sipsolutions.net>
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
This module contains helpers to read barcodes from cairo A1 surfaces.
"""

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

import os
import tempfile
import cairo
import subprocess
from sdaps import image
from sdaps import defs


def read_barcode(surface, matrix, x, y, width, height, btype="CODE128"):
    """Tries to read the barcode at the given position"""
    result = scan(surface, matrix, x, y, width, height, btype)

    if result == None:
      # Try kfill approach
      result = scan(surface, matrix, x, y, width, height, btype, True)

    return result

def scan(surface, matrix, x, y, width, height, btype="CODE128", kfill=False):
    x0, y0 = matrix.transform_point(x, y)
    x1, y1 = matrix.transform_point(x + width, y + height)

    # Bounding box ...
    x = min(x0, x1)
    y = min(y0, y1)
    width = max(x0, x1) - x
    height = max(y0, y1) - y

    x, y, width, height = int(x), int(y), int(width), int(height)
    # Round the width to multiple of 4 pixel, so that the stride will
    # be good ... hopefully
    width = width - width % 4 + 4

    # a1 surface for kfill algorithm
    a1_surface = cairo.ImageSurface(cairo.FORMAT_A1, width, height)

    cr = cairo.Context(a1_surface)
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.set_source_surface(surface, -x, -y)
    cr.paint()

    if kfill:
        pxpermm = (matrix[0] + matrix[3]) / 2
        barwidth = pxpermm * defs.code128_barwidth
        barwidth = int(round(barwidth))

        if barwidth <= 3:
            return

        if barwidth > 6:
            barwidth = 6

        image.kfill_modified(a1_surface, barwidth)

    pbm = image.get_pbm(a1_surface)
    tmp = tempfile.mktemp(suffix='.png', prefix='sdaps-zbar-')
    f = open(tmp, 'wb')
    f.write(pbm)
    f.close()

    # Is the /dev/stdin sufficiently portable?
    proc = subprocess.Popen(['zbarimg', '-q', '-Sdisable', '-S%s.enable' % btype.lower(), tmp], stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    os.unlink(tmp)

    # The following can be used to look at the images
    #rgb_surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
    #cr = cairo.Context(rgb_surface)
    #cr.set_operator(cairo.OPERATOR_SOURCE)
    #cr.set_source_rgba(1, 1, 1, 1)
    #cr.paint()
    #cr.set_operator(cairo.OPERATOR_OVER)
    #cr.set_source_rgba(0, 0, 0, 1)
    #cr.mask_surface(a1_surface)
    #global b_count
    #rgb_surface.write_to_png("/tmp/barcode-%03i.png" % b_count)
    #b_count += 1

    if proc.returncode == 4:
        return None

    assert(proc.returncode == 0)
    barcode = stdout.split(b'\n')[0]
    assert barcode.split(b':', 1)[0].replace(b'-', b'').lower() == btype.lower().encode('ascii')

    return barcode.split(b':', 1)[1].decode('utf-8')

#b_count = 0
