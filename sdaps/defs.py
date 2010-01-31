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
Defs
====

This module contains constants and some magic values.
"""

import os
from pkg_resources import get_build_platform
from distutils.sysconfig import get_python_version
import gettext, locale
import __builtin__

paper_width = 210.0 # mm
paper_height = 297.0 # mm

corner_mark_x = 10.0 # mm
corner_mark_y = 12.0 # mm
corner_mark_width = 190.0 # mm
corner_mark_height = 273.0 # mm
corner_mark_length = 20.0 # mm

# top left, top right, bottom left, bottom right
corner_boxes = [
	[0, 1, 1, 1],
	[1, 1, 0, 0],
	[1, 0, 1, 1],
	[1, 0, 1, 0],
	[1, 0, 0, 0],
	[0, 0, 0, 1],
]
# x, y
corner_boxes_positions = [
	[13.0, 15.0],
	[193.5, 15.0],
	[13.0, 278.5],
	[193.5, 278.5],
]
corner_box_width = 3.5 # mm
corner_box_height = 3.5 # mm


codebox_length = 16 # bits
codebox_step = 3.5 # mm
codebox_width = codebox_step * 16 # mm
codebox_height = 3.5 # mm
codebox_offset = 0.75 # mm

survey_id_msb_x = 19.5 # mm
survey_id_msb_y = 278.5 # mm
survey_id_lsb_x = 134.5 # mm
survey_id_lsb_y = 278.5 # mm

questionnaire_id_msb_x = 19.5 # mm
questionnaire_id_msb_y = 272.0 # mm
questionnaire_id_lsb_x = 134.5 # mm
questionnaire_id_lsb_y = 272.0 # mm

# XXX: I do not like this, but I did not find any sane way to generate a .py
#      file with the information during setup. If someone knows, please drop
#      me a line.
def find_data_prefix():
	import sys
	import os
	for path in sys.path:
		while True:
			new_path, tail = os.path.split(path)
			if path == new_path:
				break
			path = new_path
			if os.path.exists(os.path.join(path, 'share', 'sdaps')):
				return os.path.join(path, 'share')
	return os.path.join(sys.prefix, 'share')

def find_locale_dir(src_dir=None):
	if src_dir:
		if os.path.exists(os.path.join(src_dir, 'mo')):
			return os.path.join(src_dir, 'mo')
		else:
			sys.stderr.write("You should run ./setup.py build_i18n!")
			return None
	else:
		return os.path.join(find_data_prefix(), 'locale')

def find_data_dir(src_dir=None):
	return os.path.join(find_data_prefix(), 'sdaps')

build_tree = None
def init(sdaps_src_tree=None):
	global in_src, src_tree, build_tree, locale_dir, glade_dir

	if sdaps_src_tree is not None:
		in_src = True
	else:
		in_src = False
	src_tree = sdaps_src_tree
	dir = 'lib.%s-%s' % (get_build_platform(), get_python_version())

	if in_src:
		build_tree = os.path.abspath(os.path.join(src_tree, 'build', dir, 'sdaps'))
		if not os.path.exists(build_tree):
			import sys
			sys.stderr.write('You need to at least run "./setup.py build_ext" to run sdaps!\n')
			sys.exit(1)

	locale_dir = find_locale_dir()
	if not in_src:
		data_dir = find_data_dir()



	# Initilize the translation system, step 2
	gettext.bindtextdomain('sdaps', defs.locale_dir)
	if hasattr(gettext, 'bind_textdomain_codeset'): 
		gettext.bind_textdomain_codeset('sdaps','UTF-8')
		gettext.textdomain('sdaps')
		locale.bindtextdomain('sdaps', defs.locale_dir)
	if hasattr(locale, 'bind_textdomain_codeset'): 
		locale.bind_textdomain_codeset('sdaps','UTF-8')
		locale.textdomain('sdaps')

# Initilize the translation system, step 1
__builtin__._ = lambda x: gettext.gettext(x).decode('UTF-8')
__builtin__.ngettext = lambda a, b, c: gettext.ngettext(a, b, c).decode('UTF-8')
