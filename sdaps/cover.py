# -*- coding: utf8 -*-
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

import model
import script

from ugettext import ugettext, ungettext
_ = ugettext


parser = script.subparsers.add_parser("cover",
    help=_("Create a cover for the questionnaires."),
    description=_("""This command creates a cover page for questionnaires. All
    the metadata of the survey will be printed on the page."""))
parser.add_argument('-o', '--output',
    help=_("Filename to store the data to (default: cover_%%i.pdf)"))

@script.connect(parser)
@script.logfile
def cover(cmdline):
    import template

    survey = model.survey.Survey.load(cmdline['project'])

    story = template.story_title(survey)
    subject = []
    for key, value in survey.info.iteritems():
        subject.append(u'%(key)s: %(value)s' % {'key': key, 'value': value})
    subject = u'\n'.join(subject)

    if cmdline['output']:
        filename = cmdline['output']
    else:
        filename = survey.new_path('cover_%i.pdf')

    doc = template.DocTemplate(
        filename,
        _(u'sdaps questionnaire'),
        {
            'title': survey.title,
            'subject': subject
        }
    )
    doc.build(story)


