# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <post@christoph-simon.eu>
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

import cairo
import pango
import pangocairo

import buddies


def paint_box(cr, mm_to_pt, x, y, box):
	cr.save()
	cr.set_matrix(mm_to_pt)
	cr.translate(x, y)
	
	pattern = cairo.SurfacePattern(box[1])
	# 300dpi
	m = cairo.Matrix()
	m.scale(300.0/25.4, 300.0/25.4)
	pattern.set_matrix(m)
	pattern.set_filter(cairo.FILTER_FAST)

	cr.set_source(pattern)
	cr.paint()
	
	cr.restore()

	cr.save()
	
	tmp_x, tmp_y = mm_to_pt.transform_point(x, y)
	tmp_width, tmp_height = mm_to_pt.transform_distance(8, 13)

	tmp_x, tmp_y = mm_to_pt.transform_point(x, y + 8.0)
	t = "%.2f" % box[0]
	
	cr.move_to(tmp_x, tmp_y)

	layout = cr.create_layout()
	layout.set_markup(t)
	font = pango.FontDescription("serif 6")
	layout.set_font_description(font)
	
	cr.show_layout(layout)
	

	cr.restore()
	

def fill_page(cr, mm_to_pt, checkboxes):
	y = 15
	y_step = 13
	x_step = 10
	x_max = 210 - 15 - 8
	y_max = 297 - 15 - 8
	
	while y < y_max:
		x = 15
		while x < x_max:
			
			if len(checkboxes) == 0:
				return
			box = checkboxes.pop(0)
			
			paint_box(cr, mm_to_pt, x, y, box)

			x += x_step
		y += y_step


def boxgallery (survey):
	survey.questionnaire.boxgallery.init()
	survey.iterate(survey.questionnaire.boxgallery.get_checkbox_images)
	checkboxes = survey.questionnaire.boxgallery.checkboxes
	survey.questionnaire.boxgallery.clean()
	
	checkboxes.sort(key = lambda x: x[0])

	# Hardcode 300dpi
	# Hardcode the mm size:
	# 3.5 + 0.4mm = 3.9mm
	mm_to_pt = cairo.Matrix(72.0/25.4, 0, 0, 72.0/25.4, 0, 0)
	
	page = 1
	pdf = cairo.PDFSurface(survey.path('boxgallery.pdf'), 595, 842)
	cr = cairo.Context(pdf)
	cr = pangocairo.CairoContext(cr)
	
	while len(checkboxes) > 0:
		fill_page(cr, mm_to_pt, checkboxes)
		cr.show_page()
		pdf.flush()
		
		page += 1
	
	del pdf
	del cr

