project('sdaps', 'c', version: '1.9.13')

py_mod = import('python')
py = py_mod.find_installation()

pycairo = dependency('py3cairo')
cairo = dependency('cairo')
glib = dependency('glib-2.0')
tiff = dependency('libtiff-4')

i18n = import('i18n')

subdir('po')
subdir('tex')

# The below handles the main python code and C extension

sdaps_ext = py.extension_module(
    'image',
    ['sdaps/image/wrap_image.c',
     'sdaps/image/image.c',
     'sdaps/image/image.h',
     'sdaps/image/transform.c',
     'sdaps/image/transform.h',
     'sdaps/image/surface.c',
     'sdaps/image/surface.h'],
    install: true,
    subdir: 'sdaps/image',
    # py.dependency() is only needed for meson < 0.63.0
    dependencies: [pycairo, cairo, glib, tiff, py.dependency()],
)

subdir('test')

install_data(
    'bin/sdaps',
    install_dir: get_option('bindir'),
    install_tag: 'bin'
)

install_data(
    'sdaps/gui/main_window.ui',
    install_dir: get_option('datadir') / meson.project_name() / 'ui',
    install_tag: 'gui'
)

modules = {
    'sdaps': [
        'calculate.py',
        'clifilter.py',
        'defs.py',
        'log.py',
        'matrix.py',
        'script.py',
        'surface.py',
        'template.py',
        'paths.py',
    ],
    'sdaps/add': [],
    'sdaps/annotate': [ 'buddies.py' ],
    'sdaps/boxgallery': [ 'buddies.py' ],
    'sdaps/cmdline/': [
        'add.py',
        'annotate.py',
        'boxgallery.py',
        'convert.py',
        'cover.py',
        'csvdata.py',
        'feather.py',
        'gui.py',
        'ids.py',
        'info.py',
        'recognize.py',
        'reorder.py',
        'report.py',
        'reporttex.py',
        'reset.py',
        'setup.py',
        'stamp.py',
    ],
    'sdaps/convert': [],
    'sdaps/cover': [],
    'sdaps/csvdata': [ 'buddies.py' ],
    'sdaps/gui': [
        'buddies.py',
        'sheet_widget.py',
        'widget_buddies.py',
    ],
    'sdaps/image': [],
    'sdaps/model': [
        'buddy.py',
        'data.py',
        'db.py',
        'questionnaire.py',
        'sheet.py',
        'survey.py',
    ],
    'sdaps/pandas': [ 'buddies.py' ],
    'sdaps/recognize': [
        'blank.py',
        'buddies.py',
        'classic.py',
        'code128.py',
        'qrcode.py',
    ],
    'sdaps/reorder': [],
    'sdaps/report': [
        'answers.py',
        'buddies.py',
        'flowables.py',
    ],
    'sdaps/reporttex': [
        'buddies.py',
    ],
    'sdaps/reset': [],
    'sdaps/setup': [
        'additionalparser.py',
        'buddies.py',
    ],
    'sdaps/setuptex': [
        'sdapsfileparser.py',
    ],
    'sdaps/stamp': [
        'latex.py',
    ],
    'sdaps/utils': [
        'barcode.py',
        'create-latexmap.py',
        'exceptions.py',
        'image.py',
        'mimetype.py',
        'opencv.py',
        'paper.py',
        'ugettext.py',
        'latex.py',
        'latexmap.py',
    ],
}

foreach module, files: modules
    sources = [ module / '__init__.py' ]
    foreach file: files
        sources += module / file
    endforeach
    py.install_sources(sources, subdir: module, pure: false)
endforeach
