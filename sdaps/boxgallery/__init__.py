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
This modules contains a script for the user to output all boxes sorted by their
coverage. This can be used to adjust magic values for checkbox recognition.
"""

from sdaps import model
from sdaps import script

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

parser = script.subparsers.add_parser("boxgallery",
    help=_("Create PDFs with boxes sorted by the detection heuristics."),
    description=_("""SDAPS uses multiple heuristics to detect determine the
    state of checkboxes. There is a list for each heuristic giving the expected
    state and the quality of the value (see defs.py). Using this command a PDF
    will be created for each of the heuristics so that one can adjust the
    values."""))

@script.connect(parser)
@script.logfile
def boxgallery(cmdline):
    survey = model.survey.Survey.load(cmdline['project'])
    import boxgallery
    boxgallery.boxgallery(survey)


