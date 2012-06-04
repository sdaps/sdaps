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

from pdftools import *

from sdaps import model
from sdaps.ugettext import ugettext, ungettext
_ = ugettext


inch = 72.0 # pt (pdf unit)
cm = inch / 2.54
mm = cm * 0.1

# TODO Documentation for these values
# (min, max)
TEXTBOX_WIDTH = (6.0 * cm, 20.0 * cm)
TEXTBOX_HEIGHT = (0.6 * cm, 20.0 * cm)
CHECKBOX_SIZE = (3.4 * mm, 3.6 * mm)
LINE_SIZE = (0.0 * mm, 0.5 * mm)

class DummyBox (object) :
	def __init__(self, page, x, y, width, height):
		self.page = page
		self.x = x
		self.y = y
		self.width = width
		self.height = height

def parse (questionnaire_pdf) :

	doc = pdffile.PDFDocument(questionnaire_pdf)
	
	boxes = list()
	
	page_count = doc.count_pages()
	assert page_count == 1 or page_count % 2 == 0
	
	for page_number in range(1, page_count + 1) :
		page = doc.read_page(page_number)
		contents = page.read_contents()
		box = None
		box_linecount = 0
		# width and height are in pt!
		# TODO Test if its A4...
		width = page['MediaBox'][2]
		height = page['MediaBox'][3]
		for obj in contents.contents :
			if isinstance(obj, pdfpath.Path) and obj.painting :
				# only analyse painting paths. Ignore clipping paths
				# in fact, the subpath contains all information
				if len(obj.subpaths) == 1 and isinstance(obj.subpaths[0], pdfpath.Rectangle) :
					# OpenOffice seams to construct only paths containing exactly one rectangle
					rect = obj.subpaths[0]
					# if it's a big rectangle, it's a textbox
					if TEXTBOX_WIDTH[0] < rect.width < TEXTBOX_WIDTH[1] and \
						TEXTBOX_HEIGHT[0] < rect.height < TEXTBOX_HEIGHT[1] :
						box = model.questionnaire.Textbox()
						box_linecount = 0
						box.setup.setup(
							page_number,
							rect.point.x / mm,
							# transform the coordinate origin from the lower left corner to the upper left corner
							# and name the upper left corner of the box, not the lower left one
							(height - rect.point.y - rect.height) / mm,
							rect.width / mm,
							rect.height / mm
						)
					# if it's a small square, it's a checkbox
					elif CHECKBOX_SIZE[0] < rect.width < CHECKBOX_SIZE[1] and \
						CHECKBOX_SIZE[0] < rect.height < CHECKBOX_SIZE[1] :
						box = model.questionnaire.Checkbox()
						box_linecount = 0
						box.setup.setup(
							page_number,
							rect.point.x / mm,
							# transform the coordinate origin from the lower left corner to the upper left corner
							# and name the upper left corner of the box, not the lower left one
							(height - rect.point.y - rect.height) / mm,
							rect.width / mm,
							rect.height / mm
						)
					elif LINE_SIZE[0] < rect.width < LINE_SIZE[1] or \
						LINE_SIZE[0] < rect.height < LINE_SIZE[1] :

						if box is None:
							continue

						if rect.width < LINE_SIZE[1]:
							if rect.height / mm == box.height and \
								box.y == (height - rect.point.y - rect.height) / mm and \
								(abs(box.x - rect.point.x / mm) < 0.01 or
								 abs(box.x + box.width - ((rect.point.x + rect.width) / mm))  < 0.01):
								box_linecount += 1
						else:
							if rect.width / mm == box.width and \
								box.x == rect.point.x / mm and \
								(abs(box.y - (height - rect.point.y - rect.height) / mm) < 0.01 or
								 abs(box.y + box.height - ((height - rect.point.y - rect.height) + rect.height) / mm) < 0.01):
								box_linecount += 1
						if box_linecount == 4:
							if isinstance(box, DummyBox):
								print _("Warning: Ignoring a box (page: %i, x: %.1f, y: %.1f, width: %.1f, height: %.1f).") % \
									(box.page, box.x, box.y, box.width, box.height)
							else:
								boxes.append(box)
							box = None
							box_linecount = 0
					else:
						box_linecount = 0
						box = DummyBox(
							page_number,
							rect.point.x / mm,
							# transform the coordinate origin from the lower left corner to the upper left corner
							# and name the upper left corner of the box, not the lower left one
							(height - rect.point.y - rect.height) / mm,
							rect.width / mm,
							rect.height / mm
						)
				elif len(obj.subpaths) == 1 and isinstance(obj.subpaths[0], pdfpath.Subpath):
					if box is None:
						continue

					# OOo 3.x draws the box using a move + 4 lines + close.	
					if len(obj.subpaths[0].contents) == 6:
						# 5 subpaths, m,l,l,l,l,c

						point = obj.subpaths[0].contents[0]
						if not isinstance(point, pdfpath.Move):
							continue
						point = point.point
						if not (point.x / mm - box.x < 0.0001 and (height - point.y) / mm - box.y < 0.0001):
							continue

						point = obj.subpaths[0].contents[1]
						if not isinstance(point, pdfpath.Line):
							continue
						point = point.point2
						if not (point.x / mm - box.x < 0.0001 and (height - point.y) / mm - box.y - box.height < 0.0001):
							continue

						point = obj.subpaths[0].contents[2]
						if not isinstance(point, pdfpath.Line):
							continue
						point = point.point2
						if not (point.x / mm - box.x - box.width < 0.0001 and (height - point.y) / mm - box.y - box.height < 0.0001):
							continue

						point = obj.subpaths[0].contents[3]
						if not isinstance(point, pdfpath.Line):
							continue
						point = point.point2
						if not (point.x / mm - box.x - box.width < 0.0001 and (height - point.y) / mm - box.y < 0.0001):
							continue
						point = obj.subpaths[0].contents[4]
						if not isinstance(point, pdfpath.Line):
							continue
						point = point.point2

						if not (point.x / mm - box.x < 0.0001 and (height - point.y) / mm - box.y - box.height < 0.0001):
							continue

						if not isinstance(obj.subpaths[0].contents[5], pdfpath.Close):
							continue

						if isinstance(box, DummyBox):
							print _("Warning: Ignoring a box (page: %i, x: %.1f, y: %.1f, width: %.1f, height: %.1f).") % \
								(box.page, box.x, box.y, box.width, box.height)
						else:
							boxes.append(box)
						box = None

					# LibreOffice 3.5 draws the border as four trapezoids, with a 45degree angle in between, then filling it
					elif len(obj.subpaths[0].contents) == 8:
						# 8 subpaths, m,l,l,l,l,l,l,h
						# The angled corners have 3 points, instead of two, whoever thought of that ...
						# We just check that all points are inside the rectangle here
						x_min = 99999
						y_min = 99999
						x_max = -99999
						y_max = -99999
						for point in obj.subpaths[0].contents:
							if isinstance(point, pdfpath.Close):
								continue

							if isinstance(point, pdfpath.Line):
								point = point.point2
							else:
								point = point.point

							x_min = min(x_min, point.x)
							y_min = min(y_min, point.y)

							x_max = max(x_max, point.x)
							y_max = max(y_max, point.y)

						_width = x_max - x_min
						_height = y_max - y_min

						if _width == 1:
							if abs(_height - box.height*mm) < 0.0001:
								box_linecount += 1
						elif _height == 1:
							if abs(_width - box.width*mm) < 0.0001:
								box_linecount += 1
						else:
							box = None
							box_linecount = 0

						if box_linecount == 4:
							boxes.append(box)
							box = None
							box_linecount = 0

	return boxes, page_count


 
