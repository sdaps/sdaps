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

from sdaps import script


# Warning for questionnaires with more than 2 pages
# recognize can not join papers together!
# Dont shuffle them!!!!

@script.register
def add (survey, *files) :
	u'''files
	
	Add scanned questionnaires to the survey.
	
	files: TIFF-Images containing scanned questionnaires
	
	'''
	
	import Image
	import subprocess
	import os
	
	from sdaps import model
	
	assert isinstance(survey, model.survey.Survey)
		
	for file in files :
		
		print 'Processing', file
		
		try :
			image = Image.open(file)
		except IOError :
			print 'Unknown file format'
			print 'It should be TIFF'
			print 'Processing stopped'
			continue
		
		if image.format != 'TIFF' :
			print 'Unknown image file format', '(%s)' % image.format
			print 'It should be TIFF'
			print 'Processing stopped'
			continue
		
		if not image.mode == '1' :
			print 'Wrong data type inside TIFF', '(%s)' % image.mode
			print 'It should be black and white data'
			print 'Processing stopped'
			continue
		
		directory = survey.new_path('%i')
		os.mkdir(directory)
		tiffsplit = subprocess.Popen(
			['tiffsplit', file, directory + '/'],
			stdout = subprocess.PIPE, stderr = subprocess.PIPE
		)
		stdout, stderr = tiffsplit.communicate()

		for line in stdout.split('\n') :
			line = line.strip()
			if line: print line
		
		for line in stderr.split('\n') :
			if line.startswith('%s: Warning, incorrect count for field "DateTime"' % file) :
				continue
			line = line.strip()
			if line: print line
		
		img_list = os.listdir(directory)
		img_list.sort()
		c = survey.questionnaire.page_count
		assert len(img_list) % c == 0
		
		dir = os.path.basename(directory)
		for i in range(len(img_list) / c) :
			sheet = model.sheet.Sheet()
			survey.add_sheet(sheet)
			for j in range(c) :
				image = model.sheet.Image()
				sheet.add_image(image)
				image.filename = os.path.join(dir, img_list[c*i+j])
		
		print 'Done'
	
	survey.save()
	
