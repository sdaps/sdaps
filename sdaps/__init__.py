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

from ugettext import ugettext, ungettext
_ = ugettext


def sdaps(survey_dir, script_name, *arguments):
    print '-' * 80
    print
    print 'sdaps', script_name
    print
    print '-' * 80

    if not script_name in script.scripts:
        print _(u'''Unknown script "%s". Aborting.''') % script_name
        return 1
    return script.scripts[script_name](survey_dir, *arguments)


def doc(name="sdaps"):
    print _('''Usage: %s project_dir command [args]

You need to specify the project_dir for SDAPS to work on. Depending on the
command this needs to exist, or it will be created automatically.

The following commands and their respective options are available:''' % name)
    scripts = script.scripts.keys()
    scripts.sort()
    for key in scripts:
        print '     * %s' % key
    print
    for key in scripts:
        print script.scripts[key].func_name, script.scripts[key].func_doc
    return 0

def init(local_run=False):
    paths.init(local_run, __path__[0])

def main(local_run=False):
    init(local_run)

    import add
    import boxgallery
    import cover
    import csvdata
    import gui
    import ids
    import info
    import recognize
    import report
    import reporttex
    import setup
    import setuptex
    import stamp

    if len(sys.argv) < 3:
        return doc(os.path.basename(sys.argv[0]))
    else:
        return sdaps(*sys.argv[1:])


# Guess whether documentation is generated, if it is
# setup for local run.
if 'sphinx' in sys.argv[0]:
    paths.init(True, os.path.join(sys.path[0], 'sdaps'))

