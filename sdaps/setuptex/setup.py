# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2010, Benjamin Berg <benjamin@sipsolutions.net>
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
import shutil
import glob
import subprocess

from sdaps import utils
from sdaps import model
from sdaps import log
from sdaps import paths

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

from sdaps.setup import buddies
import sdapsfileparser
from sdaps.setup import additionalparser


def write_latex_override_file(survey):
    # Create the sdaps.opt file.
    latex_override = open(survey.path('sdaps.opt'), 'w')
    latex_override.write('% This file exists to force the latex document into "final" mode.\n')
    latex_override.write('% It is parsed after the setup phase of the SDAPS class.\n\n')
    latex_override.write('\\@STAMPtrue\n')
    latex_override.write('\\@PAGEMARKtrue\n\n')
    latex_override.write('\setcounter{surveyidlshw}{%i}\n' % (survey.survey_id % (2 ** 16)))
    latex_override.write('\setcounter{surveyidmshw}{%i}\n' % (survey.survey_id / (2 ** 16)))
    latex_override.write('\def\surveyid{%i}\n' % (survey.survey_id))
    latex_override.write('% We turn of draft mode if questionnaire IDs are not printed.\n')
    latex_override.write('% Otherwise we turn it on explicitly so that noboday has wrong ideas.\n')
    latex_override.write('\\if@PrintQuestionnaireId\n')
    latex_override.write('\\@sdaps@drafttrue\n')
    latex_override.write('\\else\n')
    latex_override.write('\\@sdaps@draftfalse\n')
    latex_override.write('\\fi\n')
    latex_override.close()


def setup(survey, questionnaire_tex, additionalqobjects=None):
    if os.access(survey.path(), os.F_OK):
        log.error(_('The survey directory already exists'))
        return 1

    mimetype = utils.mimetype(questionnaire_tex)
    if mimetype != 'text/x-tex' and mimetype != '':
        log.warn(_('Unknown file type (%s). questionnaire_tex should be of type text/x-tex') % mimetype)
        log.warn(_('Will keep going, but expect failure!'))

    if additionalqobjects is not None:
        mimetype = utils.mimetype(additionalqobjects)
        if mimetype != 'text/plain' and mimetype != '':
            log.error(_('Unknown file type (%s). additionalqobjects should be text/plain') % mimetype)
            return 1

    # Add the new questionnaire
    survey.add_questionnaire(model.questionnaire.Questionnaire())

    # Create the survey directory, and copy the tex file.
    os.mkdir(survey.path())
    try:
        shutil.copy(questionnaire_tex, survey.path('questionnaire.tex'))

        write_latex_override_file(survey)

        # Copy class and dictionary files
        if paths.local_run:
            cls_file = os.path.join(paths.source_dir, 'tex', 'sdaps.cls')
            code128_file = os.path.join(paths.source_dir, 'tex', 'code128.tex')
            dict_files = os.path.join(paths.source_dir, 'tex', '*.dict')
            dict_files = glob.glob(dict_files)
        else:
            cls_file = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', 'sdaps.cls')
            code128_file = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', 'code128.tex')
            dict_files = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', '*.dict')
            dict_files = glob.glob(dict_files)

        shutil.copyfile(cls_file, survey.path('sdaps.cls'))
        shutil.copyfile(code128_file, survey.path('code128.tex'))
        for dict_file in dict_files:
            shutil.copyfile(dict_file, survey.path(os.path.basename(dict_file)))

        print _("Running pdflatex now twice to generate the questionnaire.")
        # First run in draftmode, no need to generate a PDF
        subprocess.call(['pdflatex', '-draftmode', '-halt-on-error',
                         '-interaction', 'batchmode', 'questionnaire.tex'],
                        cwd=survey.path())
        # And again, without the draft mode
        subprocess.call(['pdflatex', '-halt-on-error', '-interaction',
                         'batchmode', 'questionnaire.tex'],
                        cwd=survey.path())
        if not os.path.exists(survey.path('questionnaire.pdf')):
            print _("Error running \"pdflatex\" to compile the LaTeX file.")
            raise AssertionError('PDF file not generated')

        survey.defs.print_questionnaire_id = False
        survey.defs.print_survey_id = True

        # Parse qobjects
        try:
            sdapsfileparser.parse(survey)
        except Exception, e:
            log.error(_("Caught an Exception while parsing the SDAPS file. The current state is:"))
            print >>sys.stderr, unicode(survey.questionnaire)
            print >>sys.stderr, "------------------------------------"

            raise e

        # Parse additionalqobjects
        if additionalqobjects:
            additionalparser.parse(survey, additionalqobjects)

        # Last but not least calculate the survey id
        survey.calculate_survey_id()

        if not survey.check_settings():
            log.error(_("Some combination of options and project properties do not work. Aborted Setup."))
            shutil.rmtree(survey.path())
            return 1

        # We need to now rebuild everything so that the correct ID is at the bottom
        write_latex_override_file(survey)

        print _("Running pdflatex now twice to generate the questionnaire.")
        # First run in draftmode, no need to generate a PDF
        subprocess.call(['pdflatex', '-draftmode', '-halt-on-error',
                         '-interaction', 'batchmode', 'questionnaire.tex'],
                        cwd=survey.path())
        # And again, without the draft mode
        subprocess.call(['pdflatex', '-halt-on-error', '-interaction',
                         'batchmode', 'questionnaire.tex'],
                        cwd=survey.path())
        if not os.path.exists(survey.path('questionnaire.pdf')):
            log.error(_("Error running \"pdflatex\" to compile the LaTeX file."))
            raise AssertionError('PDF file not generated')

        # Print the result
        print survey.title

        for item in survey.info.items():
            print u'%s: %s' % item

        print unicode(survey.questionnaire)

        log.logfile.open(survey.path('log'))

        survey.save()
        log.logfile.close()
    except:
        log.error(_("An error occured in the setup routine. The survey directory still exists. You can for example check the questionnaire.log file for LaTeX compile errors."))
        raise

