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

from sdaps import log
import xml.sax
import zipfile
import re

from sdaps import model
from sdaps.utils.latex import latex_to_unicode

QOBJECT_PREFIX = 'QObject'
ANSWER_PREFIX = 'Answer'
BOX = 'Box'
VARIABLE = 'Variable'
TEXTBOX = 'Textbox'
RANGE_PREFIX = 'Range'
INFO_PREFIX = 'Info-'
VERSION = 'SDAPSVersion'

index_re = re.compile(r'''^(?P<index>(?:[0-9]+\.)+)(?P<string>.*)$''')
arg_index_re = re.compile(r'''^(?P<arg>[^\[]*)(\[(?P<index>([0-9]+\.)*[0-9]+)\])?$''')


def get_index_and_string(string):
    match = index_re.match(string)
    if match is None:
        if string.startswith('XAUTO. '):
            return None, string[7:]
        return None, string

    string = match.group('string')
    index = match.group('index')
    index = index.split('.')[:-1]
    index = tuple([int(x) for x in index])

    return index, string

def parse(survey):

    # Usually the file will contain LaTeX macros for unicode characters, but
    # UTF-8 may also come through directly. Not sure when, but this is safe.
    # (see https://github.com/sdaps/sdaps/issues/208)
    sdaps_file = open(survey.path('questionnaire.sdaps'), encoding='utf-8')
    sdaps_data = sdaps_file.read()
    qobject = None
    auto_numbering_id = (0,)

    sdaps_data = sdaps_data.split('\n')

    if sdaps_data[0].startswith('['):
        lines = []
        for line in sdaps_data:
            # Ignore empty lines
            if not line:
                continue
            num, line = line.split(']', 1)
            num = int(num[1:])
            lines.append((num, line))

        lines.sort(key=lambda x: x[0])

        sdaps_data = [l[1] for l in lines]

    for line in sdaps_data:
        line = line.strip()
        if line == "":
            continue
        arg, value = line.split('=', 1)
        arg = arg.strip()
        value = value.strip()
        value = latex_to_unicode(value)

        match = arg_index_re.match(arg)
        if match is not None:
            arg = match.group('arg')
            index = match.group('index')
            if index is None:
                try:
                    survey.questionnaire.qobjects[-1]
                except IndexError:
                    pass
            else:
                index = tuple([int(s) for s in index.split('.')])
                qobject = survey.questionnaire.find_object(index)


        if arg == 'Title':
            survey.title = value
        elif arg == 'PrintQuestionnaireId':
            survey.defs.print_questionnaire_id = bool(int(value))
        elif arg == 'PrintSurveyId':
            survey.defs.print_survey_id = bool(int(value))
        elif arg == 'Pages':
            survey.questionnaire.page_count = int(value)
        elif arg == 'CheckMode':
            survey.defs.checkmode = value
            assert survey.defs.checkmode in model.survey.valid_checkmodes
        elif arg == 'GlobalID':
            survey.global_id = value
        elif arg == 'GlobalIDLabel':
            # Ignore for now
            pass
        elif arg == 'Duplex':
            survey.defs.duplex = (value.lower() == "true")
        elif arg == 'Style':
            survey.defs.style = value
            assert survey.defs.style in model.survey.valid_styles
        elif arg == "PageSize":
            args = value.split(',')
            args = [arg.strip() for arg in args]

            width, height = [round(float(arg[:-2]) / 72.27 * 25.4, 3) for arg in args]

            survey.defs.paper_width = width
            survey.defs.paper_height = height

        elif arg == "CornerMarkMargin":
            args = value.split(',')
            args = [arg.strip() for arg in args]

            left, right, top, bottom = [round(float(arg[:-2]) / 72.27 * 25.4, 3) for arg in args]

            survey.defs.corner_mark_left = left
            survey.defs.corner_mark_right = right
            survey.defs.corner_mark_top = top
            survey.defs.corner_mark_bottom = bottom

        elif arg.startswith(QOBJECT_PREFIX):
            index, string = get_index_and_string(value)
            if index:
                auto_numbering_id = index + (0,)
            else:
                auto_numbering_id = auto_numbering_id[:-1] + (auto_numbering_id[-1] + 1,)
                index = auto_numbering_id

            qobject_type = arg[len(QOBJECT_PREFIX) + 1:]

            qobject_type = qobject_type.lower().capitalize()

            qobject = getattr(model.questionnaire, qobject_type)
            assert issubclass(qobject, model.questionnaire.QObject)
            qobject = qobject()
            survey.questionnaire.add_qobject(qobject, new_id=index)
            qobject.setup.init()

            qobject.setup.question(string)
        elif arg == VARIABLE:
            assert qobject is not None

            qobject.setup.variable_name(value)

        elif arg.startswith(ANSWER_PREFIX):
            assert qobject is not None

            answer_type = arg[len(ANSWER_PREFIX) + 1:]

            qobject.setup.answer(value)

        elif arg.startswith(RANGE_PREFIX):
            assert qobject is not None
            assert isinstance(qobject, model.questionnaire.Range)

            idx, answer = value.split(',', 1)
            idx = int(idx)

            range_type = arg[len(RANGE_PREFIX) + 1:].lower()

            if range_type == 'lower':
                qobject.setup.set_lower(idx, answer)
            elif range_type == 'upper':
                qobject.setup.set_upper(idx, answer)
            else:
                raise AssertionError('File format error, %s has to be either lower or upper!' % RANGE_PREFIX)

        elif arg == BOX:
            args = value.split(',')
            args = [arg.strip() for arg in args]

            boxtype = args[0]
            # Convert to mm
            page = int(args[1])
            x, y, width, height = [float(arg[:-2]) / 72.27 * 25.4 for arg in args[2:6]]
            y = survey.defs.paper_height - y
            lw = None

            if boxtype == 'Textbox':
                box = model.questionnaire.Textbox()
                if len(args) == 9:
                    lw = args[6] if args[6] else None
                    box.var = args[7] if args[7] else None
                    box.value = int(args[8]) if args[8] else None
                else:
                    assert(len(args) == 6)
            elif boxtype == 'Codebox':
                box = model.questionnaire.Codebox()
                if len(args) == 9:
                    lw = args[6] if args[6] else None
                    box.var = args[7] if args[7] else None
                    box.value = int(args[8]) if args[8] else None
                else:
                    assert(len(args) == 6)
            else:
                box = model.questionnaire.Checkbox()
                if len(args) == 7:
                    box.form = args[6]
                elif len(args) == 10:
                    box.form = args[6]
                    lw = args[7] if args[7] else None
                    box.var = args[8] if args[8] else None
                    box.value = int(args[9]) if args[9] else None
                else:
                    assert(len(args) == 6)

            if lw:
                lw = float(lw[:-2]) / 72.27 * 25.4

            box.setup.setup(page, x, y, width, height, lw)
            qobject.setup.box(box)
        elif arg == VERSION:
            # Ignore for now.
            pass
        elif arg.startswith(INFO_PREFIX):
            # Metadata, from 1.9.9 onwards
            survey.info[arg[len(INFO_PREFIX):]] = value
        else:
            # Falltrough, it is some metadata:
            survey.info[arg] = value

    # Force duplex of for one page questionnaires
    if survey.questionnaire.page_count == 1:
        survey.defs.duplex = False

