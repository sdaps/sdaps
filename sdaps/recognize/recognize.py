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

from sdaps import model

import buddies

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

def reorder_data(survey):
	id_to_image_map = dict()

	for sheet_num, sheet in enumerate(survey.sheets):
		assert len(sheet.images) == survey.questionnaire.page_count

		for image_num, image in enumerate(sheet.images):
			# We always have two images at the same time
			# ie. we assume duplex printing and scanning!
			if not hasattr(image, 'questionnaire_id'):
				continue
			# insert into map
			info = (sheet_num, image_num - image_num % 2, image.page_number)

			if id_to_image_map.haskey(image.questionnaire_id):
				id_to_image_map[image.questionnaire_id].append(info)
			else:
				id_to_image_map[image.questionnaire_id] = list(info)

	# Check sanity (ie. we never have too many images per sheet, etc.)
	# We just do not sort these right now.
	# TODO: Also mark them as invalid or something?
	broken_ids = set()
	for id, info_list in id_to_image_map.iteritems():
		if len(info_list) != survey.questionnaire.page_count / 2:
			broken_ids.add(id)
			continue

		pages = set()
		for page in info_list:
			if page[2] in pages:
				broken_ids.add(id)
				continue

			pages.add(page[2])

	# Always permute the correct item at the place, and update the information
	# for the permuted pair.
	# We do not try to find a minimal permutation that solves the problem.
	for pos, id, info_list in enumerate(id_to_image_map.iteritems()):
		if id in broken_ids:
			continue

		# We move the item to position "pos", this way all the clean ones
		# are at the start of the data

		new_surface_list = []
		for img_pos, page in enumerate(info_list):
			# two images at a time
			img_pos = img_pos * 2

			new_surface_list.append(survey.sheets[page[0]].images[page[1]])
			new_surface_list.append(survey.sheets[page[0]].images[page[1] + 1])

			# And move the current one over
			survey.sheets[page[0]].images[page[1]] = survey.sheets[pos][img_pos]
			survey.sheets[page[0]].images[page[1]+1] = survey.sheets[pos][img_pos+1]

			# Now update the reference in the dictionary
			if hasattr(survey.sheets[page[0]].images[page[1]], 'questionnaire_id'):
				moved_id = survey.sheets[page[0]].images[page[1]].questionnaire_id
				moved_page_number = survey.sheets[page[0]].images[page[1]].page_number
			else:
				moved_id = survey.sheets[page[0]].images[page[1]+1].questionnaire_id
				moved_page_number = survey.sheets[page[0]].images[page[1]+1].page_number

			# If it is broken, whatever, we will not touch it again anways
			if not moved_id in broken_ids:
				# Find which tuple needs updating, and update it
				for i in xrange(len(id_to_image_map[moved_id])):
					if id_to_image_map[moved_id][i][2] == moved_page_number:
						id_to_image_map[moved_id][i] = (page[0], page[1], moved_page_number)


def recognize (survey, *args) :
	# iterate over sheets
	reorder = False

	# TODO: Proper option parsing. (see add.py)
	if len(args) != 0:
		if len(args) == 1:
			if args[0] != '--reorder':
				raise AssertionError
			else:
				reorder = True
		else:
			raise AssertionError

	if reorder and survey.questionnaire.page_count > 2 and survey.defs.print_questionnaire_id:
		print _("Reading in all images to get the questionnaire IDs")
		survey.iterate_progressbar(survey.questionnaire.recognize.read_questionnaire_ids)
		print _("Now reordering the data internally for further processing.")
		reorder_data(survey)
		print _("Done.")

	survey.iterate_progressbar(survey.questionnaire.recognize.recognize)
	survey.save()

