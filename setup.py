#!/usr/bin/env python3
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright (C) 2008-2013, Benjamin Berg <benjamin@sipsolutions.net>
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

from distutils.core import setup, Command, Distribution
from distutils.extension import Extension
import glob
import os
import os.path
import subprocess
import sys
from distutils.command import build, install, install_data, clean
from DistUtilsExtra.command import *
import configparser

# We import sdaps to grab the version number; a bit of a hack but
# it should work just fine as few modules are actually loaded by doing
# this
from sdaps import __version__

def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries', '-D' : 'define_macros'}
    (status, tokens) = subprocess.getstatusoutput("pkg-config --libs --cflags %s" % ' '.join(packages))
    if status != 0:
        print(tokens)
        sys.exit(1)

    for token in tokens.split():
        type = flag_map.get(token[:2])
        value = token[2:]
        if type == 'define_macros':
            value = tuple(value.split('=', 1))
        if type is None:
           value = token
           type = 'extra_compile_args'
        kw.setdefault(type, []).append(value)
    return kw

class sdaps_build_tex(build.build):

    description = "build and install the LaTeX packages and classes"

    # Hardcoded ...
    tex_installdir = 'share/sdaps/tex'
    tex_resultdir = 'tex/class/build/local'

    dict_sourcefile = 'tex/tex_translations.in'
    dict_dir = 'share/sdaps/tex'
    dict_filename = 'tex_translations'

    def run(self):
        # Build the LaTeX packages and classes, note that they cannot build
        # out of tree currently.
        maindir = os.path.abspath(os.curdir)
        if not os.path.exists('tex/class/build.lua'):
            print('error: LaTeX build script is not available')
            print('Did you forget to checkout the git submodule? See README for more information.')
            os._exit(1)
        os.chdir('tex/class')
        self.spawn(['./build.lua', 'unpack'])
        os.chdir(maindir)

        files = [os.path.join(self.tex_resultdir, f) for f in os.listdir(self.tex_resultdir)]
        self.distribution.tex_files.append((self.tex_installdir, files))


        # And now the LaTeX translations
        dest_dir = os.path.join('build', self.dict_dir)
        tex_translations = os.path.join(dest_dir, self.dict_filename)

        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        cmd = ['intltool-merge', '-d', 'tex/po', self.dict_sourcefile, tex_translations]
        self.spawn(cmd)

        ###################
        # Now build the LaTeX dictionaries
        def extract_key_lang(key):
            if not key.endswith(']'):
                return key, None
            index = key.rfind('[')
            return key[:index], key[index+1:-1]

        parser = configparser.ConfigParser()
        parser.read(tex_translations)

        langs = {}
        keys = set()
        for k, v in parser.items("translations"):
            key, lang = extract_key_lang(k)
            if not key == 'tex-language':
                keys.add(key)
                continue

            assert lang not in langs
            assert v not in list(langs.items())

            langs[lang] = v

        # Load mapping from unicode to LaTeX command name
        from sdaps.utils.latex import unicode_to_latex

        dictfiles = []
        for lang, name in langs.items():
            print('building LaTeX dictionary file for language %s (%s)' % (name, lang if lang else 'C'))
            dictfiles.append(os.path.join(dest_dir, 'translator-sdaps-dictionary-%s.dict' % name))
            f = open(dictfiles[-1], 'w')

            f.write('% This file is auto-generated from gettext translations (.po files).\n')
            f.write('% The header of the original file follows for reference:\n')
            f.write('%\n')
            for line in open(self.dict_sourcefile).readlines():
                if not line.startswith('#'):
                    break
                f.write('%' + line[1:])
            f.write('%\n\n')
            f.write('\\ProvidesDictionary{translator-sdaps-dictionary}{%s}\n\n' % name)

            for key in sorted(keys):
                if lang is not None:
                    k = "%s[%s]" % (key, lang)
                else:
                    k = key

                try:
                    value = parser.get("translations", k)
                except configparser.NoOptionError:
                    value = parser.get("translations", key)

                value = unicode_to_latex(value)

                f.write('\\providetranslation{%s}{%s}\n' % (key, value))

        # And install the dictionary files
        self.distribution.tex_files.append((self.dict_dir, dictfiles))

class sdaps_clean_tex(clean.clean):
    dict_dir = 'share/sdaps/tex'
    dict_filename = "tex_translations"

    def run(self):
        # Remove dictionaries

        directory = os.path.join('build', self.dict_dir)
        if os.path.isdir(directory):
            print("removing all LaTeX dictionaries in '%s'" % directory)
            for filename in os.listdir(directory):
                if filename.startswith('translator-sdaps-dictionary-'):
                    os.unlink(os.path.join(directory, filename))

        fn = os.path.join('build', self.dict_dir, self.dict_filename)
        if os.path.exists(fn):
            os.unlink(fn)

class sdaps_clean(clean.clean):
    sub_commands = \
        [
            ('clean_tex', lambda x : True ),
            ('clean_i18n', lambda x : True ),
        ]

    def run(self):
        for cmd in self.get_sub_commands():
            self.run_command(cmd)

class sdaps_build(build_extra.build_extra):
    sub_commands = \
        build_extra.build_extra.sub_commands + \
        [
            ('build_tex', lambda self : self.build_tex),
        ]

    user_options = build_extra.build_extra.user_options + [
        # The format is (long option, short option, description).
        ('build-tex', None, 'Also build LaTeX class and translations'),
    ]

    def initialize_options(self):
        self.build_tex = None

        build_extra.build_extra.initialize_options(self)

    def finalize_options(self):
        if self.build_tex is None:
            self.build_tex = False

        build_extra.build_extra.finalize_options(self)

class sdaps_install_tex(install_data.install_data):
    # We just use install_data, but set data_files from distribution.tex_files
    # instead.

    description = "install LaTeX data files"

    user_options = install_data.install_data.user_options + [
        ('skip-build', None, "skip the build steps"),
    ]

    boolean_options = install_data.install_data.boolean_options + ['skip-build']

    def initialize_options(self):
        self.skip_build = None

        install_data.install_data.initialize_options(self)

        self.data_files = self.distribution.tex_files

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('skip_build', 'skip_build'),
                                  )

        install_data.install_data.finalize_options(self)

    def run(self):
        if not self.skip_build:
            self.run_command('build_tex')

        install_data.install_data.run(self)


class sdaps_install(install.install):
    sub_commands = \
        install.install.sub_commands + \
        [
            ('install_tex', lambda self : self.install_tex),
        ]

    # Isn't there a better way to have the build time option also
    # in the install section?
    user_options = install.install.user_options + [
        # The format is (long option, short option, description).
        ('install-tex', None, 'Disable LaTeX build, should be done if the class is already available e.g. from TeX Live'),
    ]

    def initialize_options(self):
        self.install_tex = None

        install.install.initialize_options(self)

    def finalize_options(self):
        if self.install_tex is None:
            self.install_tex = False

        install.install.finalize_options(self)

class SDAPSDistribution(Distribution):
    # All we need is to add tex_files

    def __init__(self, attrs=None):
        self.tex_files = None

        super().__init__(attrs=attrs)

    def has_tex_files(self):
        return self.tex_files and len(self.tex_files) > 0

setup(name='sdaps',
      version=__version__,
      description='Scripts for data acquisition with paper-based surveys',
      url='http://sdaps.sipsolutions.net',
      author='Benjamin Berg, Christoph Simon',
      author_email='benjamin@sipsolutions.net, post@christoph-simon.eu',
      license='GPL-3',
      long_description="""
SDAPS is a tool to carry out paper based surveys. You can create machine
readable questionnaires using LaTeX. It also provides the tools to later
analyse the scanned data, and create a report.
""",
      distclass=SDAPSDistribution,
      packages=['sdaps',
                'sdaps.add',
                'sdaps.annotate',
                'sdaps.boxgallery',
                'sdaps.cmdline',
                'sdaps.cover',
                'sdaps.convert',
                'sdaps.csvdata',
                'sdaps.gui',
                'sdaps.image',
                'sdaps.model',
                'sdaps.recognize',
                'sdaps.reorder',
                'sdaps.stamp',
                'sdaps.report',
                'sdaps.reporttex',
                'sdaps.reset',
                'sdaps.setup',
                'sdaps.setuptex',
                'sdaps.utils'
      ],
      package_dir={'sdaps.gui': 'sdaps/gui'},
      scripts=[
               'bin/sdaps',
               ],
      ext_modules=[Extension('sdaps.image.image',
                   ['sdaps/image/wrap_image.c', 'sdaps/image/image.c', 'sdaps/image/transform.c', 'sdaps/image/surface.c'],
                   **pkgconfig('py3cairo', 'cairo', 'glib-2.0', libraries=['tiff']))],
      data_files=[
                  ('share/sdaps/ui',
                   glob.glob("sdaps/gui/*.ui")
                  ),
                  # NOTE: This is on purpose! sdapsreport.cls is not included
                  #       in the LaTeX package uploaded to CTAN.
                  ('share/sdaps/tex', glob.glob('tex/*.cls')
                  ),
                  ],
      tex_files=[],
      cmdclass = { "install": sdaps_install,
                   "install_tex" : sdaps_install_tex,
                   "build" : sdaps_build,
                   "build_tex" : sdaps_build_tex,
                   "build_i18n" :  build_i18n.build_i18n,
                   "build_help" :  build_help.build_help,
                   "build_icons" :  build_icons.build_icons,
                   "clean" : sdaps_clean,
                   "clean_i18n" : clean_i18n.clean_i18n,
                   "clean_tex" : sdaps_clean_tex,
                  }
     )
