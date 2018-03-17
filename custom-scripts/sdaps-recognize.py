#!/usr/bin/env python3
# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright (C) 2012, Benjamin Berg <benjamin@sipsolutions.net>
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

# Use the following and local_run=True below to run without installing SDAPS
#sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '..'))

import sdaps
#sdaps.init(local_run=True)
sdaps.init()

from sdaps import model
from sdaps import image

# Assume the first argument is a survey
survey = model.survey.Survey.load(sys.argv[1])

# We need the recognize buddies, as they are able to identify the data
from sdaps.recognize import buddies

# A sheet object to attach the images to
sheet = model.sheet.Sheet()
survey.add_sheet(sheet)

images = []

for file in sys.argv[2:]:
    num_pages = image.get_tiff_page_count(file)
    for page in range(num_pages):
        images.append((file, page))

if len(images) == 0:
    # No images, simply exit again.
    sys.exit(1)


def add_image(survey, tiff, page):
    img = model.sheet.Image()
    survey.sheet.add_image(img)
    # SDAPS assumes a relative path from the survey directory
    img.filename = os.path.relpath(os.path.abspath(tiff), survey.survey_dir)
    img.orig_name = tiff
    img.tiff_page = page

while images:
    # Simply drop the list of images again.
    sheet.images = []

    add_image(survey, *images.pop(0))

    if survey.defs.duplex:
        add_image(survey, *images.pop(0))
    else:
        add_image(survey, 'DUMMY', -1)

    # Run the recognition algorithm over the given images
    survey.questionnaire.recognize.recognize()

    for qobject in survey.questionnaire.qobjects:
        if isinstance(qobject, model.questionnaire.Question):
            # Only print data if an image for the page has been loaded
            if survey.sheet.get_page_image(qobject.page_number) is None:
                continue
            for box in qobject.boxes:
                print("%s,%s,%s,%s,%i,%f" % (
                    survey.sheet.global_id,
                    survey.sheet.survey_id,
                    survey.sheet.questionnaire_id,
                    '_'.join([str(num) for num in box.id]),
                    int(box.data.state),
                    float(box.data.quality)))
    print()

# And, we simply quit, ie. we don't save the survey

