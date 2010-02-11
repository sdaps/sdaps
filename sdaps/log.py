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
This module alters sys.stdout and sys.stderr to copy all output into a logfile.
'''

import sys
import time
import StringIO


class Copier (object) :
	'''copy all data going through the pipe into a logfile'''

	def __init__ (self, pipe, logfile) :
		self.pipe = pipe
		self.logfile = logfile

	def write (self, data) :
		self.pipe.write(data)
		self.logfile.write(data)


class Wiper (object) :
	'''wipe out the progressbar before forwarding data through the pipe'''

	def __init__ (self, pipe, progressbar) :
		self.pipe = pipe
		self.progressbar = progressbar

	def write (self, data) :
		if self.progressbar.visible :
			self.pipe.write(' ' * 80)
			self.pipe.write('\r')
			self.progressbar.visible = 0
		self.pipe.write(data)


class Encoder (object) :
	'''Encode data going through the pipe to utf8'''

	def __init__ (self, pipe) :
		self.pipe = pipe

	def write (self, data) :
		self.pipe.write(data.encode('utf8'))

	def close (self) :
		self.pipe.close()


class Logfile (object) :

	def __init__ (self) :
		self.logfile = StringIO.StringIO()

	def write (self, data) :
		self.logfile.write(data)

	def open (self, filename) :
		logfile = Encoder(file(filename, 'a'))
		logfile.write(self.logfile.getvalue())
		self.logfile = logfile

	def close (self) :
		self.logfile.close()
		self.logfile = StringIO.StringIO()


class ProgressBar (object) :

	def __init__ (self, pipe) :
		self.pipe = pipe
		self.visible = 0

	def start (self, max_value) :
		self.max_value = max_value
		self.start_time = time.time()
		self.update(0)

	def update (self, value) :
		progress = float(value) / float(self.max_value)
		self.elapsed_time = time.time() - self.start_time
		self.pipe.write('|')
		self.pipe.write(('#' * int(round(progress * 64))).ljust(64))
		self.pipe.write('| ')
		self.pipe.write(('%i%% ' % int(round(progress * 100))).rjust(5))
		if progress == 0 :
			self.pipe.write('--:--:--')
		elif progress == 1 :
			self.pipe.write(time.strftime('%H:%M:%S', time.gmtime(self.elapsed_time)))
			self.pipe.write('\n')
		else :
			remaining_time = self.elapsed_time * (1 / progress - 1)
			self.pipe.write(time.strftime('%H:%M:%S', time.gmtime(remaining_time)))
		self.pipe.write('\r')
		self.pipe.flush()
		self.visible = 1


progressbar = ProgressBar(sys.stdout)
logfile = Logfile()

sys.stdout = Encoder(sys.stdout)
sys.stderr = Encoder(sys.stderr)
sys.stdout = Wiper(sys.stdout, progressbar)
sys.stderr = Wiper(sys.stderr, progressbar)
sys.stdout = Copier(sys.stdout, logfile)
sys.stderr = Copier(sys.stderr, logfile)

