# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <christoph.simon@gmx.eu>
# Copyright (C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
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

import random

try:
	import cStringIO as StringIO
except:
	import StringIO

import subprocess
import os
import sys
import tempfile
import shutil
import math

import reportlab.pdfgen.canvas
from reportlab.lib import units

from sdaps import model
from sdaps import log
from sdaps import defs

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

mm = units.mm


def draw_survey_id (canvas, survey) :
	if 0 : assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)

	pos = survey.defs.get_survey_id_pos()

	canvas.saveState()
	canvas.setFont('Courier-Bold', 10.5)
	canvas.drawCentredString(pos[3] * mm, pos[4] * mm, _(u'Survey-ID: %i') % survey.survey_id)
	draw_codebox(canvas, pos[0] * mm, pos[2] * mm, survey.survey_id >> 16)
	draw_codebox(canvas, pos[1] * mm, pos[2] * mm, survey.survey_id & ((1 << 16) - 1))
	canvas.restoreState()


def draw_questionnaire_id (canvas, survey, questionnaire_id) :
	if 0 : assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)

	pos = survey.defs.get_questionnaire_id_pos()

	canvas.saveState()
	canvas.setFont('Courier-Bold', 10.5)
	canvas.drawCentredString(pos[3] * mm, pos[4] * mm, _(u'Questionnaire-ID: %i') % questionnaire_id)
	draw_codebox(canvas, pos[0] * mm, pos[2] * mm, questionnaire_id)
	draw_codebox(canvas, pos[1] * mm, pos[2] * mm, questionnaire_id)
	canvas.restoreState()


def draw_codebox (canvas, x, y, code) :
	if 0 : assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)
	size = defs.codebox_step * mm
	length = defs.codebox_length # 2 Bytes
	canvas.saveState()
	canvas.translate(x, y)
	canvas.rect(0, 0, defs.codebox_width * mm, defs.codebox_height * mm)
	for i in range(length) :
		if code & (1 << i) :
			canvas.rect((length - i - 1) * size, 0, size, defs.codebox_height * mm, stroke = 1, fill = 1)
	canvas.restoreState()


def draw_corner_marks (survey, canvas) :
	if 0 : assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)
	
	length = defs.corner_mark_length
	x, y = (defs.corner_mark_left, defs.corner_mark_top)
	canvas.line( x * mm,  y * mm, (x + length) * mm, y * mm)
	canvas.line( x * mm,  y * mm, x * mm, (y + length) * mm)

	x, y = (survey.defs.paper_width - defs.corner_mark_right, defs.corner_mark_top)
	canvas.line( x * mm,  y * mm, (x - length) * mm, y * mm)
	canvas.line( x * mm,  y * mm, x * mm, (y + length) * mm)

	x, y = (defs.corner_mark_left, survey.defs.paper_height - defs.corner_mark_bottom)
	canvas.line( x * mm,  y * mm, (x + length) * mm, y * mm)
	canvas.line( x * mm,  y * mm, x * mm, (y - length) * mm)

	x, y = (survey.defs.paper_width - defs.corner_mark_right, survey.defs.paper_height - defs.corner_mark_bottom)
	canvas.line( x * mm,  y * mm, (x - length) * mm, y * mm)
	canvas.line( x * mm,  y * mm, x * mm, (y - length) * mm)


# top left, top right, bottom left, bottom right
corners = [
	[0, 1, 1, 1],
	[1, 1, 0, 0],
	[1, 0, 1, 1],
	[1, 0, 1, 0],
	[1, 0, 0, 0],
	[0, 0, 0, 1],
]

def draw_corner_boxes (survey, canvas, page) :
	if 0 : assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)

	width = defs.corner_box_width
	height = defs.corner_box_height
	padding = defs.corner_box_padding

	corner_boxes_positions = [
		(defs.corner_mark_left + padding, defs.corner_mark_top + padding),
		(survey.defs.paper_width - defs.corner_mark_right - padding - width, defs.corner_mark_top + padding),
		(defs.corner_mark_left + padding, survey.defs.paper_height - defs.corner_mark_bottom - padding - height),
		(survey.defs.paper_width - defs.corner_mark_right - padding - width, survey.defs.paper_height - defs.corner_mark_bottom - padding - height)
	]
                                
	for i in xrange(4):
		x, y = corner_boxes_positions[i]
		canvas.rect(x * mm,  y * mm, width * mm, height * mm, fill = corners[page][i])

def stamp (survey, count = 0, used_ids = None) :
	# copy questionnaire_ids
	# get number of sheets to create
	if count :
		if not survey.defs.print_questionnaire_id :
			print _("You may not specify the number of sheets for surveys that do not print a quesitonnaire ID.")
			return 1

		if used_ids :
			used_ids = file(used_ids, 'r')
			survey.questionnaire_ids.extend([int(id) for id in used_ids.readlines()])
			used_ids.close()
		sheets = count
		max = pow(2, 16)
		min = max - 50000
		questionnaire_ids = range(0, max)
		for id in survey.questionnaire_ids :
			questionnaire_ids[id] = 0
		questionnaire_ids = [id for id in questionnaire_ids if id > min]
		random.shuffle(questionnaire_ids)
	else :
		if survey.defs.print_questionnaire_id :
			print _("You needs to specify the number of questionnaires to create when questionnaire are printed IDs.")
			return 1

		sheets = 1
		questionnaire_ids = None

	questionnaire_length = survey.questionnaire.page_count

	have_pdftk = False
	# Test if pdftk is present, if it is we can use it to be faster
	try:
		result = subprocess.Popen(['pdftk', '--version'], stdout=subprocess.PIPE)
		# Just assume pdftk is there, if it was executed sucessfully
		if result is not None:
			have_pdftk = True
	except OSError:
		pass

	if not have_pdftk:
		try:
			import pyPdf
		except:
			print >>sys.stderr, _(u'You need to have either pdftk or pyPdf installed. pdftk is the faster method.')
			sys.exit(1)

	# Write the "stamp" out to tmp.pdf if are using pdftk.
	if have_pdftk:
		stampsfile = file(survey.path('tmp.pdf'), 'wb')
	else:
		stampsfile = StringIO.StringIO()

	canvas = reportlab.pdfgen.canvas.Canvas(stampsfile, bottomup = False, pagesize=(survey.defs.paper_width * mm, survey.defs.paper_height * mm))
	# bottomup = False => (0, 0) is the upper left corner

	print ungettext(u'Creating stamp PDF for %i sheet', u'Creating stamp PDF for %i sheets', sheets) % sheets
	log.progressbar.start(sheets)
	for i in range(sheets) :
		for j in range(questionnaire_length) :
			draw_corner_marks(survey, canvas)
			draw_corner_boxes(survey, canvas, j)
			if j % 2 or questionnaire_length == 1:
				if questionnaire_ids :
					if j == 1 or questionnaire_length == 1 :
						# Only read a new ID for the first page.
						id = questionnaire_ids.pop()
						survey.questionnaire_ids.append(id)
					draw_questionnaire_id(canvas, survey, id)

				if survey.defs.print_survey_id:
					draw_survey_id(canvas, survey)
			canvas.showPage()
		log.progressbar.update(i + 1)

	canvas.save()

	print ungettext(u'%i sheet; %f seconds per sheet', u'%i sheet; %f seconds per sheet', log.progressbar.max_value) % (
		log.progressbar.max_value,
		float(log.progressbar.elapsed_time) /
		float(log.progressbar.max_value)
	)

	if have_pdftk:
		stampsfile.close()
		# Merge using pdftk
		print _("Stamping using pdftk")
		tmp_dir = tempfile.mkdtemp()

		for page in xrange(1, questionnaire_length + 1):
			print ungettext(u"pdftk: Splitting out page %d of each sheet.", u"pdftk: Splitting out page %d of each sheet.", page) % page
			args = []
			args.append('pdftk')
			args.append(survey.path('tmp.pdf'))
			args.append('cat')
			cur = page
			for i in range(sheets):
				args.append('%d' % cur)
				cur += questionnaire_length
			args.append('output')
			args.append(os.path.join(tmp_dir, 'stamp-%d.pdf' % page))

			subprocess.call(args)

		print _(u"pdftk: Splitting the questionnaire for watermarking.")
		subprocess.call(['pdftk', survey.path('questionnaire.pdf'), 'dump_data', 'output', os.path.join(tmp_dir, 'doc_data.txt')])
		for page in xrange(1, questionnaire_length + 1):
			subprocess.call(['pdftk', survey.path('questionnaire.pdf'), 'cat', '%d' % page, 'output', os.path.join(tmp_dir, 'watermark-%d.pdf' % page)])

		for page in xrange(1, questionnaire_length + 1):
			print ungettext(u"pdftk: Watermarking page %d of all sheets.", u"pdftk: Watermarking page %d of all sheets.", page) % page
			subprocess.call(['pdftk', os.path.join(tmp_dir, 'stamp-%d.pdf' % page), 'background', os.path.join(tmp_dir, 'watermark-%d.pdf' % page), 'output', os.path.join(tmp_dir, 'watermarked-%d.pdf' % page)])

		args = []
		args.append('pdftk')
		for page in xrange(1, questionnaire_length + 1):
			char = chr(ord('A') + page - 1)
			args.append('%s=' % char + os.path.join(tmp_dir, 'watermarked-%d.pdf' % page))

		args.append('cat')

		for i in range(sheets):
			for page in xrange(1, questionnaire_length + 1):
				char = chr(ord('A') + page - 1)
				args.append('%s%d' % (char, i + 1))

		args.append('output')
		args.append(os.path.join(tmp_dir, 'final.pdf'))
		print _(u"pdftk: Assembling everything into the final PDF.")
		subprocess.call(args)

		subprocess.call(['pdftk', os.path.join(tmp_dir, 'final.pdf'), 'update_info', os.path.join(tmp_dir, 'doc_data.txt'), 'output',  survey.new_path('stamped_%i.pdf')])

		# Remove tmp.pdf
		os.unlink(survey.path('tmp.pdf'))
		# Remove all the temporary files
		shutil.rmtree(tmp_dir)

	else:
		# Merge using pyPdf
		stamped = pyPdf.PdfFileWriter()
		stamped._info.getObject().update({
			pyPdf.generic.NameObject('/Producer'): pyPdf.generic.createStringObject(u'sdaps'),
			pyPdf.generic.NameObject('/Title'): pyPdf.generic.createStringObject(survey.title),
		})

		subject = []
		for key, value in survey.info.iteritems():
			subject.append(u'%(key)s: %(value)s' % {'key': key, 'value': value})
		subject = u'\n'.join(subject)

		stamped._info.getObject().update({
			pyPdf.generic.NameObject('/Subject'): pyPdf.generic.createStringObject(subject),
		})

		stamps = pyPdf.PdfFileReader(stampsfile)

		del stampsfile

		questionnaire = pyPdf.PdfFileReader(
			file(survey.path('questionnaire.pdf'), 'rb')
		)

		print _(u'Stamping using pyPdf. For faster stamping, install pdftk.')
		log.progressbar.start(sheets)

		for i in range(sheets) :
			for j in range(questionnaire_length) :
				s = stamps.getPage(i * questionnaire_length + j)
				if not have_pdftk:
					q = questionnaire.getPage(j)
					s.mergePage(q)
				stamped.addPage(s)
			log.progressbar.update(i + 1)

		stamped.write(open(survey.new_path('stamped_%i.pdf'), 'wb'))

		print ungettext(u'%i sheet; %f seconds per sheet', u'%i sheet; %f seconds per sheet', log.progressbar.max_value) % (
			log.progressbar.max_value,
			float(log.progressbar.elapsed_time) /
			float(log.progressbar.max_value)
		)

	survey.save()

