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

from sdaps import csv

from sdaps import model


class Questionnaire (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'csvdata'
	obj_class = model.questionnaire.Questionnaire
	
	def export_header (self) :
		header = ['questionnaire_id']
		for qobject in self.obj.qobjects :
			header.extend(qobject.csvdata.export_header())
		self.file = file(self.obj.survey.new_path('data_%i.csv'), 'w')
		self.csv = csv.DictWriter(self.file, header)
		self.csv.writerow(dict([(value, value) for value in header]))
	
	def export_data (self) :
		data = {'questionnaire_id' : str(self.obj.sheet.questionnaire_id)}
		for qobject in self.obj.qobjects :
			data.update(qobject.csvdata.export_data())
		self.csv.writerow(data)
	
	def export_finish (self) :
		del self.csv
		self.file.close()

	def import_data (self, data) :
		try :
			self.obj.survey.goto_questionnaire_id(int(data['questionnaire_id']))
		except ValueError :
			# The sheet does not exist
			# Ignore it
			pass
		else :
			for qobject in self.obj.qobjects :
				qobject.csvdata.import_data(data)


class QObject (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'csvdata'
	obj_class = model.questionnaire.QObject

	def export_header (self) :
		return []

	def export_data (self) :
		return []

	def import_data (self, data) :
		pass

	
class Choice (model.buddy.Buddy) :	

	__metaclass__ = model.buddy.Register
	name = 'csvdata'
	obj_class = model.questionnaire.Choice

	def export_header (self) :
		return ['%i_%i_%i' % box.id for box in self.obj.boxes]

	def export_data (self) :
		return dict([('%i_%i_%i' % box.id, '%i' % box.data.state) for box in self.obj.boxes])

	def import_data (self, data) :
		for box in self.obj.boxes :
			if '%i_%i_%i' % box.id in data :
				box.data.state = int(data['%i_%i_%i' % box.id])


class Mark (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'csvdata'
	obj_class = model.questionnaire.Mark

	def export_header (self) :
		return ['%i_%i' % self.obj.id]

	def export_data (self) :
		return {'%i_%i' % self.obj.id : '%i' % self.obj.get_answer()}

	def import_data (self, data) :
		if '%i_%i' % self.obj.id in data :
			self.obj.set_answer(int(data['%i_%i' % self.obj.id]))


class Additional_Mark (model.buddy.Buddy) :

	__metaclass__ = model.buddy.Register
	name = 'csvdata'
	obj_class = model.questionnaire.Additional_Mark

	def export_header (self) :
		return ['%i_%i' % self.obj.id]

	def export_data (self) :
		return {'%i_%i' % self.obj.id : '%i' % self.obj.get_answer()}

	def import_data (self, data) :
		if '%i_%i' % self.obj.id in data :
			self.obj.set_answer(int(data['%i_%i' % self.obj.id]))

