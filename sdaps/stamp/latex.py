
import sys
import os
import subprocess
import tempfile
import shutil

from sdaps import log
from sdaps import paths
from sdaps import defs
import glob

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

def tex_quote_braces(string):
    return string.replace('{', '\\{').replace('}', '\\}')

def create_stamp_pdf(survey, output_filename, questionnaire_ids):

    if questionnaire_ids is None:
        log.warn(_("There should be no need to stamp a SDAPS Project that uses LaTeX and does not have different questionnaire IDs printed on each sheet.\nI am going to do so anyways."))

    # Temporary directory for TeX files.
    tmpdir = tempfile.mkdtemp()

    try:
        # Copy class and dictionary files
        tex_file = survey.path('questionnaire.tex')
        code128_file = survey.path('code128.tex')
        qrcode_file = survey.path('qrcode.tex')
        qrcode_script = survey.path('qrcode.py')
        cls_file = survey.path('sdaps.cls')
        dict_files = survey.path('*.dict')
        dict_files = glob.glob(dict_files)

        shutil.copyfile(tex_file, os.path.join(tmpdir, 'questionnaire.tex'))
        shutil.copyfile(code128_file, os.path.join(tmpdir, 'code128.tex'))
        shutil.copyfile(cls_file, os.path.join(tmpdir, 'sdaps.cls'))
        shutil.copyfile(qrcode_file, os.path.join(tmpdir, 'qrcode.tex'))
        shutil.copyfile(qrcode_script, os.path.join(tmpdir, 'qrcode.py'))
        os.chmod(os.path.join(tmpdir, 'qrcode.py'), 0755)

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
        latex_override.write('\def\globalid{%s}\n' % (tex_quote_braces(survey.global_id)) if survey.global_id is not None else '')
        latex_override.write('\\@STAMPtrue\n')
        latex_override.write('\\@PAGEMARKtrue\n')
        latex_override.write('\\@sdaps@draftfalse\n')
        if questionnaire_ids is not None:
            quoted_ids = [tex_quote_braces(str(id)) for id in questionnaire_ids]
            latex_override.write('\def\questionnaireids{{%s}}\n' % '},{'.join(quoted_ids))
        latex_override.close()

        print _("Running %s now twice to generate the stamped questionnaire.") % defs.latex_engine
        os.environ['TEXINPUTS'] = ':' + os.path.abspath(survey.path())
        subprocess.call([defs.latex_engine, '-halt-on-error', '-shell-escape',
                         '-interaction', 'batchmode',
                         os.path.join(tmpdir, 'questionnaire.tex')],
                        cwd=tmpdir)
        # And again
        subprocess.call([defs.latex_engine, '-halt-on-error', '-shell-escape',
                         '-interaction', 'batchmode',
                         os.path.join(tmpdir, 'questionnaire.tex')],
                        cwd=tmpdir)
        if not os.path.exists(os.path.join(tmpdir, 'questionnaire.pdf')):
            log.error(_("Error running \"%s\" to compile the LaTeX file.") % defs.latex_engine)
            raise AssertionError('PDF file not generated')

        shutil.move(os.path.join(tmpdir, 'questionnaire.pdf'), output_filename)

    except:
        log.error(_("An error occured during creation of the report. Temporary files left in '%s'." % tmpdir))

        raise

    shutil.rmtree(tmpdir)
