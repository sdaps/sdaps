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


class StylesHandler (xml.sax.ContentHandler) :
	
	def __init__ (self, survey) :
		self.active = 0
		self.survey = survey
		self.title = list()
	
	def startElement (self, name, attrs) :
		if name == u'style:header' :
			self.active = 1
		elif self.active and name == u'text:p' :
			self.title.append(unicode())
	
	def endElement (self, name) :
		if name == u'style:header' :
			self.active = 0
	
	def characters (self, chars) :
		if self.active :
			self.title[-1] += chars.strip()
	
	def endDocument (self) :
		self.survey.title = '\n'.join([x for x in self.title if x])


class MetaHandler (xml.sax.ContentHandler) :
	
	def __init__ (self, survey) :
		self.attribute = None
		self.survey = survey
		self.chars = unicode()
	
	def startElement (self, name, attrs) :
		if name == u'meta:user-defined' :
			if not attrs[u'meta:name'].startswith(u'Info') :
				self.attribute = attrs[u'meta:name']
				self.chars = unicode()
	
	def endElement (self, name) :
		if self.attribute and name == u'meta:user-defined' :
			self.survey.info[self.attribute] = self.chars
			self.attribute = None
	
	def characters (self, chars) :
		if self.attribute :
			self.chars += chars.strip()
	

def parse (survey, questionnaire_odt) :
	
	document = zipfile.ZipFile(questionnaire_odt, 'r')
	
	content = document.read('styles.xml')
	handler = StylesHandler(survey)
	xml.sax.parseString(content, handler)

	content = document.read('meta.xml')
	handler = MetaHandler(survey)
	xml.sax.parseString(content, handler)
	
	document.close()

