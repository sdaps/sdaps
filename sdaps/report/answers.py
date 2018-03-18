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

import io
from PIL import Image

from reportlab import pdfgen
from reportlab import platypus
from reportlab.lib import styles
from reportlab.lib import units
from reportlab.lib import pagesizes
from reportlab.lib import enums
from reportlab.lib import colors
from xml.sax.saxutils import escape

from sdaps import template
from sdaps import model
from sdaps import image

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

from . import flowables


mm = units.mm

stylesheet = dict(template.stylesheet)

stylesheet['Right'] = styles.ParagraphStyle(
    'Right',
    parent=stylesheet['Normal'],
    alignment=enums.TA_RIGHT,
)

stylesheet['Right_Highlight'] = styles.ParagraphStyle(
    'Right_Highlight',
    parent=stylesheet['Right'],
    textColor=colors.Color(255, 0, 0)
)

stylesheet['Normal_Highlight'] = styles.ParagraphStyle(
    'Normal_Highlight',
    parent=stylesheet['Normal'],
    textColor=colors.Color(255, 0, 0)
)


class Choice(platypus.Flowable):
    '''One answer of a choice
    '''

    box_width = 200
    box_height = 9
    box_depth = 5
    box_margin = 1
    value_width = 45
    gap = 6

    def __init__(self, answer, value, significant=0):
        platypus.Flowable.__init__(self)
        if significant:
            stylesheet_name = 'Right_Highlight'
        else:
            stylesheet_name = 'Right'
        self.answer = platypus.Paragraph(escape(answer), stylesheet[stylesheet_name])
        self.value = platypus.Paragraph(
            '%.2f %%' % (value * 100), stylesheet[stylesheet_name]
        )
        self.black_box = flowables.Box(
            value * self.box_width, self.box_height, self.box_depth,
            self.box_margin
        )
        self.black_box.transparent = 0
        self.black_box.fill = 1
        self.black_box.fill_color = (0.6, 0.6, 0.6)
        self.white_box = flowables.Box(
            (1 - value) * self.box_width, self.box_height, self.box_depth,
            self.box_margin
        )

    def wrap(self, available_width, available_height):
        self.width = available_width
        self.white_box.wrap(available_width, available_height)
        available_width -= self.white_box.width - self.white_box.cx
        self.black_box.wrap(available_width, available_height)
        available_width -= self.black_box.width
        available_width -= self.gap
        self.value.wrap(self.value_width, available_height)
        available_width -= self.value.width
        self.answer.wrap(available_width, available_height)
        self.height = max(
            self.answer.height, self.value.height,
            self.black_box.height + self.box_margin,
            self.white_box.height + self.box_margin
        )
        return self.width, self.height

    def draw(self):
        if 0:
            assert isinstance(self.canv, pdfgen.canvas.Canvas)
        self.answer.drawOn(
            self.canv,
            0,
            self.height / 2.0 - self.answer.height / 2.0
        )
        self.value.drawOn(
            self.canv,
            self.answer.width,
            self.height / 2.0 - self.value.height / 2.0
        )
        self.black_box.drawOn(
            self.canv,
            self.answer.width + self.value.width + self.gap,
            self.height / 2.0 - self.black_box.height / 2.0
        )
        self.white_box.drawOn(
            self.canv,
            self.answer.width + self.value.width + self.gap + self.black_box.width - self.black_box.cx,
            self.height / 2.0 - self.white_box.height / 2.0
        )


class Range(platypus.Flowable):
    '''
    -----                self.top_margin
    values(percent)    self.values_height
    -----                self.values_gap
    values(bars)        self.bars_height
    -----
    skala with mean        self.skala_height
    -----
    marks(1 - range)        self.marks_height
    -----
    '''

    margin = 6
    top_margin = 0
    left_margin = 12

    def __init__(self, range_min, range_max, values, answers, mean, standard_deviation, count, significant=0):
        platypus.Flowable.__init__(self)

        self.range_min = range_min
        self.range_max = range_max

        self.values = values
        self.mean = mean
        self.standard_deviation = standard_deviation
        self.count = count

        self.box_width = 40
        self.box_height = 60
        self.box_depth = 6

        self.mean_width = 2
        self.mean_height = 6

        self.values_height = 10
        self.values_gap = self.box_depth
        self.bars_height = max(self.values.values()) * self.box_height
        self.skala_height = self.mean_height
        self.marks_height = 10

        if significant:
            stylesheet_name = 'Normal_Highlight'
        else:
            stylesheet_name = 'Normal'

        self.answers_paragraph = \
            platypus.Paragraph(escape(' - '.join(answers)), stylesheet[stylesheet_name])
        self.count_paragraph = \
            platypus.Paragraph(_('Answers: %i') % self.count, stylesheet['Normal'])
        self.mean_paragraph = \
            platypus.Paragraph(_('Mean: %.2f') % self.mean, stylesheet['Normal'])
        self.stdd_paragraph = \
            platypus.Paragraph(_('Standard Deviation: %.2f') % self.standard_deviation, stylesheet['Normal'])

    def wrap(self, available_width, available_height):
        self.answers_paragraph.wrap(available_width, available_height)
        self.count_paragraph.wrap(available_width, available_height)
        self.mean_paragraph.wrap(available_width, available_height)
        self.stdd_paragraph.wrap(available_width, available_height)
        self.width = available_width # self.box_width * 5
        self.offset = self.width - self.box_width * len(self.values) - self.margin
        self.height = self.top_margin + self.values_height + self.values_gap + \
                      self.bars_height + self.skala_height + self.marks_height
        return self.width, self.height

    def draw(self):
        if 0:
            assert isinstance(self.canv, pdfgen.canvas.Canvas)
        self.canv.setFont("Times-Roman", 10)
        # mean
        mean = flowables.Box(self.mean_width, self.mean_height, self.box_depth)
        mean.transparent = 0
        mean.fill = 1
        mean.fill_color = (0.6, 0.6, 0.6)
        mean.drawOn(self.canv,
                    self.offset + (self.mean - 0.5) * self.box_width - self.mean_width / 2.0,
                    self.marks_height)
        # values

        for i, key in enumerate(range(self.range_min, self.range_max + 1)):
            if key in self.values:
                self.canv.drawCentredString(
                    self.offset + (i + 0.5) * self.box_width + self.box_depth * 0.5,
                    self.marks_height + self.skala_height + self.bars_height + self.values_gap,
                    '%.2f %%' % (self.values[key] * 100)
                )
        # bars
        for i, key in enumerate(range(self.range_min, self.range_max + 1)):
            if key in self.values:
                value = self.values[key]
            else:
                value = 0

            box = flowables.Box(self.box_width, value * self.box_height, self.box_depth)
            box.transparent = 0
            box.fill = 1
            box.fill_color = (0.6, 0.6, 0.6)
            box.drawOn(self.canv,
                       self.offset + i * self.box_width, self.marks_height + self.skala_height)
        # skala
        for i in range((self.range_max - self.range_min) * 10 + 1):
            if i % 10 == 0:
                self.canv.setLineWidth(0.2)
                self.canv.line(
                    self.offset + (i / 10.0 + 0.5) * self.box_width,
                    1 + self.marks_height,
                    self.offset + (i / 10.0 + 0.5) * self.box_width,
                    5 + self.marks_height
                )
            elif i % 5 == 0:
                self.canv.line(
                    self.offset + (i / 10.0 + 0.5) * self.box_width,
                    1.5 + self.marks_height,
                    self.offset + (i / 10.0 + 0.5) * self.box_width,
                    4.5 + self.marks_height
                )
            else:
                self.canv.line(
                    self.offset + (i / 10.0 + 0.5) * self.box_width,
                    2 + self.marks_height,
                    self.offset + (i / 10.0 + 0.5) * self.box_width,
                    4 + self.marks_height
                )
            if i % 10 == 0:
                self.canv.setLineWidth(0.1)
        # marks
        for i in range(1, len(self.values)+1):
            self.canv.drawCentredString(
                self.offset + (i - 0.5) * self.box_width, 0,
                '%i' % i
            )

        # statistics
        y_pos = self.marks_height + self.skala_height + self.bars_height + \
                self.values_gap + self.values_height
        self.answers_paragraph.drawOn(self.canv, self.left_margin, y_pos - 15)
        self.count_paragraph.drawOn(self.canv, self.left_margin, y_pos - 27)
        self.mean_paragraph.drawOn(self.canv, self.left_margin, y_pos - 39)
        self.stdd_paragraph.drawOn(self.canv, self.left_margin, y_pos - 51)


class Freeform(platypus.Flowable):

    cache = dict()

    def __init__(self, box):
        platypus.Flowable.__init__(self)

        assert isinstance(box, model.questionnaire.Textbox)
        assert box.data.state

        image = box.sheet.get_page_image(box.question.page_number)

        self.filename = box.question.questionnaire.survey.path(image.filename)
        self.tiff_page = image.tiff_page
        self.rotated = image.rotated

        mm_to_px = image.matrix.mm_to_px()
        x0, y0 = mm_to_px.transform_point(box.data.x, box.data.y)
        x1, y1 = mm_to_px.transform_point(box.data.x + box.data.width, box.data.y + box.data.height)

        self.bbox = (int(x0), int(y0), int(x1), int(y1))

        self.width = box.data.width * mm
        self.height = box.data.height * mm

    def wrap(self, available_width, available_height):
        self.available_width = available_width
        return self.available_width, self.height

    def draw(self):
        if 0:
            assert isinstance(self.canv, pdfgen.canvas.Canvas)
        if(self.filename, self.tiff_page, self.bbox) in self.cache:
            img = self.cache[(self.filename, self.tiff_page, self.bbox)]
        else:
            img = io.BytesIO(image.get_pbm(
                image.get_a1_from_tiff(
                    self.filename,
                    self.tiff_page,
                    self.rotated if self.rotated else False
                )
            ))
            img = Image.open(img).crop(self.bbox)
            self.cache[(self.filename, self.bbox)] = img
        self.canv.drawInlineImage(img, 0, 0, self.width, self.height)
        self.canv.setStrokeColorRGB(0.6, 0.6, 0.6)
        self.canv.line(0, 0, self.available_width, 0)
        self.canv.line(0, self.height, self.available_width, self.height)


class RawText(platypus.Paragraph):

    def __init__(self, text, *args, **kwargs):

        # Replace things like 

        text = escape(text)
        text = text.replace('\n', '<br/>')

        text = text

        platypus.Paragraph.__init__(self, text, *args, bulletText='•', **kwargs)

