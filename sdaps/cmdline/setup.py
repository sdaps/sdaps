# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2010, Benjamin Berg <benjamin@sipsolutions.net>
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

from sdaps import model
from sdaps import script

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext


parser = script.subparsers.add_parser("setup", aliases=["setup_tex"],
    help=_("Create a new survey using a LaTeX document."),
    description=_("""Create a new survey from a LaTeX document. You need to
    be using the SDAPS class. All the metadata and options for the project
    can be set inside the LaTeX document."""))

parser.add_argument('questionnaire.tex',
    help=_("The LaTeX Document"))
parser.add_argument('-a', '--add',
    help=_("Additional files that are required by the LaTeX document and need to be copied into the project directory."),
    action='append', default=[])
parser.add_argument('additional_questions',
    nargs='?',
    help=_("Additional questions that are not part of the questionnaire."))

@script.connect(parser)
def setup(cmdline):
    from sdaps import setuptex

    return setuptex.setup(cmdline['project'], cmdline['questionnaire.tex'], cmdline['additional_questions'], cmdline['add'])


