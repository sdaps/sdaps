#!/usr/bin/env python

u"""
This file generates the latexmap.py file which is needed
to convert latex symbols into their unicode counterpart.

Run with create-latexmap.py path/to/utf8enc.dfu
"""

import re
import sys

if len(sys.argv) != 2:
    print __doc__
    sys.exit(1)

output = open('latexmap.py', 'w')
input = open(sys.argv[1])

data = input.read()

regexp = re.compile(r'^\\DeclareUnicodeCharacter\{(?P<unicode>[0-9a-fA-F]{4})\}\{(?P<str>[^\}]+)\}', re.MULTILINE)

mapping = []
for match in regexp.finditer(data):
    mapping.append('''\tu\'%s\': u\'\\u%s\'''' %
                   (match.group('str').replace('\\', '\\\\').replace('\'', '\\\''),
                    match.group('unicode')))

output.write('''#This file is auto generated from the latex unicode mapping.

#: Mapping from LaTeX commands to unicode characters.
mapping = {
''')

output.write(',\n'.join(mapping))
output.write('''
}
''')
