# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
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

import csv

from sdaps import clifilter
from sdaps import model

from . import buddies


def csvdata_export(survey, csvfile, image_writer, filter=None, export_images=False, export_question_images=False, export_quality=False, csvoptions={}):
    # compile clifilter
    filter = clifilter.clifilter(survey, filter)

    # export
    survey.questionnaire.csvdata.open_csv(csvfile, image_writer, export_images, export_question_images, export_quality, csvoptions)

    survey.iterate(
        survey.questionnaire.csvdata.export_data,
        filter,
    )

    survey.questionnaire.csvdata.export_finish()


def csvdata_import(survey, csvfile):
    csvreader = csv.DictReader(csvfile)

    for data in csvreader:
        survey.questionnaire.csvdata.import_data(data)

    csvfile.close()

    survey.save()


