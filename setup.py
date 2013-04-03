#!/usr/bin/env python
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

from distutils.core import setup
from distutils.extension import Extension
import glob
import os
import os.path
import commands
import sys
from DistUtilsExtra.command import *
import ConfigParser

def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries', '-D' : 'define_macros'}
    (status, tokens) = commands.getstatusoutput("pkg-config --libs --cflags %s" % ' '.join(packages))
    if status != 0:
        print tokens
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

class sdaps_build_i18n(build_i18n.build_i18n):

    # Hardcoded ...
    dict_sourcefile = 'tex/tex_translations.in'
    dict_dir = 'share/sdaps/tex'
    dict_filename = 'tex_translations'

    def run(self):
        # run the original code
        build_i18n.build_i18n.run(self)

        dest_dir = os.path.join('build', self.dict_dir)
        tex_translations = os.path.join(dest_dir, self.dict_filename)

        # Build the tex_translations file
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

        parser = ConfigParser.ConfigParser()
        parser.read(tex_translations)

        langs = {}
        keys = set()
        for k, v in parser.items("translations"):
            key, lang = extract_key_lang(k)
            if not key == 'tex-language':
                keys.add(key)
                continue

            assert lang not in langs
            assert v not in langs.items()

            langs[lang] = v

        dictfiles = []
        for lang, name in langs.iteritems():
            print 'building LaTeX dictionary file for language %s (%s)' % (name, lang if lang else 'C')
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

            for key in keys:
                if lang is not None:
                    k = "%s[%s]" % (key, lang)
                else:
                    k = key

                try:
                    value = parser.get("translations", k)
                except ConfigParser.NoOptionError:
                    value = parser.get("translations", key)

                f.write('\\providetranslation{%s}{%s}\n' % (key, value))

        # And install the dictionary files
        self.distribution.data_files.append((self.dict_dir, dictfiles))

class sdaps_clean_i18n(clean_i18n.clean_i18n):
    dict_dir = 'share/sdaps/tex'
    dict_filename = "tex_translations"

    def run(self):
        # Remove dictionaries

        directory = os.path.join('build', self.dict_dir)
        if os.path.isdir(directory):
            print "removing all LaTeX dictionaries in '%s'" % directory
            for filename in os.listdir(directory):
                if filename.startswith('translator-sdaps-dictionary-'):
                    os.unlink(os.path.join(directory, filename))

        fn = os.path.join('build', self.dict_dir, self.dict_filename)
        if os.path.exists(fn):
            os.unlink(fn)

        clean_i18n.clean_i18n.run(self)

setup(name='sdaps',
      version='1.0.3',
      description='Scripts for data acquisition with paper-based surveys',
      url='http://sdaps.sipsolutions.net',
      author='Benjamin Berg, Christoph Simon',
      author_email='benjamin@sipsolutions.net, post@christoph-simon.eu',
      license='GPL-3',
      long_description="""
SDAPS is a tool to carry out paper based surveys. You can create machine
readable questionnaires using LibreOffice and LaTeX. It also provides
the tools to later analyse the scanned data, and create a report.
""",
      packages=['sdaps',
                'sdaps.add',
                'sdaps.annotate',
                'sdaps.boxgallery',
                'sdaps.cover',
                'sdaps.csvdata',
                'sdaps.gui',
                'sdaps.ids',
                'sdaps.image',
                'sdaps.info',
                'sdaps.model',
                'sdaps.recognize',
                'sdaps.reorder',
                'sdaps.stamp',
                'sdaps.report',
                'sdaps.reporttex',
                'sdaps.setup.pdftools',
                'sdaps.setup',
                'sdaps.setuptex'
      ],
      package_dir={'sdaps.gui': 'sdaps/gui'},
      scripts=[
               'bin/sdaps',
               ],
      ext_modules=[Extension('sdaps.image.image',
                   ['sdaps/image/wrap_image.c', 'sdaps/image/image.c', 'sdaps/image/transform.c', 'sdaps/image/surface.c'],
                   **pkgconfig('pycairo', 'cairo' ,'glib-2.0', libraries=['tiff']))],
      data_files=[
                  ('share/sdaps/ui',
                   glob.glob("sdaps/gui/*.ui")
                  ),
                  ('share/sdaps/tex', glob.glob('tex/*.cls')
                  ),
                  ('share/sdaps/tex', glob.glob('tex/*.tex')
                  ),
                  ],
      cmdclass = { "build" : build_extra.build_extra,
                   "build_i18n" :  sdaps_build_i18n,
                   "build_help" :  build_help.build_help,
                   "build_icons" :  build_icons.build_icons,
                   "clean" : sdaps_clean_i18n }
     )

