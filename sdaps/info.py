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


@script.register
@script.logfile
@script.doc(_(u'''[field [content]]

    Alter metadata.

    field: name of the field you whish to alter
    content: the new content for that field or empty if you want to delete the
        field.

    With no arguments, info will print a list of existing fields.
    '''))
def info(survey_dir, field=None, content=None):
    survey = model.survey.Survey.load(survey_dir)

    if field:
        field = field.decode('utf-8').strip()
        if content:
            content = content.decode('utf-8').strip()
            survey.info[field] = content
            print '%s = %s' % (field, content)
        else:
            del survey.info[field]
    else:
        print _(u'Existing fields: %s') % (u', '.join(survey.info.keys()))

    survey.save()

