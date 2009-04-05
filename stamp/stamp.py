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

import reportlab.pdfgen.canvas
from reportlab.lib import units
import pyPdf

import model
import log

mm = units.mm


def draw_survey_id (canvas, survey_id) :
	if 0 : assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)
	canvas.saveState()
	canvas.setFont('Courier-Bold', 10.5)
	canvas.drawCentredString(105 * mm, 281.5 * mm, u'Umfrage-ID: %i' % survey_id)
	draw_codebox(canvas, 19.5 * mm, 278.5 * mm, survey_id >> 16)
	draw_codebox(canvas, 134.5 * mm, 278.5 * mm, survey_id & ((1 << 16) - 1))
	canvas.restoreState()


def draw_questionnaire_id (canvas, questionnaire_id) :
	if 0 : assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)
	canvas.saveState()
	canvas.setFont('Courier-Bold', 10.5)
	canvas.drawCentredString(105 * mm, 275 * mm, u'Fragebogen-ID: %i' % questionnaire_id)
	draw_codebox(canvas, 19.5 * mm, 272 * mm, questionnaire_id)
	draw_codebox(canvas, 134.5 * mm, 272 * mm, questionnaire_id)
	canvas.restoreState()


def draw_codebox (canvas, x, y, code) :
	if 0 : assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)
	size = 3.5 * mm
	length = 2 * 8 # 2 Bytes
	canvas.saveState()
	canvas.translate(x, y)
	canvas.rect(0, 0, length * size, size)
	for i in range(length) : 
		if code & (1 << i) :
			canvas.rect((length - i - 1) * size, 0, size, size, stroke = 1, fill = 1)
	canvas.restoreState()


def draw_corner_marks (canvas) :	
	if 0 : assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)
	canvas.line( 10 * mm,  12 * mm, 30 * mm, 12 * mm)
	canvas.line( 10 * mm,  12 * mm, 10 * mm, 32 * mm)
	canvas.line(180 * mm,  12 * mm, 200 * mm, 12 * mm)
	canvas.line(200 * mm,  12 * mm, 200 * mm, 32 * mm)
	canvas.line( 10 * mm, 285 * mm, 30 * mm, 285 * mm)
	canvas.line( 10 * mm, 265 * mm, 10 * mm, 285 * mm)
	canvas.line(180 * mm, 285 * mm, 200 * mm, 285 * mm)
	canvas.line(200 * mm, 265 * mm, 200 * mm, 285 * mm)


# top left, top right, bottom left, bottom right
corners = [
	[0, 1, 1, 1],
	[1, 1, 0, 0],
	[1, 0, 1, 1],
	[1, 0, 1, 0],
	[1, 0, 0, 0],
	[0, 0, 0, 1],
]	

def draw_corner_boxes (canvas, page) :
	if 0 : assert isinstance(canvas, reportlab.pdfgen.canvas.Canvas)
	canvas.rect( 13 * mm,  15 * mm, 3.5 * mm, 3.5 * mm, fill = corners[page][0])
	canvas.rect(193.5 * mm,  15 * mm, 3.5 * mm, 3.5 * mm, fill = corners[page][1])
	canvas.rect( 13 * mm, 278.5 * mm, 3.5 * mm, 3.5 * mm, fill = corners[page][2])
	canvas.rect(193.5 * mm, 278.5 * mm, 3.5 * mm, 3.5 * mm, fill = corners[page][3])


def stamp (survey, count = 0, used_ids = None) :
	# Warning: Only even number of pages is allowed!!!

	# copy questionnaire_ids
	# get number of sheets to create
	if count :
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
		sheets = 1
	
	questionnaire = pyPdf.PdfFileReader(
		file(survey.path('questionnaire.pdf'), 'rb')
	)

	questionnaire_length = questionnaire.getNumPages()

	stampsfile = StringIO.StringIO()
	canvas = reportlab.pdfgen.canvas.Canvas(stampsfile, bottomup = False)
	# bottomup = False => (0, 0) is the upper left corner
	
	for i in range(sheets) :
		for j in range(questionnaire_length) :
			draw_corner_marks(canvas)
			draw_corner_boxes(canvas, j)
			if j % 2 :
				if questionnaire_ids :
					id = questionnaire_ids.pop()
					survey.questionnaire_ids.append(id)
					draw_questionnaire_id(canvas, id)
				draw_survey_id(canvas, survey.survey_id)
			canvas.showPage()

	canvas.save()
	
	survey.save()
	
	stamped = pyPdf.PdfFileWriter()
	stamped._info.getObject().update({
		pyPdf.generic.NameObject('/Producer'): pyPdf.generic.createStringObject(u'sdaps'),
		pyPdf.generic.NameObject('/Title'): pyPdf.generic.createStringObject(survey.title),
	})
	if u'Umfrage' in survey.info :
		stamped._info.getObject().update({
			pyPdf.generic.NameObject('/Subject'): pyPdf.generic.createStringObject(survey.info[u'Umfrage']),
		})

	stamps = pyPdf.PdfFileReader(stampsfile)
	
	del stampsfile

	print '%i sheets' % sheets
	log.progressbar.start(sheets)

	have_pdftk = False
	# Test if pdftk is present, if it is we can use it to be faster
	try:
		result = subprocess.Popen(['pdftk', '--version'], stdout=subprocess.PIPE)
		# Just assume pdftk is there, if it was executed sucessfully
		if result is not None:
			have_pdftk = True
	except OSError:
		pass

	if questionnaire_length != 2:
		have_pdftk = False
		print >>sys.stderr, "The fast code (that uses pdftk) can only handle two page questionnaires. Using slower fallback code."
	elif not have_pdftk:
		print >>sys.stderr, "If you install pdftk, the process will be much faster and the PDF will be smaller."
	
	for i in range(sheets) :
		for j in range(questionnaire_length) :
			s = stamps.getPage(i * questionnaire_length + j)
			if not have_pdftk:
				q = questionnaire.getPage(j)
				s.mergePage(q)
			stamped.addPage(s)
		log.progressbar.update(i + 1)

	print '%i sheets; %f seconds per sheet' % (
		log.progressbar.max_value,
		float(log.progressbar.elapsed_time) / 
		float(log.progressbar.max_value)
	)
	
	stamped.write(file(survey.path('tmp.pdf'), 'wb'))
	
	if have_pdftk:
		tmp_dir = tempfile.mkdtemp()
		try:
			print "pdftk: Splitting out the odd pages."
			subprocess.call(['pdftk', survey.path('tmp.pdf'), 'cat', '1-endodd', 'output', os.path.join(tmp_dir, 'odd.pdf')])
			print "pdftk: Splitting out the even pages."
			subprocess.call(['pdftk', survey.path('tmp.pdf'), 'cat', '1-endeven', 'output', os.path.join(tmp_dir, 'even.pdf')])

			# Extract the second page, as the first page is used for watermarking
			print "pdftk: Extracting the second page of the questionnaire for watermarking."
			subprocess.call(['pdftk', survey.path('questionnaire.pdf'), 'cat', '2', 'output', os.path.join(tmp_dir, 'even-watermark.pdf')])

			print "pdftk: Watermarking the odd pages."
			subprocess.call(['pdftk', os.path.join(tmp_dir, 'odd.pdf'), 'background', survey.path('questionnaire.pdf'), 'output', os.path.join(tmp_dir, 'odd-watermarked.pdf')])
			print "pdftk: Watermarking the even pages."
			subprocess.call(['pdftk', os.path.join(tmp_dir, 'even.pdf'), 'background', os.path.join(tmp_dir, 'even-watermark.pdf'), 'output', os.path.join(tmp_dir, 'even-watermarked.pdf')])

			args = []
			args.append('pdftk')
			args.append('A=' + os.path.join(tmp_dir, 'odd-watermarked.pdf'))
			args.append('B=' + os.path.join(tmp_dir, 'even-watermarked.pdf'))
			args.append('cat')

			for i in range(sheets):
				args.append('A%d' % (i + 1))
				args.append('B%d' % (i + 1))

			args.append('output')
			args.append(survey.new_path('stamped_%i.pdf'))
			print "pdftk: Assembling everything into the final PDF."
			subprocess.call(args)
		except OSError:
			print >>sys.stderr, "Something bad has happened!"
		# Remove tmp.pdf
		os.unlink(survey.path('tmp.pdf'))
		# Remove all the temporary files
		shutil.rmtree(tmp_dir)
	else:
		os.rename(survey.path('tmp.pdf'), survey.new_path('stamped_%i.pdf'))

