
# Import all submodules and register the toplevel grouping parsers

from sdaps import script
from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

from . import add
from . import annotate
from . import boxgallery
from . import convert
from . import cover

export = script.subparsers.add_parser('export',
    help=_("Export data from an SDAPS project."),
    description=_("""Export data from an SDAPS project. Please check the
    documentation for the provided formats for more information."""))
# Set required as an attribute rather than kwarg so that it works with python <3.7
export_subparser = export.add_subparsers(dest='format')
export_subparser.required = True

from . import gui
from . import ids

import_ = script.subparsers.add_parser('import',
    help=_("Import data into an SDAPS project."),
    description=_("""Import data into an SDAPS project. This is only useful in
    rare cases. Please check the documentation for the provided formats for more
    information."""))
# Set required as an attribute rather than kwarg so that it works with python <3.7
import_subparser = import_.add_subparsers(dest='format')
import_subparser.required = True

from . import info
from . import recognize
from . import reorder

report_ = script.subparsers.add_parser('report',
    help=_("Generate a report."))
# Set required as an attribute rather than kwarg so that it works with python <3.7
report_subparser = report_.add_subparsers(dest='format')
report_subparser.required = True

from . import reset

setup_ = script.subparsers.add_parser('setup',
    help=_("Create a new SDAPS project."))
# Set required as an attribute rather than kwarg so that it works with python <3.7
setup_subparser = setup_.add_subparsers(dest='format')
setup_subparser.required = True

from . import stamp

# And, subparsers of import/export
from . import csvdata
from . import feather

# setup subparsers (yeah, I know)
from . import setup

# Report subparsers
from . import report
from . import reporttex
