# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008, 2011, Benjamin Berg <benjamin@sipsolutions.net>
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
This modules contains the functionality to create reports using LaTeX.
"""

import os
import tempfile
import shutil
import glob

from sdaps import model

from sdaps import clifilter
from sdaps import template
from sdaps import matrix
from sdaps import paths
from sdaps import defs
from sdaps.utils import latex

from sdaps.utils import paper
from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

from . import buddies
import codecs


def report(survey, filter, filename=None, papersize=None, small=0, suppress=None, tex_only=False):
    assert isinstance(survey, model.survey.Survey)

    # compile clifilter
    filter = clifilter.clifilter(survey, filter)

    # First: calculate buddies

    # init buddies
    survey.questionnaire.calculate.init()

    # iterate over sheets
    survey.iterate(
        survey.questionnaire.calculate.read,
        lambda: survey.sheet.valid and filter()
    )

    # do calculations
    survey.questionnaire.calculate.calculate()

    # Temporary directory for TeX files.
    if tex_only and filename:
        tmpdir = filename

        # Create directory
        os.makedirs(tmpdir)
    else:
        tmpdir = tempfile.mkdtemp(prefix='sdaps-report-')

    # Second: report buddies

    # init buddies
    survey.questionnaire.report.init(tmpdir, small, suppress)

    # Filename of output
    if filename is None and tex_only == False:
        filename = survey.new_path('report_%i.pdf')

    try:
        # iterate over sheets
        survey.iterate(
            survey.questionnaire.report.report,
            lambda: survey.sheet.valid and filter(),
            tmpdir
        )

        # Copy class and dictionary files
        if paths.local_run:
            cls_file = os.path.join(paths.source_dir, 'tex', 'sdapsreport.cls')
            dict_files = os.path.join(paths.build_dir, 'tex', '*.dict')
            dict_files = glob.glob(dict_files)
        else:
            cls_file = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', 'sdapsreport.cls')
            dict_files = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', '*.dict')
            dict_files = glob.glob(dict_files)

        shutil.copyfile(cls_file, os.path.join(tmpdir, 'sdapsreport.cls'))
        for dict_file in dict_files:
            shutil.copyfile(dict_file, os.path.join(tmpdir, os.path.basename(dict_file)))

        texfile = codecs.open(os.path.join(tmpdir, 'report.tex'), 'w', 'utf-8')

        author = _('author|Unknown')

        extra_info = []
        for key, value in survey.info.items():
            if key == 'Author':
                author = value
                continue

            extra_info.append('\\addextrainfo{%(key)s}{%(value)s}' % {'key': key, 'value': value})

        extra_info = '\n'.join(extra_info)
        texfile.write(r"""\documentclass[%(language)s,%(papersize)s]{sdapsreport}

    \usepackage{ifxetex}
    \ifxetex
    \else
      \usepackage[utf8]{inputenc}
    \fi
    \usepackage[%(language)s]{babel}

    \title{%(title)s}
    \subject{%(title)s}
    \author{%(author)s}

    \addextrainfo{%(turned_in)s}{%(count)i}
    %(extra_info)s

    \begin{document}

    \maketitle

    """ % {'language': _('tex language|english'),
           'title': _('sdaps report'),
           'turned_in': _('Turned in Questionnaires'),
           'title': survey.title,
           'author': author,
           'extra_info': extra_info,
           'count': survey.questionnaire.calculate.count,
           'papersize' : paper.get_tex_papersize(papersize)})

        survey.questionnaire.report.write(texfile, tmpdir)

        texfile.write(r"""
    \end{document}
    """)
        texfile.close()

        if tex_only:
            print(_("The TeX project with the report data is located at '%s'.") % tmpdir)
            return

        print(_("Running %s now multiple times to generate the report.") % survey.defs.engine)
        latex.compile(survey.defs.engine, 'report.tex', cwd=tmpdir)

        if not os.path.exists(os.path.join(tmpdir, 'report.pdf')):
            print(_("Error running \"%s\" to compile the LaTeX file.") % survey.defs.engine)
            raise AssertionError('PDF file not generated')

        shutil.move(os.path.join(tmpdir, 'report.pdf'), filename)

    except:
        print(_("An occured during creation of the report. Temporary files left in '%s'." % tmpdir))

        raise

    shutil.rmtree(tmpdir)

