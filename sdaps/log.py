# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
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

'''
This module alters sys.stdout and sys.stderr to copy all output into a logfile.

Note that some magic is done when the output stream is not a tty. In that
case the progress bar and messages done using the :py:meth:`interactive`
function will be suppressed. The reason to do this is to allow commands to
output data to `sys.stdout`.
'''

import sys
import time
import io

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext


def warn(msg):
    sys.stderr.write(_('Warning: ') + msg + '\n')


def error(msg):
    sys.stderr.write(_('Error: ') + msg + '\n')

def interactive(msg):
    """Only forward the message to stdout if it is a terminal."""
    if hasattr(sys.stdout, "interactive"):
        sys.stdout.interactive(msg)
    else:
        if sys.stdout.isatty():
            sys.stdout.write(msg)

class Copier(object):
    '''copy all data going through the pipe into a logfile'''

    def __init__(self, pipe, logfile):
        self.pipe = pipe
        self.logfile = logfile

    def write(self, data):
        self.pipe.write(data)
        self.logfile.write(data)

    def interactive(self, data):
        if self.pipe.isatty():
            self.pipe.write(data)
        self.logfile.write(data)

    def isatty(self):
        return self.pipe.isatty()

    def flush(self):
        self.pipe.flush()
        self.logfile.flush()

    def fileno(self):
        return self.pipe.fileno()

class Wiper(object):
    '''wipe out the progressbar before forwarding data through the pipe'''

    def __init__(self, pipe, progressbar):
        self.pipe = pipe
        self.progressbar = progressbar

    def write(self, data):
        if self.progressbar.visible:
            self.pipe.write(' ' * 80)
            self.pipe.write('\r')
            self.progressbar.visible = 0
        self.pipe.write(data)

    def isatty(self):
        return self.pipe.isatty()

    def flush(self):
        self.pipe.flush()

    def fileno(self):
        return self.pipe.fileno()

class Encoder(object):
    '''Encode data going through the pipe to utf-8'''

    def __init__(self, pipe):
        self.pipe = pipe

    def write(self, data):
        if isinstance(data, bytes):
            self.pipe.write(data.encode('utf-8'))
        else:
            self.pipe.write(data)

    def close(self):
        self.pipe.close()

    def isatty(self):
        return self.pipe.isatty()

    def flush(self):
        self.pipe.flush()

    def fileno(self):
        return self.pipe.fileno()

class Logfile(object):

    def __init__(self):
        self.logfile = io.StringIO()

    def write(self, data):
        self.logfile.write(data)
        self.logfile.flush()

    def open(self, filename):
        logfile = Encoder(open(filename, 'a'))
        logfile.write(self.logfile.getvalue())
        self.logfile = logfile

    def close(self):
        self.logfile.close()
        self.logfile = io.StringIO()

    def isatty(self):
        return False

    def flush(self):
        self.logfile.flush()

    def fileno(self):
        return self.logfile.fileno()

class ProgressBar(object):

    def __init__(self, pipe):
        self.pipe = pipe
        self.visible = 0

    def start(self, max_value):
        self.max_value = max_value
        self.start_time = time.time()
        self.update(0)

    def update(self, value):
        self.elapsed_time = time.time() - self.start_time

        # Don't display anything if the output is a pipe
        if not self.pipe.isatty():
            return

        progress = float(value) / float(self.max_value)
        self.pipe.write('|')
        self.pipe.write(('#' * int(round(progress * 64))).ljust(64))
        self.pipe.write('| ')
        self.pipe.write(('%i%% ' % int(round(progress * 100))).rjust(5))
        if progress == 0:
            self.pipe.write('--:--:--')
        elif progress == 1:
            self.pipe.write(time.strftime('%H:%M:%S', time.gmtime(self.elapsed_time)))
            self.pipe.write('\n')
        else:
            remaining_time = self.elapsed_time * (1 / progress - 1)
            self.pipe.write(time.strftime('%H:%M:%S', time.gmtime(remaining_time)))
        self.pipe.write('\r')
        self.pipe.flush()
        self.visible = 1

    def isatty(self):
        return self.pipe.isatty()

    def flush(self):
        self.pipe.flush()

progressbar = ProgressBar(sys.stdout)
logfile = Logfile()

redirects_activated = False
def activate_redirects():
    global redirects_activated

    if redirects_activated is not False:
        return
    redirects_activated = True

    sys.stdout = Encoder(sys.stdout)
    sys.stderr = Encoder(sys.stderr)
    sys.stdout = Wiper(sys.stdout, progressbar)
    sys.stderr = Wiper(sys.stderr, progressbar)
    sys.stdout = Copier(sys.stdout, logfile)
    sys.stderr = Copier(sys.stderr, logfile)

