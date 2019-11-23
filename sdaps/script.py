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
This module defines some decorators, helping to implement sdaps-scripts.
To register a function as a sdaps-script(callable from the command line), use
@register
'''

import sys
import os
import functools
import argparse

from . import __version__
from . import log
from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

# Create parser

if "sphinx" in sys.argv[0]:
    prog = "sdaps"
else:
    prog = None

description = _("SDAPS -- Paper based survey tool.")
epilog = None
parser = argparse.ArgumentParser(description=description, epilog=epilog, prog=prog)

parser.add_argument('--version',
    help=_('Display version and exit'),
    action='version',
    version="%%(prog)s %s" % __version__)

# Set required as an attribute rather than kwarg so that it works with python <3.7
subparsers = parser.add_subparsers(help=_("command list|Commands:"), dest='command')
subparsers.required = True

def add_subparser(*args, **kwargs):
    parser = subparsers.add_parser(*args, **kwargs)

    return parser

def add_project_argument(parser):
    parser.add_argument('project', type=str, help=_("project directory|The SDAPS project."))

def add_project_subparser(*args, **kwargs):
    parser = add_subparser(*args, **kwargs)

    add_project_argument(parser)

    return parser

def doc(docstring):
    '''decorator to add a docstring to a function.

    When using normal Python docstring syntax it cannot be generated
    dynamically. Using this one can for example add translations.

    >>> @doc(_(u'docstring'))
    >>> def function(*args, **kwargs):
    >>>    pass
    '''

    def decorator(function):
        function.__doc__ = docstring
        return function
    return decorator

def connect(parser, name=None):
    '''decorator to connect an already prepared parser to call into a function.

    This function initilizes the _func and _name properties for the parser to
    the given function, and its name. It also sets the functions docstring to
    be the parsers help. This way the help string appears in the sphinx
    documentation for the function.

    >>> @script.connect(parser)
    >>> def add(cmdline):
    >>>     pass
    '''

    def decorator(function):
        # Use the function name as a fallback, it should be the same usually.
        if name is None:
            local_name = function.__name__
        else:
            local_name = name

        parser.set_defaults(_func=function, _name=local_name)

        function.__doc__ = parser.format_help()

        return function

    return decorator

def logfile(function):
    '''open the logfile when running the function and close it afterwards.

    >>> @logfile
    >>> def function(survey_dir, *args, **kwargs):
    >>>     pass

    @logfile will open survey_dir/log as a logfile when function is called and
    close it, when function finishes.
    '''
    def decorated_function(cmdline):
        log.logfile.open(os.path.join(cmdline['project'], 'log'))
        result = function(cmdline)
        log.logfile.close()
        return result

    functools.update_wrapper(decorated_function, function)

    return decorated_function


