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

import cairo
import math
import os

from sdaps import clifilter
from sdaps import template
from sdaps import model
from sdaps import image

from sdaps import calculate

from sdaps.utils.latex import raw_unicode_to_latex, unicode_to_latex

from sdaps.utils.image import ImageWriter


def format_raw_text(text):
    from sdaps.setuptex import latexmap

class Questionnaire(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Questionnaire

    def init(self, img_dir, small=0, suppress=None):
        self.small = small

        self.textbox_writer = ImageWriter(img_dir, 'textbox-')

        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.report.init(small, suppress)

    def report(self, tmpdir):
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.report.report(tmpdir)

    def write(self, out, tmpdir):
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.report.write(out, tmpdir)

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

    def report(self, tmpdir):
        pass

    def write(self, out, tmpdir):
        pass

    def filters(self):
        return []


class Head(QObject, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Head

    def write(self, out, tmpdir):
        # Smarter numbering handling?
        out.write('\\section*{%s %s}\n' % (self.obj.id_str(), unicode_to_latex(self.obj.title)))


class Question(QObject, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Question

    def write_begin(self, out):
        # Smarter numbering handling?
        out.write('\\begin{question}{%s %s}\n' % (self.obj.id_str(), unicode_to_latex(self.obj.question)))

    def write_end(self, out):
        # Smarter numbering handling?
        out.write('\\end{question}\n\n')

    def write(self, out, tmpdir):
        self.write_begin(out)
        self.write_end(out)


class Choice(Question, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Choice

    def init(self, small, suppress):
        self.small = small
        self.suppress = suppress
        self.text = ""

    def report(self, tmpdir):
        if not self.small:
            for box in self.obj.boxes:
                if (isinstance(box, model.questionnaire.Textbox) and
                        box.data.state):
                    if box.data.text and self.suppress != 'substitutions':
                        text = raw_unicode_to_latex(box.data.text)
                        self.text += '\\freeformtext{%s}\n' % (text)
                    elif self.suppress != 'images':
                        img_file = self.obj.questionnaire.report.textbox_writer.output_box(box)
                        self.text += '\\freeform{%fmm}{%s}\n' % (box.data.width, img_file)

    def write_begin(self, out):
        # Smarter numbering handling?
        out.write('\\begin{choicequestion}{%s %s}\n' % (self.obj.id_str(), unicode_to_latex(self.obj.question)))

    def write_end(self, out):
        # Smarter numbering handling?
        out.write('\\end{choicequestion}\n\n')

    def write(self, out, tmpdir):
        self.write_begin(out)
        if self.obj.calculate.count:
            for box in self.obj.boxes:
                out.write('''\\choiceanswer{%s}{%.3f}\n''' % (unicode_to_latex(box.text), self.obj.calculate.values[box.value]))
        self.write_end(out)

        out.write(self.text)

    def filters(self):
        for box in self.obj.boxes:
            yield '%i in %s' % (box.value, self.obj.id_filter())

class Option(Choice, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Option

    def filters(self):
        for box in self.obj.boxes:
            yield '%i == %s' % (box.value, self.obj.id_filter())

class Range(Question, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Range

    def write(self, out, tmpdir):
        Question.write_begin(self, out)

        if self.obj.calculate.range_count:
            out.write('\\pgfkeyssetvalue{/sdaps/mark/range}{%s}\n' % (self.obj.calculate.range_max - self.obj.calculate.range_min + 1))
            out.write('\\pgfkeyssetvalue{/sdaps/mark/rangemin}{%s}\n' % (self.obj.calculate.range_min))
            out.write('\\pgfkeyssetvalue{/sdaps/mark/rangemax}{%s}\n' % (self.obj.calculate.range_max))
            out.write('\\pgfkeyssetvalue{/sdaps/mark/lower}{%s}\n' % (unicode_to_latex(self.obj.answers[0])))
            out.write('\\pgfkeyssetvalue{/sdaps/mark/upper}{%s}\n' % (unicode_to_latex(self.obj.answers[1])))
            out.write('\\pgfkeyssetvalue{/sdaps/mark/count}{%i}\n' % (self.obj.calculate.count))
            out.write('\\pgfkeyssetvalue{/sdaps/mark/stddev}{%.1f}\n' % (self.obj.calculate.standard_deviation))
            for key in range(self.obj.calculate.range_min, self.obj.calculate.range_max + 1):
                if key in self.obj.calculate.range_values:
                    fraction = self.obj.calculate.range_values[key]
                else:
                    fraction = 0
                out.write('\\pgfkeyssetvalue{/sdaps/mark/%i/fraction}{%.3f}\n' % (key, fraction))
            out.write('\\pgfkeyssetvalue{/sdaps/mark/mean}{%.1f}\n' % (self.obj.calculate.mean))
            out.write('\n\\markanswer\n')

        if self.obj.calculate.count > 0 and self.obj.calculate.values:
            out.write('\\begin{embedchoicequestion}\n')
            for box in self.obj.boxes:
                if box.value in self.obj.calculate.values:
                    out.write('''\\choiceanswer{%s}{%.3f}\n''' % (unicode_to_latex(box.text), self.obj.calculate.values[box.value]))
            out.write('\\end{embedchoicequestion}\n')

        Question.write_end(self, out)

    def filters(self):
        for x in range(len(self.obj.boxes)+1):
            yield '%i == %s' % (x, self.obj.id_filter())


class Text(Question, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Text

    def init(self, small, suppress):
        self.small = small
        self.suppress = suppress
        self.text = ""

    def report(self, tmpdir):
        if not self.small:
            for box in self.obj.boxes:
                if box.data.state:
                    if box.data.text and self.suppress != 'substitutions':
                        text = raw_unicode_to_latex(box.data.text)
                        self.text += '\\freeformtext{%s}\n' % (text)
                    elif self.suppress != 'images':
                        img_file = self.obj.questionnaire.report.textbox_writer.output_box(box)
                        self.text += '\\freeform{%fmm}{%s}\n' % (box.data.width, img_file)

    def write(self, out, tmpdir):
        Question.write_begin(self, out)

        out.write(self.text)

        Question.write_end(self, out)


class Additional_FilterHistogram(Question, metaclass=model.buddy.Register):

    name = 'report'
    obj_class = model.questionnaire.Additional_FilterHistogram

    def write(self, tmpdir):
        Question.write_begin(self, out)

        if self.obj.calculate.count:
            for i in range(len(self.obj.calculate.values)):
                out.write('''\\choiceanswer{%s}{%.3f}{%.3f}\n''' %
                          (unicode_to_latex(self.obj.answers[i]), self.obj.calculate.values[i], self.obj.calculate.significant[i]))

        Question.write_end(self, out)

