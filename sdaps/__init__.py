# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <christoph.simon@gmx.eu>
# Copyright (C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
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
SDAPS has a modular design. It ships a core python module called "model" which
is responsible for storing and basic modification of the data. When other
modules like "recognize" are loaded they '''extend''' the original model.

As an example the "recognize" module contains everything required to analyize
the scanned data and find checkmarks. However, it will in addition load the
"image", "matrix" and "surface" modules. These three modules are responsible
for loading and caching the image data and doing some pre-processing of the
image data (transformation matrix calculation).

Please have a look at the documentation of the "model" package.
"""

import sys

import paths
import ugettext
import script


def sdaps (survey_dir, script_name, *arguments) :
	print '-' * 80
	print
	print 'sdaps', script_name
	print
	print '-' * 80

	try :
		return script.scripts[script_name](survey_dir, *arguments)
	except KeyError, detail :
		print _(u'''Unknown script "%s". Aborting.''') % script_name
		return 1


def doc () :
	for script_class in script.scripts.itervalues() :
		print script_class.func_name, script_class.func_doc
	return 0


def main (local_run = False) :
	paths.init(local_run, __path__[0])

	# Import scripts
	# (They will register themselfs)
	import add
	import boxgallery
	import cover
	import csvdata
	import gui
	import ids
	import info
	import recognize
	import report
	import setup
	import stamp

	# Run
	if len(sys.argv) < 3 :
		return doc()
	else :
		return sdaps(*sys.argv[1:])


