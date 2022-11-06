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

from setuptools import setup, Distribution, Extension, Command

# Command imports (try setuptools and fall back to distutils)
from setuptools.command.sdist import sdist
from setuptools.command.install import install
try:
    from setuptools.command.build import build
except:
    from distutils.command.build import build

try:
    from setuptools.command.clean import clean
except:
    from distutils.command.clean import clean

# Needed stuff
from pkgconfig import pkgconfig
import glob
import os
import os.path
import subprocess
import sys
import configparser

# We import sdaps to grab the version number; a bit of a hack but
# it should work just fine as few modules are actually loaded by doing
# this
from sdaps import __version__


class sdaps_build_tex(Command):

    description = "build and install the LaTeX packages and classes"

    # Hardcoded ...
    tex_installdir = 'share/sdaps/tex'
    tex_resultdir = 'tex/class/build/local'

    dict_sourcefile = 'tex/tex_translations.in'
    dict_dir = 'share/sdaps/tex'
    dict_filename = 'tex_translations'

    user_options = []

    def update_data_files(self):
        data_files = getattr(self.distribution, 'data_files', [])

        files = [os.path.join(self.tex_resultdir, f) for f in os.listdir(self.tex_resultdir)]
        data_files.append((self.tex_installdir, files))

        dict_dir = os.path.join('build', self.dict_dir)

        # And install the dictionary files
        data_files.append((self.dict_dir, glob.glob(os.path.join(dict_dir, '*.dict'))))


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

        self.update_data_files()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

class sdaps_clean_tex(Command):
    dict_dir = 'share/sdaps/tex'
    dict_filename = "tex_translations"

    user_options = []

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

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

class sdaps_clean(clean):
    clean.sub_commands += \
        [
            ('clean_tex', lambda x : True ),
            #('clean_i18n', lambda x : True ),
        ]

class sdaps_build(build):
    sub_commands = \
        build.sub_commands + \
        [
            ('build_i18n', lambda self : True),
            ('build_tex', lambda self : self.build_tex),
        ]

    user_options = build.user_options + [
        # The format is (long option, short option, description).
        ('build-tex', None, 'Also build LaTeX class and translations'),
    ]

    boolean_options = install.boolean_options + ['build-tex']

    def initialize_options(self):
        self.build_tex = None

        build.initialize_options(self)

    def finalize_options(self):
        if self.build_tex is None:
            self.build_tex = False

        build.finalize_options(self)

class sdaps_install_tex(sdaps_build_tex):
    description = "install LaTeX data files"

    user_options = []

    def run(self):
        self.update_data_files()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class sdaps_install(install):
    sub_commands = \
        [
            ('install_i18n', lambda self : True),
            ('install_tex', lambda self : self.install_tex),
        ] + install.sub_commands

    # Isn't there a better way to have the build time option also
    # in the install section?
    user_options = install.user_options + [
        # The format is (long option, short option, description).
        ('install-tex', None, 'Install LaTeX file (use with TeX Live < 2022)'),
    ]
    boolean_options = install.boolean_options + ['install-tex']

    def run(self):
        # Hmm, without this install_tex is not run?
        super().run()

    def initialize_options(self):
        self.install_tex = None

        install.initialize_options(self)

    def finalize_options(self):
        if self.install_tex is None:
            self.install_tex = False

        install.finalize_options(self)

class sdaps_build_i18n(Command):
    """Simple gettext wrapper (only needed when building from source)"""
    user_options = []

    def doit(self, msgfmt=True):
        data_files = getattr(self.distribution, 'data_files', [])

        for po_file in glob.glob("po/*.po"):
            lang = os.path.basename(po_file[:-3])
            mo_dir = os.path.join("build", "mo", lang, "LC_MESSAGES")
            os.makedirs(mo_dir, exist_ok=True)
            mo_file = os.path.join(mo_dir, "sdaps.mo")

            if msgfmt:
                self.spawn(["msgfmt", po_file, "-o", mo_file])

            targetpath = os.path.join("share/locale", lang, "LC_MESSAGES")
            data_files.append((targetpath, (mo_file,)))

    def run(self):
        "Compile .po to .mo"
        self.doit(True)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

class sdaps_install_i18n(sdaps_build_i18n):
    """Simple gettext wrapper (only needed when building from source)"""
    user_options = []

    def run(self):
        "Compile .po to .mo"
        self.doit(False)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

cmdclass = {
    'build' : sdaps_build,
    'build_i18n' : sdaps_build_i18n,
    'build_tex' : sdaps_build_tex,
    'clean_tex' : sdaps_clean_tex,
    'install' : sdaps_install,
    'install_i18n' : sdaps_install_i18n,
    'install_tex' : sdaps_install_tex,
}


image_ext = Extension('sdaps.image.image',
                      ['sdaps/image/wrap_image.c',
                       'sdaps/image/image.c',
                       'sdaps/image/transform.c',
                       'sdaps/image/surface.c'])

pkgconfig.configure_extension(image_ext, 'py3cairo cairo glib-2.0 libtiff-4')

setup(version=__version__,
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
      scripts=['bin/sdaps',],
      ext_modules=[image_ext],
      # NOTE: This is on purpose! sdapsreport.cls is not included
      #       in the LaTeX package uploaded to CTAN.
      data_files=[
          ('share/sdaps/tex', glob.glob('tex/*.cls')),
          ('share/sdaps/ui', glob.glob("sdaps/gui/*.ui")),
      ],
      cmdclass = cmdclass,
     )
