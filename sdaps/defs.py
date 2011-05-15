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
Defs
====

This module contains constants and some magic values.
"""


corner_mark_left = 10.0 # mm
corner_mark_right = 10.0 # mm
corner_mark_top = 12.0 # mm
corner_mark_bottom = 12.0 # mm
corner_mark_length = 20.0 # mm

# top left, top right, bottom left, bottom right
corner_boxes = [
	[0, 1, 1, 1],
	[1, 1, 0, 0],
	[1, 0, 1, 1],
	[1, 0, 1, 0],
	[1, 0, 0, 0],
	[0, 0, 0, 1],
]

corner_box_width = 3.5 # mm
corner_box_height = 3.5 # mm
corner_box_padding = 3 # mm

codebox_length = 16 # bits
codebox_step = 3.5 # mm
codebox_width = codebox_step * codebox_length # mm
codebox_height = 3.5 # mm
# Padding that is ignored when testing the image whether it is 1/0
codebox_offset = 0.75 # mm

# The font and size of the font for the text that is printed between the codeboxes
codebox_text_font = 'Courier-Bold'
codebox_text_font_size = 10.5
# This is added to the vertical position to shift the text visually into the center
codebox_text_baseline_shift = 3

# Magic values for recognition
# The coverage above which a codebox is considered to be a logical 1
codebox_on_coverage = 0.7

# The coverage above which a cornerbox is considered to be a logical 1
cornerbox_on_coverage = 0.7

# Tolerance for the text box corner adjustment. If the difference is more than
# this in mm, the adjusted values will be discarded.
find_box_corners_tolerance = 1.5

# This is the size in mm that the checkbox will be increased for the coverage check
checkbox_border_width = 0.45
# The coverage above which a checkbox is considered to be checked
checkbox_checked_coverage = 0.32
# The coverage above a checkbox is considered to be corrected (ie. not checked)
checkbox_corrected_coverage = 0.55

# The size in mm of the area that is scanned during checking of textboxes. The step
# is the x/y distance in mm of each checked area. They overlap on purpose.
textbox_scan_step_x = 1.0
textbox_scan_step_y = 1.0
textbox_scan_width = 2.0
textbox_scan_height = 2.0

# The pixel coverage of the scan area that is required for it to
# be considered writing.
textbox_scan_coverage = 0.06

# Minimum size in mm for a textbox to be considered filled in.
# This is usefull because otherwise small dirt dots will be considered writing.
textbox_minimum_writing_width = 7
textbox_minimum_writing_height = 7

# Distance to stay away from the outline in mm so that it will not be detected
# as handwriting. The "uncorrected" value is used when the corners have not been
# detected correctly, which should hopefully never happen.
textbox_scan_padding = 0.3
textbox_scan_uncorrected_padding = 1.5

# Padding tha will always be added to the textbox size if content has been recognized.
# This is important because we want the outline to be visible if someone wrote
# over the outline (so that the reader can see that the software worked correctly).
textbox_extra_padding = 0.5

# The following values are used when working on the pixel data of the scanned images.
# The corner_mark min/max length are the minium/maximum lenght in *pixel* that the
# lines of the corner marks may have.
image_corner_mark_min_length = 215
image_corner_mark_max_length = 250
# The width of the corner mark and textbox lines in pixel in the scanned image.
image_line_width = 5
# The coverage that the line needs to have for recognition
image_line_coverage = 0.65



