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
    log.warn(_('The latex character map is missing! Please build it using the supplied tool (create-latexmap.py).'))

# Add some more mappings
# NBSP
mapping['~'] = ' '


re_latex_to_unicode_mapping = {}
for token, replacement in mapping.items():
    regexp = re.compile('%s(?=^w|})' % re.escape(token))
    re_latex_to_unicode_mapping[regexp] = replacement

# Regular expressions don't work really, but we replace a single string anyways
unicode_to_latex_mapping = {}
for token, replacement in mapping.items():
    unicode_to_latex_mapping[replacement] = "{%s}" % token


def latex_to_unicode(string):
    string = str(string)
    for regexp, replacement in re_latex_to_unicode_mapping.items():
        string, count = regexp.subn(replacement, string)

    def ret_char(match):
        return match.group('char')
    string, count = re.subn(r'\\IeC {(?P<char>.*?)}', ret_char, string)
    return string

def unicode_to_latex(string):
    string = str(string)
    for char, replacement in unicode_to_latex_mapping.items():
        string = string.replace(char, replacement)

    # The returned string may still contain unicode characters if
    # the user is using xelatex. But in that case, the remapping is not
    # needed anyway.
    # However, it could also mean that the mapping needs to be updated.
    try:
        string.encode('ascii')
    except UnicodeEncodeError:
        log.warn(_("Generated string for LaTeX contains unicode characters. This may not work correctly and could mean the LaTeX character map needs to be updated."))
    return string

def quote_braces(string):
    return string.replace('{', '\\{').replace('}', '\\}')

def write_override(survey, optfile, draft=False, questionnaire_ids=None):
    latex_override = open(optfile, 'w')

    if questionnaire_ids:
        quoted_ids = [quote_braces(str(id)) for id in questionnaire_ids]
    else:
        quoted_ids = []

    latex_override.write('''
%% This file exists to force the latex document into "final" mode.
%% It is parsed after the setup phase of the SDAPS class.

%% Old class vs. new class
\\ifcsname @PAGEMARKtrue\endcsname
    \\setcounter{surveyidlshw}{%(survey_id_lshw)i}
    \\setcounter{surveyidmshw}{%(survey_id_mshw)i}
    \\def\\surveyid{%(survey_id)i}
    %(noglobalid)s\\def\\globalid{%(global_id)s}
    \\@STAMPtrue
    \\@PAGEMARKtrue
    \\@sdaps@draft%(draft)s
    \\def\\questionnaireids{%(qids_old)s}
\\else
  \\group_begin:
    \\def\\setoptions#1#2#3{
      \\tl_gset:Nn \\g_sdaps_survey_id_tl { #1 }
      %(noglobalid)s\\tl_gset:Nn \\g_sdaps_global_id_tl { #2 }
      \\seq_gset_from_clist:Nn \\g_sdaps_questionnaire_ids_seq { #3 }
    }
    \\bool_gset_%(draft)s:N \g_sdaps_draft_bool

    \\ExplSyntaxOff
      \\setoptions{%(survey_id)i}{%(global_id)s}{%(qids)s}
    \\ExplSyntaxOn
  \group_end:
\\fi
''' % {
            'survey_id' : survey.survey_id,
            'survey_id_lshw' : (survey.survey_id % (2 ** 16)),
            'survey_id_mshw' : (survey.survey_id / (2 ** 16)),
            'draft' : 'true' if draft else 'false',
            'noglobalid' : '%' if draft else '',
            'global_id' : quote_braces(survey.global_id) if survey.global_id is not None else '',
            'qids_old' : '{' + '},{'.join(quoted_ids) + '}' if quoted_ids else '{NONE}',
            'qids' : '{' + '},{'.join(quoted_ids) + '}' if quoted_ids else '{}',
        })
    latex_override.close()

# This is a list, because the order is relevant!
ascii_to_latex = [
    ('{', '\\{'),
    ('}', '\\}'),
    ('\\', '{\\textbackslash}'),
    ('%', '\\%'),
    ('$', '\\$'),
    ('_', '\\_'),
    ('|', '{\\textbar}'),
    ('>', '{\\textgreater}'),
    ('<', '{\\textless}'),
    ('&', '\\&'),
    ('#', '\#'),
    ('^', '\\^{}'),
    ('~', '\\~{}'),
    ('"', '\\"{}'),
]

def raw_unicode_to_latex(string):
    """In addition to converting all unicode characters to LaTeX expressions
    this function also replaces some characters like newlines with their LaTeX
    equvivalent."""

    # We need to quote any special character (or replace it)
    for char, replacement in ascii_to_latex:
        string = string.replace(char, replacement)

    string = unicode_to_latex(string)

    string = str(string)

    # Replace many newlines with a paragraph marker
    string, count = re.subn('\n\n+', '\u2029', string, flags=re.MULTILINE)

    # Replace single newline with \\+newline
    string = string.replace('\n', '\\\\\n')

    # And remove the paragraph marker again (insert two newlines)
    string = string.replace('\u2029', '\n\n')

    return string.encode('ascii')

def run_engine(engine, texfile, cwd, inputs=[]):
    def _preexec_fn():
        if defs.latex_preexec_hook is not None:
            defs.latex_preexec_hook()

        inputs.extend(p for p in os.environ.get('TEXINPUTS', '').split(':') if p not in ['.', ''])

        if inputs:
            os.environ['TEXINPUTS'] = ':'.join(['.'] + inputs + [''])

    verbose = os.environ.get('VERBOSE', '0')
    if verbose in ['1', 'y']:
        mode = 'nonstopmode'
    else:
        mode = 'batchmode'
    subprocess.call([engine, '-halt-on-error',
                     '-interaction', mode, texfile],
                    cwd=cwd,
                    preexec_fn=_preexec_fn)


def compile(engine, texfile, cwd, inputs=[]):
    run_engine(engine, texfile, cwd, inputs)
    run_engine(engine, texfile, cwd, inputs)
    run_engine(engine, texfile, cwd, inputs)
    run_engine(engine, texfile, cwd, inputs)


