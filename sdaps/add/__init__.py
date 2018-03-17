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

import os

from sdaps import model
from sdaps import image
import shutil

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

def _insert_dummy_pages(survey, duplex_scan):
    # Insert dummy pages if the survey is duplex and the duplex option was not
    # passed
    if survey.defs.duplex:
        # One image per questionnaire page in duplex mode
        image_count_factor = 1
        # No dummy pages in duplex mode
        insert_dummy_pages = False
    else:
        # Two images per questionnaire page in duplex mode
        image_count_factor = 2

        # In simplex mode insertion of dummy pages depends on the command line
        # optoin (default is True)
        if duplex_scan:
            insert_dummy_pages = False
        else:
            insert_dummy_pages = True

    return insert_dummy_pages, image_count_factor

def check_image(survey, file, duplex_scan=False, force=False, message=False):

    insert_dummy_pages, image_count_factor = _insert_dummy_pages(survey, duplex_scan)

    if not image.check_tiff_monochrome(file):
        if message:
            print(_('Invalid input file %s. You need to specify a (multipage) monochrome TIFF as input.') % (file,))
        return False

    num_pages = image.get_tiff_page_count(file)

    c = survey.questionnaire.page_count
    if not insert_dummy_pages:
        c = c * image_count_factor

    # This test is on the image count that needs to come from the file
    if num_pages % c != 0 and not force:
        if message:
            print(_('Not adding %s because it has a wrong page count (needs to be a mulitple of %i).') % (file, c))
        return False

    return True

def add_image(survey, file, duplex_scan=False, force=False, copy=True):

    insert_dummy_pages, image_count_factor = _insert_dummy_pages(survey, duplex_scan)

    if not check_image(survey, file, duplex_scan, force, message=True):
        return

    num_pages = image.get_tiff_page_count(file)

    c = survey.questionnaire.page_count
    if not insert_dummy_pages:
        c = c * image_count_factor

    if insert_dummy_pages:
        c = c * image_count_factor

    if copy:
        tiff = survey.new_path('%i.tif')
        shutil.copyfile(file, tiff)
    else:
        tiff = file

    if copy:
        tiff = os.path.basename(tiff)
    else:
        tiff = os.path.relpath(os.path.abspath(tiff), survey.survey_dir)

    pages = list(range(num_pages))
    while len(pages) > 0:
        sheet = model.sheet.Sheet()
        survey.add_sheet(sheet)
        while len(pages) > 0 and len(sheet.images) < c:
            img = model.sheet.Image()
            sheet.add_image(img)
            img.filename = tiff
            img.tiff_page = pages.pop(0)

            # And a dummy page if required
            if insert_dummy_pages:
                img = model.sheet.Image()
                sheet.add_image(img)

                img.filename = "DUMMY"
                img.tiff_page = -1
                img.ignored = True

