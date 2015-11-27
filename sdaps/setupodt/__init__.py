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

u"""
Contains the functionality to create a new SDAPS project using an OpenOffice.org
document and its PDF Export.
"""

import os
import shutil

from sdaps.utils.mimetype import mimetype
from sdaps import model
from sdaps import log

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

from ..setup import buddies
from ..setup import additionalparser
from . import boxesparser
from . import qobjectsparser
from . import metaparser
from pdftools import pdffile


def setup(survey, questionnaire_odt, questionnaire_pdf, additionalqobjects, options):

    if os.access(survey.path(), os.F_OK):
        log.error(_('The survey directory already exists.'))
        return 1

    mime = mimetype(questionnaire_odt)
    if mime != 'application/vnd.oasis.opendocument.text' and mime not in ['', 'binary', 'application/octet-stream']:
        log.error(_('Unknown file type (%s). questionnaire_odt should be application/vnd.oasis.opendocument.text.') % mime)
        return 1

    mime = mimetype(questionnaire_pdf)
    if mime != 'application/pdf' and mime != '':
        log.error(_('Unknown file type (%s). questionnaire_pdf should be application/pdf.') % mime)
        return 1

    if additionalqobjects is not None:
        mime = mimetype(additionalqobjects)
        if mime != 'text/plain' and mime != '':
            log.error(_('Unknown file type (%s). additionalqobjects should be text/plain.') % mime)
            return 1

    # Add the new questionnaire
    survey.add_questionnaire(model.questionnaire.Questionnaire())

    # Parse the box objects into a cache
    boxes, page_count = boxesparser.parse(questionnaire_pdf)
    survey.questionnaire.page_count = page_count

    # Get the papersize
    doc = pdffile.PDFDocument(questionnaire_pdf)
    page = doc.read_page(1)
    survey.defs.paper_width = abs(page.MediaBox[0] - page.MediaBox[2]) / 72.0 * 25.4
    survey.defs.paper_height = abs(page.MediaBox[1] - page.MediaBox[3]) / 72.0 * 25.4
    survey.defs.print_questionnaire_id = options['print_questionnaire_id']
    survey.defs.print_survey_id = options['print_survey_id']

    survey.defs.style = options['style']
    survey.defs.checkmode = options['checkmode']
    # Force simplex if page count is one.
    survey.defs.duplex = False if page_count == 1 else options['duplex']

    survey.global_id = options['global_id']

    # Parse qobjects
    try:
        qobjectsparser.parse(survey, questionnaire_odt, boxes)
    except:
        log.error(_("Caught an Exception while parsing the ODT file. The current state is:"))
        print unicode(survey.questionnaire)
        print "------------------------------------"
        print _("If the dependencies for the \"annotate\" command are installed, then an annotated version will be created next to the original PDF file.")
        print "------------------------------------"

        # Try to make an annotation
        try:
            if questionnaire_pdf.lower().endswith('.pdf'):
                annotated_pdf = questionnaire_pdf[:-4] + '_annotated.pdf'
            else:
                # No .pdf ending? Just append the _annotated.pdf.
                annotated_pdf = questionnaire_pdf + '_annotated.pdf'

            import sdaps.annotate as annotate
            annotate.annotate(survey, questionnaire_pdf, annotated_pdf)
        except:
            # Well, whatever
            pass

        raise

    # Parse additionalqobjects
    if additionalqobjects:
        additionalparser.parse(survey, additionalqobjects)

    # Parse Metadata
    metaparser.parse(survey, questionnaire_odt)

    # Last but not least calculate the survey id
    survey.calculate_survey_id()

    if not survey.check_settings():
        log.error(_("Some combination of options and project properties do not work. Aborted Setup."))
        return 1

    # Print the result
    print survey.title

    for item in survey.info.items():
        print u'%s: %s' % item

    print unicode(survey.questionnaire)

    # Create the survey
    os.makedirs(survey.path())

    log.logfile.open(survey.path('log'))

    shutil.copy(questionnaire_odt, survey.path('questionnaire.odt'))
    shutil.copy(questionnaire_pdf, survey.path('questionnaire.pdf'))

    survey.save()
    log.logfile.close()

