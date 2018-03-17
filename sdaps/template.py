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

"""
Template
========

This modules contains templates for reportlab. These are used to create the
reports.
"""

from reportlab import platypus
from reportlab.lib import styles
from reportlab.lib import units
from reportlab.lib import pagesizes

mm = units.mm
PADDING = 15 * mm

class DocTemplate(platypus.BaseDocTemplate):

    def __init__(self, filename, title, metainfo={}, papersize=pagesizes.A4):
        platypus.BaseDocTemplate.__init__(
            self, filename,
            pagesize=papersize,
            leftMargin=0,
            rightMargin=0,
            topMargin=0,
            bottomMargin=0,
            **metainfo
        )
            #pageTemplates=[],
            #showBoundary=0,
            #allowSplitting=1,
            #title=None,
            #author=None,
            #_pageBreakQuick=1
        self.addPageTemplates(TitlePageTemplate(papersize, title))
        self.addPageTemplates(PageTemplate(papersize))


class TitlePageTemplate(platypus.PageTemplate):

    def __init__(self, papersize, title):
        self.title = title
        frames = [
            platypus.Frame(
                PADDING, papersize[1] / 2,
                papersize[0] - 2*PADDING, papersize[1] / 6,
                showBoundary=0
            ),
            platypus.Frame(
                PADDING, PADDING,
                papersize[0] - 2*PADDING, papersize[1] / 2 - PADDING,
                showBoundary=0
            ),
        ]
        platypus.PageTemplate.__init__(
            self,
            id='Title',
            frames=frames,
        )

    def beforeDrawPage(self, canvas, document):
        canvas.saveState()
        canvas.setFont('Times-Bold', 24)
        canvas.drawCentredString(
            document.width / 2.0,
            document.height - 50 * mm,
            self.title
        )
        canvas.restoreState()

    def afterDrawPage(self, canvas, document):
        pass


class PageTemplate(platypus.PageTemplate):

    def __init__(self, papersize):
        frames = [
            platypus.Frame(
                PADDING, PADDING,
                papersize[0] - 2*PADDING, papersize[1] - 2*PADDING,
                showBoundary=0
            )
        ]
        platypus.PageTemplate.__init__(
            self,
            id='Normal',
            frames=frames,
        )
        self.frames

    def beforeDrawPage(self, canvas, document):
        pass

    def afterDrawPage(self, canvas, document):
        pass


stylesheet = dict()

stylesheet['Normal'] = styles.ParagraphStyle(
    'Normal',
    fontName='Times-Roman',
    fontSize=10,
    leading=14,
)

stylesheet['Title'] = styles.ParagraphStyle(
    'Title',
    parent=stylesheet['Normal'],
    fontSize=18,
    leading=22,
    alignment=styles.TA_CENTER,
)


def story_title(survey, info=dict()):
    story = [
        platypus.Paragraph(str(line), stylesheet['Title'])
        for line in survey.title.split('\n')
    ]
    story += [
        platypus.FrameBreak(),
    ]

    keys = list(survey.info.keys())
    if keys:
        keys.sort()
        table = [
            [
                platypus.Paragraph(str(key), stylesheet['Normal']),
                platypus.Paragraph(str(survey.info[key]), stylesheet['Normal'])
            ]
            for key in keys
        ]
        story += [
            platypus.Table(table, colWidths=(50 * mm, None)),
        ]
    if info:
        story += [
            platypus.Spacer(0, 10 * mm)
        ]
        keys = list(info.keys())
        keys.sort()
        table = [
            [
                platypus.Paragraph(str(key), stylesheet['Normal']),
                platypus.Paragraph(str(info[key]), stylesheet['Normal'])
            ]
            for key in keys
        ]
        story += [
            platypus.Table(table, colWidths=(50 * mm, None)),
        ]

    story += [
        platypus.NextPageTemplate('Normal'),
        platypus.PageBreak()
    ]
    return story

