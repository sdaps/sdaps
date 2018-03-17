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

'''Some path values, used to find and load program components.
'''

import os


import gettext
import locale


local_run = False

# required if local_run == True
build_dir = str()

# required if local_run == True
lib_build_dir = str()

# required if local_run == True
source_dir = str()

# required if local_run == False
prefix = str()


def init(local_run_value, package_path):
    '''Initialize path values for sdaps
    '''
    global local_run, build_dir, lib_build_dir, source_dir, prefix

    # Initialize local_run
    local_run = local_run_value

    base_dir = os.path.split(os.path.abspath(package_path))[0]

    if local_run:
        source_dir = base_dir

        from pkg_resources import get_build_platform
        from distutils.sysconfig import get_python_version

        # Initialize gettext
        init_gettext(os.path.join(
            base_dir,
            'build',
            'mo'))

        # Initialize build_dir
        build_dir = os.path.join(base_dir, 'build', 'share', 'sdaps')

        # Initialize build_dir
        lib_build_dir = os.path.join(
            base_dir,
            'build', 'lib.%s-%s' % (get_build_platform(), get_python_version()),
            'sdaps')
    else:
        # Look for the data in the parent directories
        path = base_dir
        while True:
            if os.path.exists(os.path.join(path, 'share', 'sdaps')):
                prefix = path
                break
            new_path = os.path.split(path)[0]
            assert not path == new_path, "could not find locales" # Wir wären oben angekommen
            path = new_path

        # Initialize gettext
        init_gettext(os.path.join(prefix, 'share', 'locale'))


def init_gettext(locale_dir):
    '''Initialize gettext using the given directory containing the l10n data.
    '''
    gettext.bindtextdomain('sdaps', locale_dir)

    if hasattr(gettext, 'bind_textdomain_codeset'):
        gettext.bind_textdomain_codeset('sdaps', 'UTF-8')
        gettext.textdomain('sdaps')
    if hasattr(locale, 'bind_textdomain_codeset'):
        locale.bindtextdomain('sdaps', locale_dir)
        locale.bind_textdomain_codeset('sdaps', 'UTF-8')
        locale.textdomain('sdaps')

