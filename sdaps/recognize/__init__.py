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

u"""
This module adds the functionality to automatically recognize the scanned image
data. It reads the image data and tries to guess whether a checkbox is
empty/checked/filled and finds the written area in a textfield.
"""

from sdaps import model
from sdaps import script

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext


parser = script.subparsers.add_parser("recognize",
    help=_("Run the optical mark recognition."),
    description=_("""Iterates over all images and runs the optical mark
    recognition. It will reevaluate sheets even if "recognize" has already
    run or manual changes were made."""))

parser.add_argument('--identify',
    help=_("Only identify the page properties, but don't recognize the checkbox states."),
    action="store_true",
    default=False)

@script.connect(parser)
@script.logfile
def recognize(cmdline):
    survey = model.survey.Survey.load(cmdline['project'])
    import recognize
    if cmdline['identify']:
        return recognize.identify(survey)
    else:
        return recognize.recognize(survey)


