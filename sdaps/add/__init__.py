# -*- coding: utf8 -*-
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
from sdaps import script

from sdaps.ugettext import ugettext, ungettext
_ = ugettext


parser = script.subparsers.add_parser("add",
    help=_("Add scanned questionnaires to the survey."),
    description=_("""This command is used to add scanned images to the survey.
    The image data needs to be a (multipage) 300dpi monochrome TIFF file. You
    may choose not to copy the data into the project directory. In that case
    the data will be referenced using a relative path."""))

parser.add_argument('--force',
    help=_("Force adding the images even if the page count is wrong (only use if you know what you are doing)."),
    action="store_true",
    default=False)
parser.add_argument('--copy',
    help=_("Copy the files into the directory (default)."),
    dest="copy",
    action="store_true",
    default=True)
parser.add_argument('--no-copy',
    help=_("Do not copy the files into the directory."),
    dest="copy",
    action="store_false")
parser.add_argument('--duplex',
    help=_("Images contain a duplex scan of a simplex questoinnaire (default: simplex scan)."),
    dest="duplex",
    action="store_true",
    default=False)

parser.add_argument('images',
    help=_("A number of TIFF image files."),
    nargs='+')

@script.connect(parser)
@script.logfile
def add(cmdline):
    from sdaps import image
    import subprocess
    import sys
    import shutil

    survey = model.survey.Survey.load(cmdline['project'])

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
        if cmdline['duplex']:
            insert_dummy_pages = False
        else:
            insert_dummy_pages = True

    for file in cmdline['images']:

        print _('Processing %s') % file

        if not image.check_tiff_monochrome(file):
            print _('Invalid input file %s. You need to specify a (multipage) monochrome TIFF as input.') % (file,)
            raise AssertionError()

        num_pages = image.get_tiff_page_count(file)

        c = survey.questionnaire.page_count
        if not insert_dummy_pages:
            c = c * image_count_factor

        # This test is on the image count that needs to come from the file
        if num_pages % c != 0 and not cmdline['force']:
            print _('Not adding %s because it has a wrong page count (needs to be a mulitple of %i).') % (file, c)
            continue

        if insert_dummy_pages:
            c = c * image_count_factor

        if cmdline['copy']:
            tiff = survey.new_path('%i.tif')
            shutil.copyfile(file, tiff)
        else:
            tiff = file

        if cmdline['copy']:
            tiff = os.path.basename(tiff)
        else:
            tiff = os.path.relpath(os.path.abspath(tiff), survey.survey_dir)

        pages = range(num_pages)
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

        print _('Done')

    survey.save()

