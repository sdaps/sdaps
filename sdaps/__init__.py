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
sdaps has a modular design. It ships a core python module called "model" which
is responsible for storing and basic modification of the data. When other
modules like "recognize" are loaded they '''extend''' the original model.

As an example the "recognize" module contains everything required to analyize
the scanned data and find checkmarks. However, it will in addition load the
"image", "matrix" and "surface" modules. These three modules are responsible
for loading and caching the image data and doing some pre-processing of the
image data(transformation matrix calculation).

Please have a look at the documentation of the "model" package.
"""

import sys

import paths
import script
import os
import argparse

from ugettext import ugettext, ungettext
_ = ugettext


def init(local_run=False):
    paths.init(local_run, __path__[0])

def main(local_run=False):
    init(local_run)

    description = _("SDAPS -- Paper based survey tool.")
    epilog = None
    script.parser = argparse.ArgumentParser(description=description, epilog=epilog)

    script.parser.add_argument('project', type=str, help=_("The SDAPS project."))
    script.subparsers = script.parser.add_subparsers(help=_("Commands:"))

    import add
    import boxgallery
    import cover
    import csvdata
    import gui
    import ids
    #import info
    import recognize
    import report
    import reporttex
    import setup
    import setuptex
    import stamp

    cmdline = script.parser.parse_args()
    cmdline = vars(cmdline)

    # Assume the script is at pos 2 ...
    print '-'*78
    print '- SDAPS -- %s' % cmdline['func'].__name__
    print '-'*78

    cmdline['func'](cmdline)




# Guess whether documentation is generated, if it is
# setup for local run.
if 'sphinx' in sys.argv[0]:
    paths.init(True, os.path.join(sys.path[0], 'sdaps'))

