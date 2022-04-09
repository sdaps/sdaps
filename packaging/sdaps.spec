Summary: SDAPS OMR utilities
Name: sdaps
Version: 0
Release: 1%{?dist}
License: GPLv3, LPPL1.3c
Source0: https://sdaps.org/releases/%{name}-%{version}.tar.gz
Group: Applications/Science
URL: https://sdaps.org
BuildRequires: python3-devel, libtiff-devel, python3-distutils-extra
BuildRequires: pkgconfig, python3-pkgconfig, cairo-devel, python3-cairo-devel
BuildRequires: python3-imaging, python3-reportlab, zbar
BuildRequires: python3-opencv, python3-gobject, poppler-glib
BuildRequires: python3-setuptools, yum
BuildRequires: intltool
BuildRequires: gcc

Recommends: opencv-python3, python3-gobject, poppler-glib, gtk3
Suggests: libtiff-tools


#
Requires: texlive-collection-latexrecommended
Requires: texlive-collection-pictures
# So we do not need latexextra completely
Requires: texlive-siunitx, texlive-environ, texlive-lastpage, texlive-sectsty
Requires: texlive-ulem
# So we do not need the whole english langpack
Requires: texlive-hyphen-english, texlive-babel-english

# Building requires l3build in addition to the rest
BuildRequires: texlive-l3build
BuildRequires: texlive-collection-latexrecommended
BuildRequires: texlive-collection-pictures
BuildRequires: texlive-siunitx, texlive-environ, texlive-lastpage, texlive-sectsty
BuildRequires: texlive-ulem
BuildRequires: texlive-hyphen-english, texlive-babel-english


#BuildRequires: texlive-cm, texlive-cm-super, texlive-knuth-lib, texlive-ec
#BuildRequires: texlive-hyphen-base, texlive-hyphen-english
#Requires: texlive-tex, texlive-xetex, texlive-latex-bin, texlive-l3kernel
#Requires: texlive-l3packages, texlive-tools, texlive-hyperref, texlive-pgf, texlive-qrcode
#Requires: texlive-xcolor, texlive-url, texlive-koma-script, texlive-oberdiek, texlive-geometry
#Requires: texlive-sectsty, texlive-amsmath, texlive-amsfonts, texlive-environ, texlive-beamer
#Requires: texlive-siunitx, texlive-babel-english, texlive-lastpage, texlive-ulem
#Requires: texlive-mfware, texlive-mdwtools
#Requires: texlive-cm, texlive-cm-super, texlive-knuth-lib, texlive-ec
#Requires: texlive-hyphen-base, texlive-hyphen-english

%description
SDAPS is a tool to carry out paper based surveys. You can create machine
readable questionnaires using LaTeX. It also provides the tools to later
analyse the scanned data, and create a report.

%prep
%setup -q -n sdaps-1.9.9

%build
%{__python3} setup.py build --build-tex

%install
# Note: Ideally we would pass --skip-build, but the build system is too stupid
# to install data files then.
%{__python3} setup.py install --install-tex --root %{buildroot}

%check
cd test
IGNORE_PATTERN_EXTEND='\|^survey_id' ./run-test-locally.sh

%files
%defattr(-,root,root,-)
%doc README.md
%doc examples
%{python3_sitearch}/sdaps*
%{_datadir}/sdaps*
%{_datadir}/locale*
%{_bindir}/*

%changelog
