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

from gi.repository import Poppler
import cairo
from . import buddies
import os.path

def annotate(survey, infile=None, outfile=None):
    if infile is None:
        infile = 'file://' + os.path.abspath(survey.path('questionnaire.pdf'))
    else:
        infile = 'file://' + os.path.abspath(infile)

    if outfile is None:
        outfile = survey.path('annotated_questionnaire.pdf')

    pdf = Poppler.Document.new_from_file(infile, None)

    width, height = pdf.get_page(0).get_size()

    output = cairo.PDFSurface(outfile, 2*width, 2*height)

    cr = cairo.Context(output)

    for p in range(survey.questionnaire.page_count):
        pdf.get_page(p).render_for_printing(cr)

        cr.save()
        # Use mm space in here.
        cr.scale(72.0 / 25.4, 72.0 / 25.4)

        layout_info = dict()
        layout_info['twidth'] = width / 72.0 * 25.4 - 20 # mm
        layout_info['xshift'] = width / 72.0 * 25.4 + 10 # mm
        layout_info['ypos'] = 15 # mm
        layout_info['font'] = "Sans 3"
        layout_info['boxfont'] = "Sans 2"

        # And, render the questions on top (1 based page numbers here)
        survey.questionnaire.annotate.draw(cr, p + 1, layout_info)

        cr.restore()

        cr.show_page()


