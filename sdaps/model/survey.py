# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <post@christoph-simon.eu>
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

import bz2
import cPickle
import os
from sdaps import defs

from sdaps import log

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

valid_styles = ['classic', 'code128']

# Force a certain set of options using slots
class Defs (object) :
	__slots__ = ['paper_width', 'paper_height', 'print_questionnaire_id',
	             'print_survey_id', 'style', 'duplex']

	def get_survey_id_pos(self):
		assert(self.style == 'classic')

		y_pos = self.paper_height - defs.corner_mark_bottom - defs.corner_box_padding
		y_pos -= defs.codebox_height

		left_padding = defs.corner_mark_left + 2*defs.corner_box_padding + defs.corner_box_width
		right_padding = defs.corner_mark_right + 2*defs.corner_box_padding + defs.corner_box_width

		text_y_pos = y_pos + defs.codebox_text_baseline_shift
		x_center = left_padding + (self.paper_width - left_padding - right_padding) / 2.0

		msb_box_x = left_padding
		lsb_box_x = self.paper_width - right_padding - defs.codebox_width

		text_x_pos = left_padding + (self.paper_width - right_padding - left_padding) / 2

		return msb_box_x, lsb_box_x, y_pos, text_x_pos, text_y_pos

	def get_questionnaire_id_pos(self):
		assert(self.style == 'classic')

		msb_box_x, lsb_box_x, y_pos, text_x_pos, text_y_pos = self.get_survey_id_pos()

		if self.print_survey_id:
			# Just move the y positions up if neccessary
			y_pos -= defs.codebox_height + defs.corner_box_padding
			text_y_pos -= defs.codebox_height + defs.corner_box_padding

		return msb_box_x, lsb_box_x, y_pos, text_x_pos, text_y_pos


class Survey (object) :

	pickled_attrs = set(('sheets', 'defs', 'survey_id', 'questionnaire_ids', 'questionnaire'))

	def __init__ (self) :
		self.questionnaire = None
		self.sheets = list()
		self.title = unicode()
		self.info = dict()
		self.survey_id = 0
		self.global_id = None
		self.questionnaire_ids = list()
		self.index = 0
		self.defs = Defs()

	def add_questionnaire (self, questionnaire) :
		self.questionnaire = questionnaire
		questionnaire.survey = self

	def add_sheet (self, sheet) :
		self.sheets.append(sheet)
		sheet.survey = self

	def calculate_survey_id (self) :
		import hashlib
		md5 = hashlib.new('md5')

		for qobject in self.questionnaire.qobjects :
			qobject.calculate_survey_id(md5)

		# TODO: Remove compatibility feature at some point
		# Keep backward compatibility by not hashing "style" and "duplex" if
		# they are both set to their default value
		def_items_to_hash = list(self.defs.__slots__)
		if self.defs.style == 'classic' and \
		   self.defs.duplex == True or self.questionnaire.page_count == 1:
			def_items_to_hash.remove('style')
			def_items_to_hash.remove('duplex')

		for defs_slot in def_items_to_hash:
			if isinstance(self.defs.__getattribute__(defs_slot), float) :
				md5.update(str(round(self.defs.__getattribute__(defs_slot), 1)))
			else:
				md5.update(str(self.defs.__getattribute__(defs_slot)))

		self.survey_id = 0
		# This compresses the md5 hash to a 32 bit unsigned value, by
		# taking the lower two bits of each byte.
		for i, c in enumerate(md5.digest()) :
			self.survey_id += bool(ord(c) & 1) << (2 * i)
			self.survey_id += bool(ord(c) & 2) << (2 * i + 1)

	@staticmethod
	def load (survey_dir) :
		import ConfigParser
		file = bz2.BZ2File(os.path.join(survey_dir, 'survey'), 'r')
		survey = cPickle.load(file)
		file.close()
		survey.survey_dir = survey_dir

		# TODO: Remove compatibility feature at some point
		if not hasattr(survey.defs, 'style'):
			survey.defs.style = 'classic'
			survey.defs.duplex = (survey.questionnaire.page_count > 1)

		config = ConfigParser.SafeConfigParser()
		config.optionxform = str
		config.read(os.path.join(survey_dir, 'info'))
		survey.title = config.get('sdaps', 'title').decode('utf-8')

		# TODO: Remove compatibility feature at some point
		if config.has_option('sdaps', 'global_id'):
			survey.global_id = config.get('sdaps', 'global_id').decode('utf-8')
			if survey.global_id == '' or survey.global_id == 'None':
				survey.global_id = None
		else:
			survey.global_id = None

		survey.info = dict()
		for key, value in config.items('info'):
			survey.info[key.decode('utf-8')] = value.decode('utf-8')

		return survey

	@staticmethod
	def new (survey_dir) :
		survey = Survey()
		survey.survey_dir = survey_dir
		return survey

	def save (self) :
		import ConfigParser
		file = bz2.BZ2File(os.path.join(self.survey_dir, 'survey'), 'w')
		cPickle.dump(self, file, 2)
		file.close()

		# Hack to include comments. Set allow_no_value here, and add keys
		# with a '#' in the front and no value.
		config = ConfigParser.SafeConfigParser(allow_no_value=True)
		config.optionxform = str
		config.add_section('sdaps')
		config.add_section('info')
		config.add_section('defs')
		config.add_section('questionnaire')
		config.set('sdaps', 'title', self.title.encode('utf-8'))
		if self.global_id is not None:
			config.set('sdaps', 'global_id', self.global_id.encode('utf-8'))
		else:
			config.set('sdaps', 'global_id', '')

		for key, value in self.info.iteritems():
			config.set('info', key.encode('utf-8'), value.encode('utf-8'))

		config.set('defs', '# These values are not read back, they exist for information only!')
		for attr in self.defs.__slots__:
			config.set('defs', attr, str(getattr(self.defs, attr)).encode('utf-8'))

		config.set('questionnaire', '# These values are not read back, they exist for information only!')
		config.set('questionnaire', 'page_count', str(self.questionnaire.page_count))
		# Put the survey ID into "questionnaire". This seems sane even though
		# it is not stored there internally..
		config.set('questionnaire', 'survey_id', str(self.survey_id))

		config.write(open(os.path.join(self.survey_dir, 'info'), 'w'))

	def path (self, *path) :
		return os.path.join(self.survey_dir, *path)

	def new_path (self, path) :
		content = os.listdir(self.path())
		i = 1
		while path % i in content : i += 1
		return os.path.join(self.survey_dir, path % i)

	def get_sheet (self) :
		return self.sheets[self.index]

	sheet = property(get_sheet)

	def iterate (self, function, filter = lambda : True, *args, **kwargs) :
		'''call function once for each sheet
		'''
		for self.index in range(len(self.sheets)) :
			if filter() : function(*args, **kwargs)

	def iterate_progressbar (self, function, filter = lambda : True) :
		'''call function once for each sheet and display a progressbar
		'''
		print ungettext('%i sheet', '%i sheets', len(self.sheets)) % len(self.sheets)
		if len(self.sheets) == 0:
			return

		log.progressbar.start(len(self.sheets))

		for self.index in range(len(self.sheets)) :
			if filter() : function()
			log.progressbar.update(self.index + 1)

		print _('%f seconds per sheet') % (
			float(log.progressbar.elapsed_time) /
			float(log.progressbar.max_value)
		)

	def goto_sheet (self, sheet) :
		u'''goto the specified sheet object
		'''
		self.index = self.sheets.index(sheet)

	def goto_questionnaire_id (self, questionnaire_id) :
		u'''goto the sheet object specified by its questionnaire_id
		'''
		sheets = filter(
			lambda sheet: sheet.questionnaire_id == questionnaire_id,
			self.sheets
		)
		if len(sheets) == 1 :
			self.goto_sheet(sheets[0])
		else :
			raise ValueError

	def __getstate__ (self) :
		u'''Only pickle attributes that are in the pickled_attrs set.
		'''
		dict = self.__dict__.copy()
		keys = dict.keys()
		for key in keys :
			if not key in self.pickled_attrs :
				del dict[key]
		return dict

