# SDAPS

This Program can be used to carry out paper based surveys.

SDAPS uses a specialised LaTeX class to define questionnaires. This is tightly
integrated and is an easy way to create machine readable questionnaires.

After this, the program can create an arbitrary number of (unique)
questionnaires that can be printed and handed out. After being filled out, you
just scan them in, let sdaps run over them, and let it create a report with
the results.

The main LaTeX class is also available on CTAN (https://ctan.org/pkg/sdaps) and
may also be installed directly, e.g. using a LaTeX distribution like TeX Live.
Please check whether you can install it that way, and if not choose the
`--build-tex` or `--install-tex` for building/installing SDAPS.

## Requirements

Depending on what part of SDAPS you use, different dependencies are
required.

general (including recognize):
 * Python 3.6
 * distutils and distutils-extra
 * python3-cairo (including development files)
 * libtiff (including development files)
 * pkg-config
 * zbarimg binary for "code128" and "qr" styles
 * python3 development files

graphical user interface (gui):
 * GTK+ and introspection data
 * python3-gi

reportlab based reports (report):
 * reportlab
 * Python Imaging Library (PIL)

LaTeX based questionnaires (setup_tex/stamp):
 * pdflatex and packages:
   * PGF/TikZ
   * translator (part of beamer)
   * and more

LaTeX based reports:
 * pdflatex and packages:
   * PGF/TikZ
   * translator (part of beamer)
 * siunitx

Import of other image formats (convert, add --convert):
 * python3-opencv
 * Poppler and introspection data
 * python3-gi

Export to feather format:
 * python3-pandas
 * pyarrows

Debug output (annotate):
 * Poppler and introspection data
 * python3-gi

## Installation

You can install sdaps using `./setup.py install` or
`./setup.py install --install-tex`. The C extension will be compiled
automatically, but of course you have to have all the dependencies installed
for this to work. When `--install-tex` is passed, the LaTeX class files
will also be installed. This is only necessary if your LaTeX distribution
does not yet include the sdaps package.

Please note that this git repository uses submodules to pull in the LaTeX
code. This means you need to run
 $ git submodule init
and then run
 $ git submodule update
to checkout and update the repository after a pull.

Alternatively, do the initial clone using "git clone --recursive".

## Standalone execution

As an alternative to installing sdaps it is also supported to run it without
installation. To do this run `./setup.py build` or
`./setup.py build --build-tex` to build the binary modules, translation and
possibly LaTeX class files. After this execute sdaps using the provided
`sdaps.py` script in the toplevel directory.

Adding `--build-tex` is only neccessary when testing the latest version of the
LaTeX class or if the class is not already installed using other means (e.g.
distribution LaTeX installation).

## Using SDAPS

Please run sdaps with "--help" after installing it for a list of commands.
Also check the website http://sdaps.org for some examples.

## Quality of the recognition

The quality of the recognition in SDAPS is quite good in my experience.
There is a certain amount of wrong detections, that mostly arise from people
not checking or filling out the boxes correctly. For example:
 * The cross is not inside the checkbox, but next to it
 * People cross the same box multiple times
 * People use very thick pens
 * Filling out is not done properly

As you can see, most of the errors arise from the possibility to correct
wrong marks by filling out checkboxes. SDAPS tries to be smart about this
by using different heuristics to detect the case, but it is not foolproof.

Suggestions on how to decrease the error rate are of course welcome.

### Matrix Errors

It can happen that SDAPS is not able to calculate the transformation matrix
which transforms the pixel space of the image into the mm coordinate system
used internally. If this happens the affected pages cannot be further
analysed.
It is usually possible to manually correct them using the GUI, but that can
be quite tedious.

See also TROUBLESHOOTING for some more information.
