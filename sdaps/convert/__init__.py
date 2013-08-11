# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2013, Benjamin Berg <benjamin@sipsolutions.net>
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
from sdaps import log

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext


parser = script.subparsers.add_parser("convert",
    help=_("Convert a set of images to the correct image format."),
    description=_("""This command can be used if you scanned files in a different
        mode than the expected monochrome TIFF file. All the given files will
        be loaded, converted to monochrome and stored into a multipage 1bpp
        TIFF file. Optionally you can select that a 3D transformation should
        be performed, using this it may be possible to work with photos of
        questionnaires instead of scans."""))

parser.add_argument('--3d-transform',
    help=_("""Do a 3D-transformation after finding the corner marks. If the
        corner marks are not found then the image will be added as-is."""),
    dest="transform",
    action="store_true",
    default=False)
parser.add_argument('-o', '--output',
    help=_("The location of the output file. Must be given."),
    dest="output")

parser.add_argument('images',
    help=_("A number of TIFF image files."),
    nargs='+')

@script.connect(parser)
@script.logfile
def convert(cmdline):
    import subprocess
    import sys
    import shutil

    from sdaps import image
    from sdaps.utils import opencv

    if cmdline['output'] is None:
        log.error(_("No output filename specified!"))
        sys.exit(1)

    # We need a survey only for the paper size!
    survey = model.survey.Survey.load(cmdline['project'])

    for i, (img, filename, page) in enumerate(opencv.iter_images_and_pages(cmdline['images'])):
        img = opencv.ensure_portrait(img)
        img = opencv.sharpen(img)

        if cmdline['transform']:
            try:
                img = opencv.transform_using_corners(img, survey.defs.paper_width, survey.defs.paper_height)
            except AssertionError:
                log.error(_("Could not apply 3D-transformation to image '%s', page %i!") % (filename, page))

        mono = opencv.convert_to_monochrome(img)
        image.write_a1_to_tiff(cmdline['output'], opencv.to_a1_surf(mono))

