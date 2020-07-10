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

"""
This module reset already stored data so next reports and exports will contain only new questionnaires.
"""

from collections import defaultdict
from sdaps import model, log
import bz2,os,pickle
import os.path
from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

def reset(survey):
    print((_("Removing stored data...")))
    image_files = set()

    def delete_sheet():
        sheet = survey.get_sheet()
        for img in sheet.images:
            if img.ignored:
                continue

            image_files.add(img.filename)

        survey.delete_sheet(survey.get_sheet())

    survey.iterate(delete_sheet)
    survey.questionnaire_ids = []

    # Try to delete all the source files, but only if they are relative
    for f in image_files:
        try:
            full_path = os.path.abspath(survey.path(f))
            # Only delete file if it is in the survey directory
            if not full_path.startswith(os.path.abspath(survey.survey_dir)):
                continue
            os.unlink(full_path)
        except OSError as e:
            log.warn(_("Failed to delete file {}: {}").format(full_path, e.strerror))

    survey.save()
    print((_("Done")))
