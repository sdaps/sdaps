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



inch = 72.0 # pt (pdf unit)
cm = inch / 2.54
mm = cm * 0.1

# TODO Documentation for these values
# (min, max)
TEXTBOX_WIDTH = (17.3 * cm, 17.5 * cm)
TEXTBOX_HEIGHT = (1.5 * cm, 20 * cm)
CHECKBOX_SIZE = (3.4 * mm, 3.6 * mm)


def parse (questionnaire_pdf) :

	doc = pdffile.PDFDocument(questionnaire_pdf)
	
	boxes = list()
	
	page_count = doc.count_pages()
	assert page_count % 2 == 0
	
	for page_number in range(1, page_count + 1) :
		page = doc.read_page(page_number)
		contents = page.read_contents()
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
						boxes.append(box)
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
						boxes.append(box)
						box.setup.setup(
							page_number,
							rect.point.x / mm,
							# transform the coordinate origin from the lower left corner to the upper left corner
							# and name the upper left corner of the box, not the lower left one
							(height - rect.point.y - rect.height) / mm,
							rect.width / mm,
							rect.height / mm
						)
	
	return boxes, page_count


 
