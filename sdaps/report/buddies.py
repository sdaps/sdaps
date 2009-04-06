# -*- coding: utf-8 -*-
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

import math

from reportlab import platypus
from reportlab.lib import styles
from reportlab.lib import colors
from reportlab.lib import units

from sdaps import template

from sdaps import model

import flowables
import answers


mm = units.mm


stylesheet = dict(template.stylesheet)

stylesheet['Head'] = styles.ParagraphStyle(
	'Head',
	stylesheet['Normal'],
	fontSize = 12,
	leading = 17,
	backColor = colors.lightgrey,
	spaceBefore = 5 * mm,
)

stylesheet['Question'] = styles.ParagraphStyle(
	'Question',
	stylesheet['Normal'],
	spaceBefore = 3 * mm,
	fontName = 'Times-Bold',
)


class Questionnaire (model.buddy.Buddy) :
	
	__metaclass__ = model.buddy.Register
	name = 'report'
	obj_class = model.questionnaire.Questionnaire
	
	def init (self, small = 0) :
		self.count = 0
		self.small = small
		# iterate over qobjects
		for qobject in self.obj.qobjects :
			qobject.report.init(small)
	
	def report (self) :
		self.count += 1
		# iterate over qobjects
		for qobject in self.obj.qobjects :
			qobject.report.report()
	
	def calculate (self) :
		# iterate over qobjects
		for qobject in self.obj.qobjects :
			qobject.report.calculate()

	def reference (self) :
		# iterate over qobjects
		for qobject in self.obj.qobjects :
			qobject.report.reference()

	def story (self) :
		story = list()
		# iterate over qobjects
		for qobject in self.obj.qobjects :
			story.extend(list(qobject.report.story()))
		return story

	def filters (self) :
		filters = list()
		# iterate over qobjects
		for qobject in self.obj.qobjects :
			filters.extend(list(qobject.report.filters()))
		return filters


class QObject (model.buddy.Buddy) :
	
	__metaclass__ = model.buddy.Register
	name = 'report'
	obj_class = model.questionnaire.QObject
	
	def init (self, small) :
		pass
	
	def report (self) :
		pass

	def calculate (self) :
		pass
	
	def reference (self) :
		pass
	
	def story (self) :
		return []

	def filters (self) :
		return []
	

class Head (QObject) :
	
	__metaclass__ = model.buddy.Register
	name = 'report'
	obj_class = model.questionnaire.Head
	
	def story (self) :
		return [
			platypus.Paragraph(u'%i. %s' % (self.obj.id[0], self.obj.title), stylesheet['Head'])
		]

	
class Question (QObject) :
	
	__metaclass__ = model.buddy.Register
	name = 'report'
	obj_class = model.questionnaire.Question
	
	def story (self) :
		return [
			platypus.Paragraph(u'%i.%i %s' % (self.obj.id[0], self.obj.id[1], self.obj.question), stylesheet['Question']),
		]


class Choice (Question) :	
	
	__metaclass__ = model.buddy.Register
	name = 'report'
	obj_class = model.questionnaire.Choice
	
	def init (self, small) :
		self.small = small
		self.values = dict([(box.value, 0) for box in self.obj.boxes])
		self.text = list()
		self.count = 0
	
	def report (self) :
		for item in self.obj.get_answer() :
			self.values[item] += 1
		for box in self.obj.boxes :
			if isinstance(box, model.questionnaire.Textbox) and box.data.state :
				self.text.append(answers.Text(box))
		self.count += 1

	def calculate (self) :
		if self.count :
			self.significant = dict()
			for value in self.values :
				self.values[value] = self.values[value] / float(self.count)
				if hasattr(self, 'ref_count') and self.ref_count :
					# c = abs(self.values[value] - self.ref_values[value]) / pow(self.ref_standard_derivation, 2)
					# a = 0.1
					# libm = ctypes.CDLL("libm.so")
					# libm.erf.restype = ctypes.c_double
					# P = libm.erf(ctypes.c_double(c))				
					# self.significant = not (P <= a)
					self.significant[value] = abs(self.values[value] - self.ref_values[value]) > 0.1
				else :
					self.significant[value] = 0

	def reference (self) :
		if self.count :
			self.ref_values = self.values
			self.ref_count = self.count
	
	def filters (self) :
		for box in self.obj.boxes :
			yield u'%i in _%i_%i' % (box.value, self.obj.id[0], self.obj.id[1])
	
	def story (self) :
		story = Question.story(self)
		if self.count :
			for box in self.obj.boxes :
				story.append(
					answers.Choice(
						box.text,
						self.values[box.value],
						self.significant[box.value]
					)
				)
			story = [platypus.KeepTogether(story)]
			if not self.small and len(self.text) > 0 :
				story.append(platypus.Spacer(0, 3 * mm))
				story.extend(self.text)
		return story


class Mark (Question) :
	
	__metaclass__ = model.buddy.Register
	name = 'report'
	obj_class = model.questionnaire.Mark
	
	def init (self, small) :
		self.small = small
		self.values = dict([(x, 0) for x in range(1, 6)])
		self.count = 0
	
	def report (self) :
		answer = self.obj.get_answer()
		if answer :
			self.values[answer] += 1
			self.count += 1

	def calculate (self) :
		if self.count :
			for mark in self.values :
				self.values[mark] = self.values[mark] / float(self.count)
			self.mean = sum([mark * value for mark, value in self.values.items()])
			self.standard_derivation = math.sqrt(sum([value * pow(mark - self.mean, 2) for mark, value in self.values.items()]))
			if hasattr(self, 'ref_count') and self.ref_count :
				# c = abs(self.mean - self.ref_mean) / pow(self.ref_standard_derivation, 2)
				# a = 0.1
				# libm = ctypes.CDLL("libm.so")
				# libm.erf.restype = ctypes.c_double
				# P = libm.erf(ctypes.c_double(c))				
				# self.significant = not (P <= a)
				self.significant = abs(self.mean - self.ref_mean) > 0.1
			else :
				self.significant = 0
	
	def reference (self) :
		if self.count :
			self.ref_count = self.count
			self.ref_mean = self.mean
			self.ref_standard_derivation = self.standard_derivation
	
	def filters (self) :
		for x in range(6) :
			yield u'%i == _%i_%i' % (x, self.obj.id[0], self.obj.id[1])
	
	def story (self) :
		story = Question.story(self)
		if self.count :
			story.append(answers.Mark(
				self.values.values(), self.obj.answers, self.mean, self.standard_derivation, self.count,
				self.significant
			))
			story = [platypus.KeepTogether(story)]
		return story


class Text (Question) :
	
	__metaclass__ = model.buddy.Register
	name = 'report'
	obj_class = model.questionnaire.Text
	
	def init (self, small) :
		self.small = small
		self.text = list()
	
	def report (self) :
		for box in self.obj.boxes :
			if box.data.state :
				self.text.append(answers.Text(box))
	
	def story (self) :
		story = Question.story(self)
		if not self.small :
			if len(self.text) > 0 :
				story.append(self.text[0])
			story = [platypus.KeepTogether(story)]
			if len(self.text) > 1 :
				story.extend(self.text[1:])
		return story


class Additional_Mark (Mark) :
	
	__metaclass__ = model.buddy.Register
	name = 'report'
	obj_class = model.questionnaire.Additional_Mark
	
