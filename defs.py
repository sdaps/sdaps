# -*- coding: utf-8 -*-
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

paper_width = 210.0 # mm
paper_height = 297.0 # mm

corner_mark_x = 10.0 # mm
corner_mark_y = 12.0 # mm
corner_mark_width = 190.0 # mm
corner_mark_height = 273.0 # mm
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
# x, y
corner_boxes_positions = [
	[13.0, 15.0],
	[193.5, 15.0],
	[13.0, 278.5],
	[193.5, 278.5],
]
corner_box_width = 3.5 # mm
corner_box_height = 3.5 # mm


codebox_length = 16 # bits
codebox_step = 3.5 # mm
codebox_width = codebox_step * 16 # mm
codebox_height = 3.5 # mm
codebox_offset = 0.75 # mm

survey_id_msb_x = 19.5 # mm
survey_id_msb_y = 278.5 # mm
survey_id_lsb_x = 134.5 # mm
survey_id_lsb_y = 278.5 # mm

questionnaire_id_msb_x = 19.5 # mm
questionnaire_id_msb_y = 272.0 # mm
questionnaire_id_lsb_x = 134.5 # mm
questionnaire_id_lsb_y = 272.0 # mm

