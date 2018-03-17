#!/usr/bin/env python3
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2011, Benjamin Berg <benjamin@sipsolutions.net>
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
This file generates the latexmap.py file which is needed
to convert latex symbols into their unicode counterpart.

Run with create-latexmap.py path/to/utf-8enc.dfu
"""

import re
import sys

if len(sys.argv) != 2:
    print(__doc__)
    sys.exit(1)

output = open('latexmap.py', 'w')
input = open(sys.argv[1])

data = input.read()

regexp = re.compile(r'^\\DeclareUnicodeCharacter\{(?P<unicode>[0-9a-fA-F]{4})\}\{(?P<str>[^\}]+)\}', re.MULTILINE)

mapping = []
for match in regexp.finditer(data):
    repr = match.group('str')
    repr = repr.replace('\\@tabacckludge', '\\')
    repr = repr.replace('\\', '\\\\').replace('\'', '\\\'')
    mapping.append('''    u\'%s\': u\'\\u%s\'''' %
                   (repr,
                    match.group('unicode')))

output.write('''#This file is auto generated from the latex unicode mapping.

#: Mapping from LaTeX commands to unicode characters.
mapping = {
''')

output.write(',\n'.join(mapping))
output.write('''
}
''')
