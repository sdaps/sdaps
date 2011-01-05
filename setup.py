#!/usr/bin/python

from distutils.core import setup
from distutils.extension import Extension
import glob
import os
import commands
import sys
from DistUtilsExtra.command import *

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

setup(name='sdaps',
      version='0.1',
      description='Scripts for data acquisition with paper based surveys',
      url='http://sdaps.sipsolutions.net',
      author='Benjamin Berg, Christoph Simon',
      author_email='benjamin@sipsolutions.net, christoph.simon@gmx.eu',
      license='GPL-3',
      long_description="""
SDAPS is a tool to carry out paper based surveys. You can create machine
readable questionnaires using OpenOffice.org. It also provides the tools to later
analyse the scanned data, and create a report.
""",
      packages=['sdaps',
                'sdaps.boxgallery',
                'sdaps.csvdata',
                'sdaps.gui',
                'sdaps.image',
                'sdaps.model',
                'sdaps.recognize',
                'sdaps.stamp',
                'sdaps.report',
                'sdaps.setup.pdftools',
                'sdaps.setup'
      ],
      package_dir={'sdaps.gui': 'sdaps/gui'},
      scripts=[
               'bin/sdaps',
               ],
      ext_modules=[Extension('sdaps.image.image',
                   ['sdaps/image/wrap_image.c', 'sdaps/image/image.c'],
                   **pkgconfig('pycairo', 'cairo' ,'glib-2.0', libraries=['tiff']))],
      data_files=[
                  ('share/sdaps/glade',
                   glob.glob("sdaps/gui/*.glade")
                  ),
                  ],
      cmdclass = { "build" : build_extra.build_extra,
                   "build_i18n" :  build_i18n.build_i18n,
                   "build_help" :  build_help.build_help,
                   "build_icons" :  build_icons.build_icons }
     )
