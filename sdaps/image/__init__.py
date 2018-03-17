# -*- coding: utf-8 -*-
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

"""
This modules contains low level image processing functions. These functions
are implemented in C for speed reasons. Usually one will not need to use these
directly, instead modules like "recognize" or "surface" use them to load and
analyze the image data.
"""

import os
import sys

from sdaps import paths
from sdaps import defs
from sdaps import log

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

if paths.local_run:
    # image.so liegt in lib_build_dir/image/
    __path__.append(os.path.join(paths.lib_build_dir, 'image'))

# If SDAPS is installed, then the image.so file is in the current directory.
# Simply importing it without changes to the paths will work.

try:
    from .image import *
except ImportError as e:
    print(e)
    log.error(_("It appears you have not build the C extension. Please run \"./setup.py build\" in the toplevel directory."))
    sys.exit(1)

set_magic_values(defs.corner_mark_min_length,
                 defs.corner_mark_max_length,
                 defs.image_line_width,
                 defs.corner_mark_search_distance,
                 defs.image_line_coverage)

