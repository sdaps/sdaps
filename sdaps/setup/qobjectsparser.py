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

import xml.sax
import zipfile

from sdaps import model


QOBJECT_PREFIX = u'QObject'
ANSWER_PREFIX  = u'Answer'
BOXES = [u'Checkbox', u'Textbox']


class ContentHandler (xml.sax.ContentHandler) :

	def __init__ (self, survey, boxes) :
		self.survey = survey
		self.boxes = boxes
		self.active = 1
		self.qobject = None
		self.answer = None
		self.last_qobject = None
		self.chars = unicode()
		self.parent_styles = dict()

	def endDocument (self) :
		for qobject in self.survey.questionnaire.qobjects :
			qobject.setup.validate()

	def startElement (self, name, attrs) :
		self.setup_characters()
		if self.active and name == u'text:p' :
			qobject = attrs[u'text:style-name']
			if qobject in self.parent_styles :
				qobject = self.parent_styles[qobject]
			if qobject.startswith(QOBJECT_PREFIX) :
				qobject = qobject[len(QOBJECT_PREFIX)+1:]
				qobject = getattr(model.questionnaire, qobject)
				assert issubclass(qobject, model.questionnaire.QObject)
				self.qobject = qobject()
				self.survey.questionnaire.add_qobject(self.qobject)
				self.qobject.setup.init()
			elif qobject.startswith(ANSWER_PREFIX) :
				self.answer = self.last_qobject
		elif name == u'draw:frame' :
			self.active = 0
			if attrs[u'draw:style-name'] in BOXES or self.parent_styles[attrs[u'draw:style-name']] in BOXES :
				self.answer.setup.box(self.boxes.pop(0))
		elif name == u'style:style' and attrs.has_key(u'style:parent-style-name'):
			self.parent_styles[attrs[u'style:name']] = attrs[u'style:parent-style-name']

	def endElement (self, name) :
		self.setup_characters()
		if self.active and self.qobject and name == u'text:p' :
			self.last_qobject = self.qobject
			self.qobject = None
		elif self.active and self.answer and name == u'text:p' :
			self.answer = None
		elif name == u'draw:frame' :
			self.active = 1

	def setup_characters (self) :
		if self.active and self.chars :
			if self.qobject :
				self.qobject.setup.question(self.chars)
			elif self.answer :
				self.answer.setup.answer(self.chars)
		self.chars = unicode()

	def characters (self, chars) :
		if self.active and (self.qobject or self.answer) :
			self.chars += chars.strip()


def parse (survey, questionnaire_odt, boxes) :

	document = zipfile.ZipFile(questionnaire_odt, 'r')
	content = document.read('content.xml')
	document.close()

	handler = ContentHandler(survey, boxes)
	xml.sax.parseString(content, handler)
