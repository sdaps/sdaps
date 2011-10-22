# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <christoph.simon@gmx.eu>
# Copyright (C) 2010, Benjamin Berg <benjamin@sipsolutions.net>
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

import re

from sdaps.setup.pdftools import pdffile
from sdaps.setup import buddies

from sdaps import model
from sdaps.ugettext import ugettext, ungettext
_ = ugettext


inch = 72.0 # pt (pdf unit)
cm = inch / 2.54
mm = cm * 0.1

# TODO Documentation for these values
# (min, max)
TEXTBOX_WIDTH = (6.0 * cm, 20.0 * cm)
TEXTBOX_HEIGHT = (0.8 * cm, 20.0 * cm)
CHECKBOX_SIZE = (3.4 * mm, 3.6 * mm)
LINE_SIZE = (0.0 * mm, 0.5 * mm)

class DummyBox (object) :
	def __init__(self, page, x, y, width, height):
		self.page = page
		self.x = x
		self.y = y
		self.width = width
		self.height = height

# Matches a checkbox in the PDF file (and might match other rectangles)
checkbox_regexp = re.compile(r'''
# Change the matrix to the top/left corner of the painting environment (the checkbox position)
1\s+ 0\s+ 0\s+ 1\s+ (?P<xpos>[0-9.]+)\s+ (?P<ypos>[0-9.]+)\s+ cm \s+
# Store the state, and set the fill/stroke color to black
q \s+
0 \s+ G \s+
0 \s+ g \s+
# Set the width, must be some setup code
[0-9.]+ \s+ w \s+
q \s+
q \s+
# Now to the actuall box. This is the stroke width
(?P<line_width>[0-9.]+) \s+ w \s+
# Move to point 0 (at least once)
(?:0\.0 \s+ 0\.0 \s+ m \s+)+
0.0 \s+ (?P<size>[0-9.]+) \s+ l \s+
(?P=size) \s+ (?P=size) \s+ l \s+
(?P=size) \s+ 0\.0 \s+ l \s+
# close the path
h \s+
# The cursor is moved to the bottom right of the box, depend on that for greater acuracy
(?P=size) \s+ (?P=size) \s+ m \s+
# Stroke the path
S \s+
# revert to old state
Q \s+
Q \s+
# Drop the path (useless, as no path is active)
n \s+
Q \s+
''', re.MULTILINE | re.VERBOSE)


textfield_vert_regexp = re.compile(r'''
q \s+
1 \s+ 0 \s+ 0 \s+ 1 \s+ (?P<x_out>[0-9.]+) \s+ (?P<y_top>[0-9.]+) \s+ cm \s+
\[\]0 \s+ d \s+ 0 \s+ J \s+ (?P<line_width>[0-9.]+) \s+ w \s+ 0 \s+ 0 \s+ m \s+ (?P<width>[0-9.]+) \s+ 0 \s+ l \s+ S \s+
Q \s+
q \s+
1 \s+ 0 \s+ 0 \s+ 1 \s+ (?P<x_left>[0-9.]+) \s+ (?P<y_line_bottom>[0-9.]+) \s+ cm \s+
\[\]0 \s+ d \s+ 0 \s+ J \s+ (?P=line_width) \s+ w \s+0 \s+ 0 \s+ m \s+ 0 \s+ (?P<line_length>[0-9.]+) \s+ l \s+ S \s+
Q \s+
q \s+
1 \s+ 0 \s+ 0 \s+ 1 \s+ (?P<x_right>[0-9.]+) \s+ (?P=y_line_bottom) \s+ cm \s+
\[\]0 \s+ d \s+ 0 \s+ J \s+ (?P=line_width) \s+ w \s+ 0 \s+ 0 \s+ m \s+ 0 \s+ (?P=line_length) \s+ l \s+ S \s+
Q \s+
# There can be multiple lines
(?:
  q \s+
  1 \s+ 0 \s+ 0 \s+ 1 \s+ (?P=x_left) \s+ (?P<y_line_top>[0-9.]+) \s+ cm \s+
  \[\]0 \s+ d \s+ 0 \s+ J \s+ (?P=line_width) \s+ w \s+ 0 \s+ 0 \s+ m \s+ 0 \s+ (?P=line_length) \s+ l \s+ S \s+
  Q \s+
  q \s+
  1 \s+ 0 \s+ 0 \s+ 1 \s+ (?P=x_right) \s+ (?P=y_line_top) \s+ cm \s+
  \[\]0 \s+ d \s+ 0 \s+ J \s+ (?P=line_width) \s+ w \s+ 0 \s+ 0 \s+ m \s+ 0 \s+ (?P=line_length) \s+ l \s+ S \s+
  Q \s+
)+
q \s+
1 \s+ 0 \s+ 0 \s+ 1 \s+ (?P=x_out) \s+ (?P<y_bottom>[0-9.]+) \s+ cm \s+
\[\]0 \s+ d \s+ 0 \s+ J \s+ (?P=line_width) \s+ w \s+ 0 \s+ 0 \s+ m \s+ (?P=width) \s+ 0 \s+ l \s+ S \s+
Q \s+
''', re.MULTILINE | re.VERBOSE)

textfield_horiz_regexp = re.compile(r'''
q \s+
1 \s+ 0 \s+ 0 \s+ 1 \s+ (?P<x_left>[0-9.]+) \s+ (?P<y_bottom>[0-9.]+) \s+ cm \s+
\[\]0 \s+ d \s+ 0 \s+ J \s+ (?P<line_width>[0-9.]+) \s+ w \s+ 0 \s+ 0 \s+ m \s+ 0 \s+ (?P<height>[0-9.]+) \s+ l \s+ S \s+
Q \s+
q \s+
1 \s+ 0 \s+ 0 \s+ 1 \s+ (?P<x_first_line>[0-9.]+) \s+ (?P<y_line_top>[0-9.]+) \s+ cm \s+
\[\]0 \s+ d \s+ 0 \s+ J \s+ (?P=line_width) \s+ w \s+0 \s+ 0 \s+ m \s+ (?P<line_length>[0-9.]+) \s+ 0 \s+ l \s+ S \s+
Q \s+
q \s+
1 \s+ 0 \s+ 0 \s+ 1 \s+ (?P=x_first_line) \s+ (?P<y_line_bottom>[0-9.]+) \s+ cm \s+
\[\]0 \s+ d \s+ 0 \s+ J \s+ (?P=line_width) \s+ w \s+0 \s+ 0 \s+ m \s+ (?P=line_length) \s+ 0 \s+ l \s+ S \s+
Q \s+
# There can be multiple lines
(?:
  q \s+
  1 \s+ 0 \s+ 0 \s+ 1 \s+ (?P<x_last_line>[0-9.]+) \s+ (?P=y_line_top) \s+ cm \s+
  \[\]0 \s+ d \s+ 0 \s+ J \s+ (?P=line_width) \s+ w \s+0 \s+ 0 \s+ m \s+ (?P=line_length) \s+ 0 \s+ l \s+ S \s+
  Q \s+
  q \s+
  1 \s+ 0 \s+ 0 \s+ 1 \s+ (?P=x_last_line) \s+ (?P=y_line_bottom) \s+ cm \s+
  \[\]0 \s+ d \s+ 0 \s+ J \s+ (?P=line_width) \s+ w \s+0 \s+ 0 \s+ m \s+ (?P=line_length) \s+ 0 \s+ l \s+ S \s+
  Q \s+
)+
q \s+
1 \s+ 0 \s+ 0 \s+ 1 \s+ (?P<x_right>[0-9.]+) \s+ (?P=y_bottom) \s+ cm \s+
\[\]0 \s+ d \s+ 0 \s+ J \s+ (?P=line_width) \s+ w \s+ 0 \s+ 0 \s+ m \s+ 0 \s+ (?P=height) \s+ l \s+ S \s+
Q \s+
''', re.MULTILINE | re.VERBOSE)

def parse (questionnaire_pdf) :

	doc = pdffile.PDFDocument(questionnaire_pdf)

	boxes = list()
	textboxes = list()

	page_count = doc.count_pages()
	assert page_count == 1 or page_count % 2 == 0

	for page_number in range(1, page_count + 1) :
		page = doc.read_page(page_number)
		contents = page.required["Contents"]

		page_width = page['MediaBox'][2]
		page_height = page['MediaBox'][3]

		x_old = 0
		y_old = 0

		matches = checkbox_regexp.finditer(contents)
		for match in matches:
			x = float(match.group('xpos'))
			y = float(match.group('ypos'))
			# Assume a relative position to the previous box
			# if the y coordinate is 0.
			if y == 0:
				x += x_old
				y += y_old
			line_width = float(match.group('line_width'))
			width = height = float(match.group('size')) + line_width
			if not (9.9213 < width <= 10):
				continue
			if line_width != 1.0:
				continue

			x -= line_width / 2.0
			y -= line_width / 2.0

			box = model.questionnaire.Checkbox()
			box.setup.setup(
				page_number,
				x / mm,
				# transform the coordinate origin from the lower left corner to the upper left corner
				# and name the upper left corner of the box, not the lower left one
				(page_height - y - height) / mm,
				width / mm,
				height / mm
			)
			boxes.append(box)

			x_old = x + line_width / 2.0
			y_old = y + line_width / 2.0

		matches = textfield_vert_regexp.finditer(contents)
		for match in matches:
			# Position is on the center of the line ...!
			x_out = float(match.group('x_out'))
			y = page_height - float(match.group('y_top'))
			height = float(match.group('y_top')) - float(match.group('y_bottom'))
			line_width = float(match.group('line_width'))
			width = float(match.group('width')) - line_width
			x = x_out + line_width / 2.0

			# Sanity checks
			if line_width != 1.0:
				continue
			x_left = float(match.group('x_left'))
			if (x - x_left) > 0.001:
				continue
			x_right = float(match.group('x_right'))
			if (x + width - x_right) > 0.001:
				continue
			line_length = float(match.group('line_length'))
			if line_length > height:
				continue

			# We only check whether the height seems correct ... not
			# that there are enough lines to draw a solid line on each side
			y_line_top = float(match.group('y_line_top'))
			y_line_bottom = float(match.group('y_line_bottom'))

			# I have seen values of ~0 and once slightly above 0.001
			if height - line_width - (line_length + y_line_bottom - y_line_top) > 0.002:
				continue
			box = model.questionnaire.Textbox()
			box.setup.setup(
				page_number,
				x / mm,
				# transform the coordinate origin from the lower left corner to the upper left corner
				# and name the upper left corner of the box, not the lower left one
				y / mm,
				width / mm,
				height / mm
			)
			textboxes.append(box)

		matches = textfield_horiz_regexp.finditer(contents)
		for match in matches:
			# Position is on the center of the line ...!
			x = float(match.group('x_left'))
			line_length = float(match.group('line_length'))
			width = float(match.group('x_last_line')) - float(match.group('x_first_line')) + line_length + line_width
			line_width = float(match.group('line_width'))
			height = float(match.group('height')) - line_width
			y = page_height - float(match.group('y_bottom')) - height
			y = y + line_width / 2.0

			# Sanity checks
			if line_width != 1.0:
				continue

			y_line_top = float(match.group('y_line_top'))
			y_line_bottom = float(match.group('y_line_bottom'))
			if abs(y_line_top - y_line_bottom - height) > 0.002:
				continue

			x_first_line = float(match.group('x_first_line'))
			if abs(x_first_line - (x + line_width / 2.0)) > 0.001:
				continue
			x_last_line = float(match.group('x_last_line'))
			if abs(x_last_line + line_length - (x + width - line_width / 2.0)) > 0.001:
				continue
			line_length = float(match.group('line_length'))
			if line_length > width:
				continue


			box = model.questionnaire.Textbox()
			box.setup.setup(
				page_number,
				x / mm,
				# transform the coordinate origin from the lower left corner to the upper left corner
				# and name the upper left corner of the box, not the lower left one
				y / mm,
				width / mm,
				height / mm
			)
			textboxes.append(box)

	# NO sorting. The order in the PDF will be the same as in the .sdaps file!
	## Sort by order of occurance
	#def sort_cmd(a, b):
	#	# does the height overlap?
	#	if a.page_number != b.page_number:
	#		return a.page_number - b.page_number
	#	if a.y >= b.y and a.y <= b.y + b.height or \
	#	   b.y >= a.y and b.y <= a.y + a.height:
	#		if a.x - b.x > 0:
	#			return 1
	#		else:
	#			return -1
	#	if a.y - b.y > 0:
	#		return 1
	#	else:
	#		return -1
	#boxes.sort(sort_cmd)

	return boxes, textboxes, page_count


 
