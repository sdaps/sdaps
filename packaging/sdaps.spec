Summary: SDAPS OMR utilities
Name: sdaps
Version: 0
Release: 1%{?dist}
License: GPLv3, LPPL1.3c
Source0: https://sdaps.org/releases/%{name}-%{version}.tar.xz
Group: Applications/Science
URL: https://sdaps.org
BuildRequires: python3-devel, libtiff-devel
BuildRequires: pkgconfig, python3-pkgconfig, cairo-devel, python3-cairo-devel
BuildRequires: python3-imaging, python3-reportlab, zbar
BuildRequires: python3-opencv, python3-gobject, poppler-glib
BuildRequires: python3-setuptools, python3-pkgconfig, yum
BuildRequires: intltool
BuildRequires: meson, gcc, git-core

Recommends: opencv-python3, python3-gobject, poppler-glib, gtk3
Suggests: libtiff-tools


Requires: texlive-latex
Requires: texlive-collection-latexrecommended
Requires: texlive-collection-pictures
# So we do not need latexextra completely
Requires: texlive-siunitx, texlive-environ, texlive-lastpage, texlive-sectsty
Requires: texlive-ulem
# So we do not need the whole english langpack
Requires: texlive-hyphen-english, texlive-babel-english
Requires: texlive-sdaps

# The LaTeX package build requires l3build in addition to the rest
#BuildRequires: texlive-l3build
BuildRequires: texlive-latex
BuildRequires: texlive-collection-latexrecommended
BuildRequires: texlive-collection-pictures
BuildRequires: texlive-siunitx, texlive-environ, texlive-lastpage, texlive-sectsty
BuildRequires: texlive-ulem
BuildRequires: texlive-hyphen-english, texlive-babel-english
BuildRequires: texlive-sdaps

%description
SDAPS is a tool to carry out paper based surveys. You can create machine
readable questionnaires using LaTeX. It also provides the tools to later
analyse the scanned data, and create a report.

%prep
%autosetup -n %{name}-%{version} -S git

%build
%meson
%meson_build

%install
%meson_install

%check
%meson_test

%files
%defattr(-,root,root,-)
%doc README.md
%doc examples
%{python3_sitearch}/sdaps*
%{_datadir}/sdaps*
%{_datadir}/locale*
%{_bindir}/*

%changelog
