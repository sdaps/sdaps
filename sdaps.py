#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <post@christoph-simon.eu>
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

import sys
import os
import os.path

bdir = '_build'
bpath = os.getenv('BUILDDIR', os.path.join(os.path.dirname(os.path.realpath(__file__)), '_build'))

if not os.path.exists(bpath):
    sys.stderr.write(f'You need to build SDAPS into {bdir} or install it on the system\n\n')
    sys.stderr.write('To do this, run the following commands in the source directory:\n')
    sys.stderr.write(f' * meson setup {bdir} [-Dlatex-class=true]\n')
    sys.stderr.write(f' * ninja -C {bdir}\n')
    sys.stderr.write('You can also set the BUILDDIR environment variable.\n')
    sys.exit(1)

import sdaps
sys.exit(sdaps.main(local_run = bpath))
