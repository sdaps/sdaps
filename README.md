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

LaTeX based questionnaires (`setup tex`/`stamp`):
 * pdflatex and packages:
   * PGF/TikZ
   * translator (part of beamer)
   * l3build (for building)
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

You can install sdaps using meson. To do so, run:
 * `meson setup _build`
 * `ninja -C _build`
 * `ninja -C _build install`

If you do *not* have a new enough version of the SDAPS LaTeX class installed
already, you can build and install a private copy by passing
`-Dlatex=true` to `meson setup`, i.e.
 * `$ meson setup _build -Dlatex=true` (add `--wipe` or `--reconfigure` if needed)

and continue as before. Note that in this case LaTeX will *not* find the class
in the default search path and extra steps will be needed if you want to compile
the LaTeX document without running `sdaps setup tex`.

Please note that this git repository uses submodules to pull in the LaTeX
code. This means you need to run
 * `git submodule init`

and then run
 * `git submodule update`

to checkout and update the repository after a pull.

Alternatively, do the initial clone using `git clone --recursive`.

## Standalone execution

You can also run SDAPS directly from the build directory. To do so, just skip
the installation step and run `./sdaps.py` from the source directory (this
assumes the build directory is `_build` as in the above example).

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
