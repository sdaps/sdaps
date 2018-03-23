# Copied from Avocado
#
# Since the RPM build steps are based on mock, edit your chroot config
# file (/etc/mock/<your-config>.cnf) and add the corresponding repo
# configuration there.
#

PYTHON3=$(shell which python3)
PYTHON_DEVELOP_ARGS=$(shell if ($(PYTHON3) setup.py develop --help 2>/dev/null | grep -q '\-\-user'); then echo "--user"; else echo ""; fi)
VERSION=$(shell $(PYTHON3) ../setup.py --version 2>/dev/null)
DESTDIR=/
PROJECT_DIRNAME=$(shell echo $${PWD\#\#*/})
AVOCADO_PLUGINS= #nothing for now
COMMIT=$(shell git log --pretty=format:'%H' -n 1)
SHORT_COMMIT=$(shell git log --pretty=format:'%h' -n 1)
MOCK_CONFIG=default

all:
	@echo
	@echo "Development related targets:"
	@echo "develop:    Runs 'python setup.py --develop on this tree alone"
	@echo "link:       Runs 'python setup.py --develop' in all subprojects and links the needed resources"
	@echo "clean:      Get rid of scratch, byte files and removes the links to other subprojects"
	@echo "spell:      Runs spell checker on comments and docstrings (requires python-enchant)"
	@echo
	@echo "Platform independent distribution/installtion related targets:"
	@echo "source:   Create source package"
	@echo "install:  Install on local system"
	@echo
	@echo "RPM related targets:"
	@echo "srpm:  Generate a source RPM package (.srpm)"
	@echo "rpm:   Generate binary RPMs"
	@echo
	@echo "Release related targets:"
	@echo "source-release:  Create source package for the latest tagged release"
	@echo "srpm-release:    Generate a source RPM package (.srpm) for the latest tagged release"
	@echo "rpm-release:     Generate binary RPMs for the latest tagged release"
	@echo

source: clean
	if test ! -d SOURCES; then mkdir SOURCES; fi
	rm -rf SOURCES/tmp
	cd ..; $(PYTHON3) ./setup.py sdist -d fedora/SOURCES/tmp
	cd SOURCES/tmp; tar -xf sdaps-$(VERSION).tar.gz
	mv SOURCES/tmp/sdaps-$(VERSION) SOURCES/tmp/sdaps-$(VERSION)-$(SHORT_COMMIT)
	cd SOURCES/tmp; tar -czf ../sdaps-$(VERSION)-$(SHORT_COMMIT).tar.gz sdaps-$(VERSION)-$(SHORT_COMMIT)
	rm -rf SOURCES/tmp

#source-release: clean
#	if test ! -d SOURCES; then mkdir SOURCES; fi
#	cd ..; git archive --prefix="sdaps-$(VERSION)/" -o "fedora/SOURCES/sdaps-$(VERSION).tar.gz" $(VERSION)

install:
	$(PYTHON3) setup.py install --root $(DESTDIR) $(COMPILE)

srpm: source
	if test ! -d BUILD/SRPM; then mkdir -p BUILD/SRPM; fi
	sed 's/#define commit SNAPSHOT_COMMIT/%define commit $(COMMIT)/' <sdaps.spec >sdaps-snapshot.spec
	mock -r $(MOCK_CONFIG) --resultdir BUILD/SRPM --buildsrpm --spec sdaps-snapshot.spec --sources SOURCES

rpm: srpm
	if test ! -d BUILD/RPM; then mkdir -p BUILD/RPM; fi
	mock -r $(MOCK_CONFIG) --resultdir BUILD/RPM --rebuild BUILD/SRPM/sdaps-$(VERSION).*git*.src.rpm

srpm-release: SOURCES/sdaps-$(VERSION).tar.gz
	#source-release
	if test ! -d BUILD/SRPM; then mkdir -p BUILD/SRPM; fi
	mock -r $(MOCK_CONFIG) --resultdir BUILD/SRPM --buildsrpm --spec sdaps.spec --sources SOURCES

rpm-release: srpm-release
	if test ! -d BUILD/RPM; then mkdir -p BUILD/RPM; fi
	mock -r $(MOCK_CONFIG) --resultdir BUILD/RPM --rebuild BUILD/SRPM/sdaps-$(VERSION)-*.src.rpm

clean:
	#$(PYTHON3) setup.py clean
	$(MAKE) -f $(CURDIR)/debian/rules clean || true
	rm -rf build/ MANIFEST BUILD BUILDROOT SPECS RPMS SRPMS SOURCES PYPI_UPLOAD
	#rm -rf docs/build
	for MAKEFILE in $(AVOCADO_PLUGINS); do\
		if test -f $$MAKEFILE/Makefile -o -f $$MAKEFILE/setup.py; then echo ">> UNLINK $$MAKEFILE";\
			if test -f $$MAKEFILE/Makefile; then PROJECT_DIRNAME=$(PROJECT_DIRNAME) make -C $$MAKEFILE unlink &>/dev/null || echo ">> FAIL $$MAKEFILE";\
			elif test -f $$MAKEFILE/setup.py; then cd $$MAKEFILE; $(PYTHON3) setup.py develop --uninstall $(PYTHON3_DEVELOP_ARGS); cd -; fi;\
		else echo ">> SKIP $$MAKEFILE"; fi;\
	done
	#$(PYTHON3) setup.py develop --uninstall $(PYTHON3_DEVELOP_ARGS)
	find . -name '*.pyc' -delete

develop:
	$(PYTHON3) setup.py develop $(PYTHON3_DEVELOP_ARGS)

spell:
	pylint --errors-only --disable=all --enable=spelling --spelling-dict=en_US --spelling-private-dict-file=spell.ignore * && echo OK

variables:
	@echo "PYTHON3: $(PYTHON3)"
	@echo "VERSION: $(VERSION)"
	@echo "DESTDIR: $(DESTDIR)"
	@echo "PROJECT_DIRNAME: $(PROJECT_DIRNAME)"
	@echo "AVOCADO_PLUGINS: $(AVOCADO_PLUGINS)"
	@echo "COMMIT: $(COMMIT)"
	@echo "SHORT_COMMIT: $(SHORT_COMMIT)"
	@echo "MOCK_CONFIG: $(MOCK_CONFIG)"
	@echo "PYTHON3_DEVELOP_ARGS: $(PYTHON3_DEVELOP_ARGS)"

.PHONY: source install clean variables

# implicit rule/recipe for man page creation
%.1: %.rst
	rst2man $< $@
