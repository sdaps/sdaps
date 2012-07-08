
import sys
import os
import subprocess
import tempfile
import shutil

from sdaps import log
from sdaps import paths
import glob

from sdaps.ugettext import ugettext, ungettext
_ = ugettext


def create_stamp_pdf(survey, questionnaire_ids):
    # Filename of output
    filename = survey.new_path('stamped_%i.pdf')

    if questionnaire_ids is None:
        print _("There should be no need to stamp a SDAPS Project that uses LaTeX and does not have different questionnaire IDs printed on each sheet.\nI am going to do so anyways.")

    # Temporary directory for TeX files.
    tmpdir = tempfile.mkdtemp()

    try:
        # Copy class and dictionary files
        tex_file = survey.path('questionnaire.tex')
        code128_file = survey.path('code128.tex')
        cls_file = survey.path('sdaps.cls')
        dict_files = survey.path('*.dict')
        dict_files = glob.glob(dict_files)

        shutil.copyfile(tex_file, os.path.join(tmpdir, 'questionnaire.tex'))
        shutil.copyfile(code128_file, os.path.join(tmpdir, 'code128.tex'))
        shutil.copyfile(cls_file, os.path.join(tmpdir, 'sdaps.cls'))
        for dict_file in dict_files:
            shutil.copyfile(dict_file, os.path.join(tmpdir, os.path.basename(dict_file)))

        latex_override = open(os.path.join(tmpdir, 'report.tex'), 'w')

        # Similar to setuptex/setup.py, but we also set questionnaire IDs
        latex_override = open(os.path.join(tmpdir, 'sdaps.opt'), 'w')
        latex_override.write('% This file exists to force the latex document into "final" mode.\n')
        latex_override.write('% It is parsed after the setup phase of the SDAPS class.\n\n')
        latex_override.write('\setcounter{surveyidlshw}{%i}\n' % (survey.survey_id % (2 ** 16)))
        latex_override.write('\setcounter{surveyidmshw}{%i}\n' % (survey.survey_id / (2 ** 16)))
        latex_override.write('\def\surveyid{%i}\n' % (survey.survey_id))
        latex_override.write('\\@STAMPtrue\n')
        latex_override.write('\\@PAGEMARKtrue\n')
        latex_override.write('\\@sdaps@draftfalse\n')
        if questionnaire_ids is not None:
            latex_override.write('\def\questionnaireids{%s}\n' % ','.join([str(id) for id in questionnaire_ids]))
        latex_override.close()

        print _("Running pdflatex now twice to generate the stamped questionnaire.")
        # First run in draftmode, no need to generate a PDF
        subprocess.call(['pdflatex', '-draftmode', '-halt-on-error',
                         '-interaction', 'batchmode',
                         os.path.join(tmpdir, 'questionnaire.tex')],
                        cwd=tmpdir)
        # And again, without the draft mode
        subprocess.call(['pdflatex', '-halt-on-error', '-interaction',
                         'batchmode',
                         os.path.join(tmpdir, 'questionnaire.tex')],
                        cwd=tmpdir)
        if not os.path.exists(os.path.join(tmpdir, 'questionnaire.pdf')):
            print _("Error running \"pdflatex\" to compile the LaTeX file.")
            raise AssertionError('PDF file not generated')

        shutil.move(os.path.join(tmpdir, 'questionnaire.pdf'), filename)

    except:
        print _("An occured during creation of the report. Temporary files left in '%s'." % tmpdir)

        raise

    shutil.rmtree(tmpdir)

