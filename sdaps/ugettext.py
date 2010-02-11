
import gettext


def ugettext (string) :
	u'''gettext for unicode objects
	'''
	return gettext.gettext(string.encode('UTF-8')).decode('UTF-8')

def ungettext (singular, plural, n) :
	u'''ngettext for unicode objects
	'''
	return gettext.ngettext(singular.encode('UTF-8'), plural.encode('UTF-8'), n).decode('UTF-8')
