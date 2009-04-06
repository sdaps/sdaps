#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension
import glob
import os
import commands
from DistUtilsExtra.command import *

def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries', '-D' : 'define_macros'}
    for token in commands.getoutput("pkg-config --libs --cflags %s" % ' '.join(packages)).split():
        type = flag_map.get(token[:2])
        value = token[2:]
        if type == 'define_macros':
            value = tuple(value.split('=', 1))
        kw.setdefault(type, []).append(value)
    return kw

setup(name='sdaps',
      version='0.1',
      packages=['sdaps',
                'sdaps.boxgallery',
                'sdaps.csvdata',
                'sdaps.image',
                'sdaps.model',
                'sdaps.recognize',
                'sdaps.stamp',
                'sdaps.report',
                'sdaps.setup.pdftools',
                'sdaps.setup',
                'sdaps.gui'
      ],
      scripts=[
               'sdaps/sdaps',
               ],
      ext_modules=[Extension('sdaps.image.image',
                   ['sdaps/image/wrap_image.c', 'sdaps/image/image.c'],
                   **pkgconfig('pycairo', 'cairo' ,'glib-2.0', libraries=['tiff']))],
      data_files=[
#                  ('share/software-properties/designer',
#                   glob.glob("data/designer/*.ui")
#                  ),
                  ('share/sdaps/glade',
                   glob.glob("sdaps/gui/*.glade")
                  ),
                  ],
      cmdclass = { "build" : build_extra.build_extra,
                   "build_i18n" :  build_i18n.build_i18n,
                   "build_help" :  build_help.build_help,
                   "build_icons" :  build_icons.build_icons }
     )
