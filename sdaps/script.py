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

u'''

	sdaps - scripts for data acquisition with paper based surveys

	script - Registration center for sdaps scripts


Defining a script
=================

	from sdaps import script

	@script.register
	def my_script (survey, *arguments) :
		u\'''arguments
		description
		\'''
		from sdaps import buddies
		do the work

	if sdaps imports your module, the script will be registerd

	if sdaps calls your script, it should import any buddies, so that they will
	be registerd.

'''

import os

import log


scripts = dict()

def register (function) :
	u'''decorator to register a function as a script.

	sdaps will be able to call a registerd script.

	@register
	def function (survey, *args, **kwargs) :
		pass

	'''
	scripts[function.func_name] = function
	return function


def doc (docstring) :
	u'''decorator to add a docstring to a function.

	When using normal Python docstring syntax, gettext can not find it to
	translate it. Using @doc, you can pass your docstring through _() to make it
	translatable.

	@doc(_(u'docstring'))
	def function (*args, **kwargs) :
		pass

	'''
	def decorator (function) :
		function.func_doc = docstring
		return function
	return decorator


def logfile (function) :
	def decorated_function (survey_dir, *args, **kwargs) :
		log.logfile.open(os.path.join(survey_dir, 'log'))
		function(survey_dir, *args, **kwargs)
		log.logfile.close()
	decorated_function.func_name = function.func_name
	decorated_function.func_doc = function.func_doc
	return decorated_function


