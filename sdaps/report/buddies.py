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

import math

from reportlab import platypus
from reportlab.lib import styles
from reportlab.lib import colors
from reportlab.lib import units

from sdaps import clifilter
from sdaps import template
from sdaps import model

from xml.sax.saxutils import escape

from . import flowables
from . import answers

from sdaps import calculate


mm = units.mm


stylesheet = dict(template.stylesheet)

stylesheet['Head'] = styles.ParagraphStyle(
    'Head',
    stylesheet['Normal'],
    fontSize=12,
    leading=17,
    backColor=colors.lightgrey,
    spaceBefore=5 * mm,
)

stylesheet['Question'] = styles.ParagraphStyle(
    'Question',
    stylesheet['Normal'],
    spaceBefore=3 * mm,
    fontName='Times-Bold',
)

stylesheet['Text'] = styles.ParagraphStyle(
    'Text',
    stylesheet['Normal'],
    spaceBefore=1 * mm,
    spaceAfter=1 * mm,
    rightIndent=5 * mm,
    bulletIndent=2 * mm,
    leftIndent=5 * mm,
)


class Questionnaire(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Questionnaire

    def init(self, small=0, suppress=None):
        self.small = small
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.report.init(small, suppress)

    def report(self):
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.report.report()

    def story(self):
        story = list()
        # iterate over qobjects
        keeptogether_list = []
        for qobject in self.obj.qobjects:
            new, keeptogether = qobject.report.story()
            new = list(new)

            if len(new) == 0:
                continue

            if keeptogether:
                keeptogether_list.extend(new)
            else:
                if len(keeptogether_list):
                    add = new.pop(0)
                    if isinstance(add, platypus.KeepTogether):
                        keeptogether_list.extend(add._content)
                    else:
                        keeptogether_list.append(add)

                    story.append(platypus.KeepTogether(keeptogether_list))
                    keeptogether_list = []

                story.extend(new)

        story.extend(keeptogether_list)
        return story

    def filters(self):
        filters = list()
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            filters.extend(list(qobject.report.filters()))
        return filters


class QObject(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.QObject

    def init(self, small, suppress):
        self.small = small

    def report(self):
        pass

    def story(self):
        return [], False

    def filters(self):
        return []


class Head(QObject, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Head

    def story(self):
        return [
            platypus.Paragraph(
                '%s %s' % (self.obj.id_str(), escape(self.obj.title)),
                stylesheet['Head'])], True


class Question(QObject, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Question

    def story(self):
        return [
            platypus.Paragraph(
                '%s %s' % (
                    self.obj.id_str(), escape(self.obj.question)),
                stylesheet['Question'])], True


class Choice(Question, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Choice

    def init(self, small, suppress):
        self.small = small
        self.suppress = suppress
        self.text = list()

    def report(self):
        if not self.small:
            for box in self.obj.boxes:
                if (isinstance(box, model.questionnaire.Textbox) and
                        box.data.state):

                    if box.data.text and self.suppress != 'substitutions':
                        self.text.append(answers.RawText(box.data.text,
                                                         stylesheet['Text']))
                    elif self.suppress != 'images':
                        self.text.append(answers.Freeform(box))

    def story(self):
        story, tmp = Question.story(self)
        if self.obj.calculate.count:
            for box in self.obj.boxes:
                story.append(
                    answers.Choice(
                        box.text,
                        self.obj.calculate.values[box.value],
                        self.obj.calculate.significant[box.value]
                    )
                )
            story = [platypus.KeepTogether(story)]
            if len(self.text) > 0:
                story.append(platypus.Spacer(0, 3 * mm))
                story.extend(self.text)
        return story, False

    def filters(self):
        for box in self.obj.boxes:
            yield '%i in %s' % (box.value, self.obj.id_filter())

class Option(Question, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Option

    def filters(self):
        for box in self.obj.boxes:
            yield '%i == %s' % (box.value, self.obj.id_filter())

class Range(Option, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Range

    def report(self):
        pass

    def story(self):
        story, tmp = Question.story(self)
        if self.obj.calculate.range_count:
            story.append(answers.Range(
                self.obj.calculate.range_min,
                self.obj.calculate.range_max,
                self.obj.calculate.range_values,
                self.obj.answers,
                self.obj.calculate.mean,
                self.obj.calculate.standard_deviation,
                self.obj.calculate.count,
                self.obj.calculate.significant))

        if self.obj.calculate.count > 0 and self.obj.calculate.values:
            for box in self.obj.boxes:
                if box.value in self.obj.calculate.values:
                    story.append(
                        answers.Choice(
                            box.text,
                            self.obj.calculate.values[box.value],
                            False
                        )
                    )

        story = [platypus.KeepTogether(story)]
        return story, False


class Text(Question, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Text

    def init(self, small, suppress):
        self.small = small
        self.suppress = suppress
        self.text = list()

    def report(self):
        if not self.small:
            for box in self.obj.boxes:
                if box.data.state:
                    if box.data.text and self.suppress != 'substitutions':
                        self.text.append(answers.RawText(box.data.text,
                                                         stylesheet['Text']))
                    elif self.suppress != 'images':
                        self.text.append(answers.Freeform(box))

    def story(self):
        story, tmp = Question.story(self)
        if len(self.text) > 0:
            story.append(self.text[0])
            story = [platypus.KeepTogether(story)]
        if len(self.text) > 1:
            story.extend(self.text[1:])
        return story, False


class Additional_FilterHistogram(Question, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Additional_FilterHistogram

    def story(self):
        story, tmp = Question.story(self)
        if self.obj.calculate.count:
            for i in range(len(self.obj.calculate.values)):
                story.append(
                    answers.Choice(
                        self.obj.answers[i],
                        self.obj.calculate.values[i],
                        self.obj.calculate.significant[i]
                    )
                )
            story = [platypus.KeepTogether(story)]
        return story, False
