#!/usr/bin/env python3
# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright (C) 2015, Benjamin Berg <benjamin@sipsolutions.net>
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

import sys
import os
import cairo
import math

# Use the following and local_run=True below to run without installing SDAPS
#sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '..'))

import sdaps
#sdaps.init(local_run=True)
sdaps.init()

from sdaps import model
from sdaps import image
from sdaps import matrix

survey = model.survey.Survey.load(sys.argv[1])
counter = 1


def ellipse(cr, x, y, width, height):
    cr.save()

    cr.translate(x + width / 2.0, y + height / 2.0)

    line_width = cr.get_line_width()

    cr.scale(width / 2.0, height / 2.0)
    cr.arc(0, 0, 1.0, 0, 2*math.pi)
    cr.close_path()

    # Restore old matrix (without removing the current path)
    cr.restore()



def generate_pdf():

    global counter
    global survey

    questionnaire = survey.questionnaire
    sheet = survey.sheet

    # Use the questionnaire ID, if not there, give up?
    if sheet.questionnaire_id is not None:
        pdf_name = 'overlay-%s.pdf' % sheet.questionnaire_id
    else:
        pdf_name = 'overlay-%04i.pdf' % counter
        counter += 1

    surface = cairo.PDFSurface(pdf_name, survey.defs.paper_width * 72 / 25.4, survey.defs.paper_height * 72 / 25.4)
    cr = cairo.Context(surface)

    # Transform to mm space
    cr.scale(72 / 25.4, 72 / 25.4)

    for p in range(questionnaire.page_count):
        # 1 based page numbers
        p += 1

        # Get the current image
        img = sheet.get_page_image(p)
        if img is None:
            print("no image")
            cr.show_page()
            continue

        # Render the image on the background, we take the easy way and paint it
        # correctly. i.e. so that the markings on top are at the expected
        # positions. It would likely be faster to only scale the image instead.
        # (And not much harder, just needs the correct transformation for the
        # other markings)
        cr.save()
        cr.transform(img.matrix.px_to_mm())
        cr.set_source_rgb(0, 0, 0)
        cr.mask_surface(img.surface.load_uncached(), 0, 0)
        cr.restore()

        # Now render all checked checkboxes, for now inline here.
        for qobj in questionnaire.qobjects:
            for box in qobj.boxes:
                if box.data.state:
                    if box.page_number != p:
                        continue

                    if not isinstance(box, model.questionnaire.Checkbox):
                        continue

                    # 1pt line width
                    cr.set_line_width(1 / 25.4)

                    x, y, width, height = box.data.x, box.data.y, box.data.width, box.data.height
                    x -= width / math.sqrt(2) / 2
                    y -= height / math.sqrt(2) / 2
                    width += width / math.sqrt(2)
                    height += height / math.sqrt(2)

                    ellipse(cr, x, y, width, height)
                    cr.set_source_rgb(1, 0, 0)
                    cr.stroke()

        cr.show_page()

    del cr
    surface.flush()
    del surface

survey.iterate_progressbar(generate_pdf)

