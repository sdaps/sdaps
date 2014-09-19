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
Defs
====

This module contains constants and some magic values.
"""


# Corner Marks ============================================

# The position of the corner markings from the side of the paper
corner_mark_left = 10.0 # mm
corner_mark_right = 10.0 # mm
corner_mark_top = 12.0 # mm
corner_mark_bottom = 12.0 # mm
corner_mark_length = 20.0 # mm

# Length in mm of the corner marks in the scanned image
corner_mark_min_length = 15 # mm
corner_mark_max_length = 22 # mm

# The distance into the image that will be searched for the corner mark.
# Basically a square area of this size will be searched in each corner.
corner_mark_search_distance = 50 # mm

# Corner Boxes ============================================

# What corners are filled for each page, this is choosen so that
# the page number and rotation can be derived from the information.
# Order: top left, top right, bottom left, bottom right
corner_boxes = [
    [0, 1, 1, 1],
    [1, 1, 0, 0],
    [1, 0, 1, 1],
    [1, 0, 1, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 1],
]

# Size of the corner boxes(measured from the center of the line)
corner_box_width = 3.5 # mm
corner_box_height = 3.5 # mm
# Distance from the corner marker(and also the distance to the codebox)
corner_box_padding = 3 # mm

# The coverage above which a cornerbox is considered to be a logical 1
cornerbox_on_coverage = 0.6


# Codebox =================================================

# Length in bits
codebox_length = 16 # bits
codebox_step = 3.5 # mm
codebox_width = codebox_step * codebox_length # mm
codebox_height = 3.5 # mm
# Padding that is ignored when testing the image whether it is 1/0
codebox_offset = 0.75 # mm

# The font and size of the font for the text that is printed between the codeboxes
codebox_text_font = 'Courier-Bold'
codebox_text_font_size = 10.5 # pt
# This is added to the vertical position to shift the text visually into the center
codebox_text_baseline_shift = 3 # mm

# Magic values for recognition
# The coverage above which a codebox is considered to be a logical 1
codebox_on_coverage = 0.7

# Code 128 Barcodes =======================================

code128_barwidth = 0.33 # mm. This is 0.93pt or 3.89px after scanning
code128_height = 6.5 # pt(5 mm)
code128_hpad = 6.5 # mm
code128_vpad = 4.02 # mm

code128_text_font = 'Courier'
code128_text_font_size = 9 # pt

# Checkbox ================================================

checkbox_metrics = {}

# The metrics is a mapping from the value to the quality and expected
# checkbox state.
# It works by searching the interval that we are in, and doing
# a linear interpolation.
# At state changes the point should be inserted twice.
# The touple is(metric, state, quality). To disable one you can just
# insert two dummy points with zero quality. To try and find better
# values have a look at the output of "boxgallery". Any suggestions
# for improvements(also algorithmic wise) are always welcome!
checkbox_metrics['coverage'] = \
    [(0, 0, 1.0), (0.02, 0, 0.9), (0.05, 0, 0.3), (0.05, 1, 0.3),
     (0.1, 1, 1.0), (0.4, 1, 1.0), (0.5, 1, 0.2), (0.5, 0, 0.2),
     (0.7, 0, 0.3), (1.0, 0, 0.6)]
checkbox_metrics['cov-lines-removed'] = \
    [(0, 1, 0), (0.01, 1, 0), (0.07, 1, 1.0), (0.10, 1, 1.0),
     (0.13, 1, 0.3), (0.13, 0, 0.3), (0.25, 0, 0.7), (1, 0, 0.7)]
checkbox_metrics['cov-min-size'] = \
    [(0, 0, .9), (0.35, 0, 0.0), (0.35, 1, 0.0), (0.5, 1, 0.9),
     (0.55, 1, 1.0), (0.8, 1, 1.0), (0.9, 1, 0.9), (0.95, 1, 0.5),
     (0.95, 0, 0.5), (0.99, 0, 0.9), (1.0, 0, 1.0)]

# Textbox =================================================

# Tolerance for the text box corner adjustment. If the difference is more than
# this in mm, the adjusted values will be discarded.
find_box_corners_tolerance = 1.5 # mm

# The size in mm of the area that is scanned during checking of textboxes. The step
# is the x/y distance in mm of each checked area. They overlap on purpose.
textbox_scan_step_x = 1.0 # mm
textbox_scan_step_y = 1.0 # mm
textbox_scan_width = 2.0 # mm
textbox_scan_height = 2.0 # mm

# The pixel coverage of the scan area that is required for it to
# be considered writing.
textbox_scan_coverage = 0.06

# Minimum size in mm for a textbox to be considered filled in.
# This is usefull because otherwise small dirt dots will be considered writing.
textbox_minimum_writing_width = 5 # mm
textbox_minimum_writing_height = 5 # mm

# Distance to stay away from the outline in mm so that it will not be detected
# as handwriting. The "uncorrected" value is used when the corners have not been
# detected correctly, which should hopefully never happen.
textbox_scan_padding = 0.5 # mm
textbox_scan_uncorrected_padding = 1.5 # mm

# Padding tha will always be added to the textbox size if content has been recognized.
# This is important because we want the outline to be visible if someone wrote
# over the outline(so that the reader can see that the software worked correctly).
textbox_extra_padding = 0.5 # mm


# Image ===================================================

# The width of the lines in the scanned image.
# All lines are 1pt wide(1/72 inch or 25.4/72 mm)
image_line_width = 24.4/72. # mm
# The coverage that the line needs to have for recognition
image_line_coverage = 0.35


# Allowed characters in code 128 barcodes (only ascii for now)
c128_chars = [chr(i) for i in xrange(32, 127)] #+ [u'È', u'É', u'Ê', u'Ë', u'Ì', u'Í', u'Î', u'Ï', u'Ð', u'Ñ', u'Ò', u'Ó']


# External commands =======================================
#: The binary used to compile latex documents.
latex_engine = "pdflatex"
