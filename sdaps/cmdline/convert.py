# -*- coding: utf-8 -*-
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
import sys

from sdaps import model
from sdaps import script
from sdaps import log

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext


parser = script.add_project_subparser("convert",
    help=_("Convert a set of images to the correct image format."),
    description=_("""This command can be used if you scanned files in something
        other than the expected monochrome TIFF mode. All given files will
        be loaded, converted to monochrome and stored in a multipage 1bpp
        TIFF file. Optionally, you can select \"3D transformation"\ ,which may facilitate
        working with photos of questionnaires instead of scans."""))

parser.add_argument('--3d-transform',
    help=_("""Do a 3D-transformation after finding the corner marks.
    If they are not found, the image will be processed as-is."""),
    dest="transform",
    action="store_true",
    default=False)
parser.add_argument('-o', '--output', required=True,
    help=_("The location of the output file."),
    dest="output")

parser.add_argument('images',
    help=_("A number of TIFF image files."),
    nargs='+')

@script.connect(parser)
@script.logfile
def convert(cmdline):
    from sdaps.convert import convert_images

    if cmdline['output'] is None:
        log.error(_("No output filename specified!"))
        sys.exit(1)

    # We need a survey only for the paper size!
    survey = model.survey.Survey.load(cmdline['project'])

    convert_images(cmdline['images'], cmdline['output'], survey.defs.paper_width, survey.defs.paper_height, cmdline['transform'])


