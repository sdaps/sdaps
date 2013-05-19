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

img_counter = 0


def output_image(box, tmpdir):
    global img_counter
    img = box.sheet.get_page_image(box.question.page_number)

    filename = box.question.questionnaire.survey.path(img.filename)

    mm_to_px = img.matrix.mm_to_px()
    x0, y0 = mm_to_px.transform_point(box.data.x, box.data.y)
    x1, y1 = mm_to_px.transform_point(box.data.x + box.data.width, box.data.y)
    x2, y2 = mm_to_px.transform_point(box.data.x, box.data.y + box.data.height)
    x3, y3 = mm_to_px.transform_point(box.data.x + box.data.width, box.data.y + box.data.height)

    x = int(min(x0, x1, x2, x3))
    y = int(min(y0, y1, y2, y3))
    width = int(math.ceil(max(x0, x1, x2, x3) - x))
    height = int(math.ceil(max(y0, y1, y2, y3) - y))

    img = image.get_a1_from_tiff(filename, img.tiff_page, img.rotated if img.rotated else False)
    output = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
    cr = cairo.Context(output)
    cr.set_source_rgb(1, 1, 1)
    cr.paint()

    cr.set_source_surface(img, -x, -y)
    cr.paint()

    img_counter += 1
    output.write_to_png(os.path.join(tmpdir, 'image-%i.png' % img_counter))
    return 'image-%i.png' % img_counter


class Questionnaire(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    name = 'report'
    obj_class = model.questionnaire.Questionnaire

    def init(self, small=0):
        self.small = small
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.report.init(small)

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


class QObject(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    name = 'report'
    obj_class = model.questionnaire.QObject

    def init(self, small):
        self.small = small

    def report(self, tmpdir):
        pass

    def write(self, out, tmpdir):
        pass

    def filters(self):
        return []


class Head(QObject):

    __metaclass__ = model.buddy.Register
    name = 'report'
    obj_class = model.questionnaire.Head

    def write(self, out, tmpdir):
        # Smarter numbering handling?
        out.write('\\section*{%s %s}\n' % (self.obj.id_str(), self.obj.title))


class Question(QObject):

    __metaclass__ = model.buddy.Register
    name = 'report'
    obj_class = model.questionnaire.Question

    def write_begin(self, out):
        # Smarter numbering handling?
        out.write('\\begin{question}{%s %s}\n' % (self.obj.id_str(), self.obj.question))

    def write_end(self, out):
        # Smarter numbering handling?
        out.write('\\end{question}\n\n')

    def write(self, out, tmpdir):
        self.write_begin(out)
        self.write_end(out)


class Choice(Question):

    __metaclass__ = model.buddy.Register
    name = 'report'
    obj_class = model.questionnaire.Choice

    def init(self, small):
        self.small = small
        self.text = ""

    def report(self, tmpdir):
        if not self.small:
            for box in self.obj.boxes:
                if (isinstance(box, model.questionnaire.Textbox) and
                        box.data.state):
                    img_file = output_image(box, tmpdir)
                    self.text += '\\freeform{%fmm}{%s}\n' % (box.data.width, img_file)

    def write_begin(self, out):
        # Smarter numbering handling?
        out.write('\\begin{choicequestion}{%s %s}\n' % (self.obj.id_str(), self.obj.question))

    def write_end(self, out):
        # Smarter numbering handling?
        out.write('\\end{choicequestion}\n\n')

    def write(self, out, tmpdir):
        self.write_begin(out)
        if self.obj.calculate.count:
            for box in self.obj.boxes:
                out.write('''\\choiceanswer{%s}{%f}\n''' % (box.text, self.obj.calculate.values[box.value]))
        self.write_end(out)

        out.write(self.text)

    def filters(self):
        for box in self.obj.boxes:
            yield u'%i in %s' % (box.value, self.obj.id_filter())


class Mark(Question):

    __metaclass__ = model.buddy.Register
    name = 'report'
    obj_class = model.questionnaire.Mark

    def write(self, out, tmpdir):
        Question.write_begin(self, out)

        if self.obj.calculate.count:
            out.write('\\pgfkeyssetvalue{/sdaps/mark/lower}{%s}\n' % (self.obj.answers[0]))
            out.write('\\pgfkeyssetvalue{/sdaps/mark/upper}{%s}\n' % (self.obj.answers[1]))
            out.write('\\pgfkeyssetvalue{/sdaps/mark/count}{%i}\n' % (self.obj.calculate.count))
            out.write('\\pgfkeyssetvalue{/sdaps/mark/stddev}{%f}\n' % (self.obj.calculate.standard_derivation))
            for i, fraction in sorted(self.obj.calculate.values.iteritems()):
                out.write('\\pgfkeyssetvalue{/sdaps/mark/%i/fraction}{%f}\n' % (i, fraction))
            out.write('\\pgfkeyssetvalue{/sdaps/mark/mean}{%f}\n' % (self.obj.calculate.mean))
            out.write('\n\\markanswer\n')

        Question.write_end(self, out)

    def filters(self):
        for x in range(6):
            yield u'%i == %s' % (x, self.obj.id_filter())


class Text(Question):

    __metaclass__ = model.buddy.Register
    name = 'report'
    obj_class = model.questionnaire.Text

    def init(self, small):
        self.small = small
        self.text = ""

    def report(self, tmpdir):
        if not self.small:
            for box in self.obj.boxes:
                if box.data.state:
                    img_file = output_image(box, tmpdir)
                    self.text += '\\freeform{%fmm}{%s}\n' % (box.data.width, img_file)

    def write(self, out, tmpdir):
        Question.write_begin(self, out)

        out.write(self.text)

        Question.write_end(self, out)


class Additional_FilterHistogram(Question):

    __metaclass__ = model.buddy.Register
    name = 'report'
    obj_class = model.questionnaire.Additional_FilterHistogram

    def write(self, tmpdir):
        Question.write_begin(self, out)

        if self.obj.calculate.count:
            for i in range(len(self.obj.calculate.values)):
                out.write('''\\choiceanswer{%s}{%f}{%f}\n''' %
                          (self.obj.answers[i], self.obj.calculate.values[i], self.obj.calculate.significant[i]))

        Question.write_end(self, out)

