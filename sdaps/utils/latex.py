# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, 2013, Benjamin Berg <benjamin@sipsolutions.net>
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

from sdaps import log
import re

from sdaps import defs
import subprocess
import os

try:
    from sdaps.utils.latexmap import mapping
except ImportError:
    mapping = {}
    log.warning(_(u'The latex character map is missing! Please build it using the supplied tool (create-latexmap.py).'))

# Add some more mappings
# NBSP
mapping[u'~'] = u' '


re_latex_to_unicode_mapping = {}
for token, replacement in mapping.iteritems():
    regexp = re.compile(u'%s(?=^w|})' % re.escape(token))
    re_latex_to_unicode_mapping[regexp] = replacement

# Regular expressions don't work really, but we replace a single string anyways
unicode_to_latex_mapping = {}
for token, replacement in mapping.iteritems():
    unicode_to_latex_mapping[replacement] = u"{%s}" % token


def latex_to_unicode(string):
    string = unicode(string)
    for regexp, replacement in re_latex_to_unicode_mapping.iteritems():
        string, count = regexp.subn(replacement, string)

    def ret_char(match):
        return match.group('char')
    string, count = re.subn(r'\\IeC {(?P<char>.*?)}', ret_char, string)
    return string

def unicode_to_latex(string):
    string = unicode(string)
    for char, replacement in unicode_to_latex_mapping.iteritems():
        string = string.replace(char, replacement)

    # Ensure only ASCII characters are left
    return string.encode('ascii')

# This is a list, because the order is relevant!
ascii_to_latex = [
    (u'{', u'\\{'),
    (u'}', u'\\}'),
    (u'\\', u'{\\textbackslash}'),
    (u'%', u'\\%'),
    (u'$', u'\\$'),
    (u'_', u'\\_'),
    (u'|', u'{\\textbar}'),
    (u'>', u'{\\textgreater}'),
    (u'<', u'{\\textless}'),
    (u'&', u'\\&'),
    (u'#', u'\#'),
    (u'^', u'\\^{}'),
    (u'~', u'\\~{}'),
    (u'"', u'\\"{}'),
]

def raw_unicode_to_latex(string):
    u"""In addition to converting all unicode characters to LaTeX expressions
    this function also replaces some characters like newlines with their LaTeX
    equvivalent."""

    # We need to quote any special character (or replace it)
    for char, replacement in ascii_to_latex:
        string = string.replace(char, replacement)

    string = unicode_to_latex(string)

    string = unicode(string)

    # Replace many newlines with a paragraph marker
    string, count = re.subn('\n\n+', u'\u2029', string, flags=re.MULTILINE)

    # Replace single newline with \\+newline
    string = string.replace('\n', '\\\\\n')

    # And remove the paragraph marker again (insert two newlines)
    string = string.replace(u'\u2029', '\n\n')

    return string.encode('ascii')

def run_engine(texfile, cwd, inputs=None):
    def _preexec_fn():
        if defs.latex_preexec_hook is not None:
            defs.latex_preexec_hook()

        if inputs:
            os.environ['TEXINPUTS'] = ':'.join(['.'] + inputs + [''])

    subprocess.call([defs.latex_engine, '-halt-on-error',
                     '-interaction', 'batchmode', texfile],
                    cwd=cwd,
                    preexec_fn=_preexec_fn)


def compile(texfile, cwd, inputs=None):
    run_engine(texfile, cwd, inputs)
    run_engine(texfile, cwd, inputs)


