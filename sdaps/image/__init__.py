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
This modules contains low level image processing functions. These functions
are implemented in C for speed reasons. Usually one will not need to use these
directly, instead modules like "recognize" or "surface" use them to load and
analyze the image data.
"""

import os
import sys
import cairo

from sdaps import paths
from sdaps import defs
from sdaps import log

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

if paths.local_run:
    # image.so liegt in lib_build_dir/image/
    __path__.append(os.path.join(paths.lib_build_dir, 'image'))

# If SDAPS is installed, then the image.so file is in the current directory.
# Simply importing it without changes to the paths will work.

try:
    from .image import *
except ImportError as e:
    print(e)
    log.error(_("It appears you have not build the C extension. Please run \"./setup.py build\" in the toplevel directory."))
    sys.exit(1)

set_magic_values(defs.corner_mark_min_length,
                 defs.corner_mark_max_length,
                 defs.image_line_width,
                 defs.corner_mark_search_distance,
                 defs.image_line_coverage)

# Offset into corners, not valid for C API which has +1 as offset!
TOP_LEFT = 0
TOP_RIGHT = 1
BOTTOM_RIGHT = 2
BOTTOM_LEFT = 3

def calculate_matrix(surface, matrix, mm_x, mm_y, mm_width, mm_height):
    """Detect the transformation matrix

    This runs a detection for the corner marks that denote the bounding box
    given by mm_x, mm_y, mm_width, mm_height in the surface. The passed matrix
    is used for to estimate the resolution of the image.

    This function returns a new cairo matrix or raises an error otherwise.
    """
    found_corners = 0

    corners = []

    for i in (1, 2, 3, 4):
        try:
            corners.append(find_corner_marker (surface, matrix, i))
            found_corners += 1
        except:
            corners.append(None)

    # We need at least 3 corners to do anything
    assert found_corners >= 3

    return matrix_from_corners_2d(corners, mm_x, mm_y, mm_width, mm_height)


def matrix_from_corners_2d(corners, mm_x, mm_y, mm_width, mm_height):
    """Calculate the transformation matrix from bounding box corners

    Given the list of corners in the order top left, top right, bottom right,
    bottom left in px space and the bounding box that is defined by these
    corners in mm space, calcualte the corresponding px to mm transformation
    matrix.

    This function returns a new cairo matrix or raises an error otherwise.
    """

    assert len(corners) == 4
    assert corners.count(None) <= 1

    # Calculate a new "perfect" location for the undefined corner
    if corners[TOP_LEFT] is None:
        corners[TOP_LEFT] = (
                corners[BOTTOM_LEFT][0] - corners[BOTTOM_RIGHT][0] + corners[TOP_RIGHT][0],
                corners[TOP_RIGHT][1] - corners[BOTTOM_RIGHT][1] + corners[BOTTOM_LEFT][1]
            )
    if corners[TOP_RIGHT] is None:
        corners[TOP_RIGHT] = (
                corners[BOTTOM_RIGHT][0] - corners[BOTTOM_LEFT][0] + corners[TOP_LEFT][0],
                corners[TOP_LEFT][1] - corners[BOTTOM_LEFT][1] + corners[BOTTOM_RIGHT][1]
            )
    if corners[BOTTOM_LEFT] is None:
        corners[BOTTOM_LEFT] = (
                corners[TOP_LEFT][0] - corners[TOP_RIGHT][0] + corners[BOTTOM_RIGHT][0],
                corners[BOTTOM_RIGHT][1] - corners[TOP_RIGHT][1] + corners[TOP_LEFT][1]
            )
    if corners[BOTTOM_RIGHT] is None:
        corners[BOTTOM_RIGHT] = (
                corners[TOP_RIGHT][0] - corners[TOP_LEFT][0] + corners[BOTTOM_LEFT][0],
                corners[BOTTOM_LEFT][1] - corners[TOP_LEFT][1] + corners[TOP_RIGHT][1]
            )

    # X-Axis
    dx = ((corners[TOP_RIGHT][0] - corners[TOP_LEFT][0]) + (corners[BOTTOM_RIGHT][0] - corners[BOTTOM_LEFT][0])) / 2
    dy = ((corners[TOP_RIGHT][1] - corners[TOP_LEFT][1]) + (corners[BOTTOM_RIGHT][1] - corners[BOTTOM_LEFT][1])) / 2

    xx = dx / mm_width
    yx = dy / mm_width

    # y-Axis
    dx = ((corners[BOTTOM_RIGHT][0] - corners[TOP_RIGHT][0]) + (corners[BOTTOM_LEFT][0] - corners[TOP_LEFT][0])) / 2
    dy = ((corners[BOTTOM_RIGHT][1] - corners[TOP_RIGHT][1]) + (corners[BOTTOM_LEFT][1] - corners[TOP_LEFT][1])) / 2

    xy = dx / mm_height
    yy = dy / mm_height

    # Center everything between the markers
    x0 = (corners[BOTTOM_LEFT][0] + corners[BOTTOM_RIGHT][0] + corners[TOP_LEFT][0] + corners[TOP_RIGHT][0]) / 4
    y0 = (corners[BOTTOM_LEFT][1] + corners[BOTTOM_RIGHT][1] + corners[TOP_LEFT][1] + corners[TOP_RIGHT][1]) / 4

    x_center = mm_width / 2 + mm_x
    y_center = mm_height / 2 + mm_y

    dx = x_center * xx + y_center * xy
    dy = x_center * yx + y_center * yy

    x0 -= dx
    y0 -= dy

    m_new = cairo.Matrix(xx, yx, xy, yy, x0, y0)
    m_new.invert()

    return m_new
