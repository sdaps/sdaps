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

# We need a survey that has the correct definitions (paper size, duplex mode)
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

    sheet.recognize.recognize()

    for img in sheet.images:
        print(img.orig_name, img.tiff_page)
        print('\tPage:', img.page_number)
        print('\tRotated:', img.rotated)
        print('\tMatrix (px to mm):', img.raw_matrix)
        print('\tSurvey-ID:', sheet.survey_id)
        print('\tGlobal-ID:', sheet.global_id)
        print('\tQuestionnaire-ID:', sheet.questionnaire_id)
        print()

# And, we simply quit, ie. we don't save the survey

