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

from sdaps import template

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext


def cover(survey, output=None):

    story = template.story_title(survey)
    subject = []
    for key, value in survey.info.items():
        subject.append('%(key)s: %(value)s' % {'key': key, 'value': value})
    subject = '\n'.join(subject)

    if output:
        filename = output
    else:
        filename = survey.new_path('cover_%i.pdf')

    doc = template.DocTemplate(
        filename,
        _('SDAPS questionnaire'),
        {
            'title': survey.title,
            'subject': subject
        }
    )
    doc.build(story)


