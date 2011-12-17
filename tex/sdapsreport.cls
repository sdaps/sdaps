%% start of file `sdapsreport.cls'.
%% Copyright 2010-2011 Ferdinand Schwenk (ferdisdot@gmail.com).
%
% This work may be distributed and/or modified under the
% conditions of the LaTeX Project Public License version 1.3c,
% available at http://www.latex-project.org/lppl/.


%-------------------------------------------------------------------------------
% identification
%-------------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{sdaps}[2011/01/04%
                      v0.1 Class for SDAPS survey-report]


%-------------------------------------------------------------------------------
% debugging
%-------------------------------------------------------------------------------
\newif\if@DEBUG\@DEBUGfalse


%-------------------------------------------------------------------------------
% option processing
%-------------------------------------------------------------------------------
% pass unknown options to scrartcl
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{scrreprt}}

% execute default options
\ExecuteOptions{12pt,final}

% process given options
\ProcessOptions\relax


%-------------------------------------------------------------------------------
% load base-class
%-------------------------------------------------------------------------------
\LoadClass[a4paper,twoside,headings=small]{scrreprt}


%-------------------------------------------------------------------------------
% required packages
%-------------------------------------------------------------------------------
% geometry package
%\RequirePackage{geometry}
%\geometry{hmargin=13mm}
%\geometry{vmargin=25mm}
%\geometry{top=21mm}
%\geometry{bottom=25mm}

% ifthen package
\RequirePackage{ifthen}

% ifpdf package
\RequirePackage{ifpdf}

% fontenc package
\RequirePackage[T1]{fontenc}

% color
\RequirePackage{color}

% Symbols (boxes)
\RequirePackage{amssymb}

% hyperrefs
\RequirePackage{url}
\ifpdf
  \RequirePackage[pdftex,]{hyperref}
\else
  \RequirePackage[dvips]{hyperref}
\fi
\hypersetup{%
  breaklinks,%
  baseurl       = http://,%
  pdfborder     = 0 0 0,%
  pdfpagemode   = UseNone,%
  pdfcreator    = \LaTeX{} with `sdaps' class,%
  pdfproducer   = \LaTeX{}
}
\AtEndOfClass{%
  \AtBeginDocument{%
    \hypersetup{%
      pdfauthor     = \@author,%
      pdftitle      = \@title,%
      pdfsubject    = sdaps report \@title,%
      pdfkeywords   = sdaps report \@title%
    }%
  }%
}

% graphics
\ifpdf
  \RequirePackage[pdftex]{graphicx}
\else
  \RequirePackage[dvips]{graphicx}
\fi

% headers and footers
\usepackage{scrpage2}
\clearscrheadings
  \chead[\@author\\\@title]{\@author\\\@title}
\pagestyle{scrheadings}

% Section formatting
\RequirePackage{sectsty}

% table of fixed width
\RequirePackage{tabularx}
% display content vertical centered
\renewcommand\tabularxcolumn[1]{m{#1}}
\newcolumntype{Y}{>{\raggedleft}X}

% check for draftmode
\RequirePackage{ifdraft}

% format counter
\RequirePackage{fmtcount}

% Einheiten
\RequirePackage[dp=1]{siunitx}

% Listen
\RequirePackage{paralist}

% KeyValue
\RequirePackage{pgfkeys}

% Zeichenprogramm
\RequirePackage{tikz}
%\usetikzlibrary{calc}


%-------------------------------------------------------------------------------
% Declaration
%-------------------------------------------------------------------------------
\newcounter{question}
\newlength{\boxheight}

%-------------------------------------------------------------------------------
%                class definition
%-------------------------------------------------------------------------------
% minimal base settings
\setlength\lineskip{1\p@}
\setlength\normallineskip{1\p@}
\renewcommand\baselinestretch{}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength\columnsep{10\p@}
\setlength\columnseprule{0\p@}
\pagestyle{scrheadings}
\pagenumbering{arabic}
\raggedbottom
\onecolumn

\newlength{\answerbarwidth}
\setlength{\answerbarwidth}{0.5\linewidth}

\newlength{\markdescwidth}
\setlength{\markdescwidth}{0.49\linewidth}
\newlength{\markdiawidth}
\setlength{\markdiawidth}{0.5\linewidth}
\newlength{\markbarheight}
\setlength{\markbarheight}{3em}


\definecolor{sdapschoicebarcolor}{gray}{0.6}
\definecolor{sdapsmarkmeancolor}{gray}{0.0}
\definecolor{sdapsmarkstddevcolor}{gray}{0.7}
\definecolor{sdapsmarkbarcolor}{gray}{0.7}
\definecolor{sdapsmarkbarframecolor}{gray}{0.0}

\definecolor{sectionbgcolor}{gray}{0.8}
\definecolor{sectionfgcolor}{gray}{0.0}


%-------------------------------------------------------------------------------
%                style commands definitions
%-------------------------------------------------------------------------------
\def\smallskip{\vspace\smallskipamount}
\def\medskip{\vspace\medskipamount}
\def\bigskip{\vspace\bigskipamount}
\newskip\smallskipamount \smallskipamount=3pt  plus 1pt minus 1pt
\newskip\medskipamount   \medskipamount  =6pt  plus 2pt minus 2pt
\newskip\bigskipamount   \bigskipamount  =12pt plus 4pt minus 4pt

\def\descriptionlabel#1{{\normalfont #1}}

\newcommand{\sectbox}[1]{%
 \noindent\protect\colorbox{sectionbgcolor}{%
   \@tempdima=\hsize
   \advance\@tempdima by-2\fboxsep
   \protect\parbox{\@tempdima}{%
     \smallskip
     \raggedright % extra commands here
     \color{sectionfgcolor}\usekomafont{section}{#1} \smallskip
    }%
  }%
}
\sectionfont{\sectbox}

\setkomafont{disposition}{\normalfont}
\addtokomafont{section}{\bfseries\sffamily}

%-------------------------------------------------------------------------------
%                structure commands definitions
%-------------------------------------------------------------------------------
\renewcommand{\author}[1]{\def\@author{#1}}
\renewcommand{\title}[1]{\def\@title{#1}}

\def\question{{\let\freeformsep\relax}\subsection*}

\newcommand*{\decimaltopercent}[1]{
  \pgfmathparse{100 * #1}
  \SI{\pgfmathresult}{\percent}
}

\newlength{\einheit}
\newcommand*{\markdiagram}{%
  \begin{tikzpicture}[semithick]
    \foreach \x in {1,...,5}
    {
      \pgfkeysgetvalue{/sdaps/mark/\x/fraction}{\val}
      \fill[xshift=\x\einheit,yshift=2pt, color=sdapsmarkbarcolor, draw=sdapsmarkbarframecolor, very thin]
        (-0.5\einheit, 0) rectangle
        (+0.5\einheit, \val\markbarheight);
      \node[above] at (\x\einheit, \markbarheight) {\decimaltopercent{\val}};
    }
    \pgfmathparse{max(\pgfkeysvalueof{/sdaps/mark/mean}\einheit - %
      \pgfkeysvalueof{/sdaps/mark/stddev}\einheit, \einheit)}
    \pgfmathsetlength\@tempdima{\pgfmathresult}
    \pgfmathparse{min(\pgfkeysvalueof{/sdaps/mark/mean}\einheit + %
      \pgfkeysvalueof{/sdaps/mark/stddev}\einheit, 5.0\einheit)}
    \pgfmathsetlength\@tempdimb{\pgfmathresult}
    \fill[color=sdapsmarkstddevcolor] %Varianz
      (\@tempdima, 0ex) rectangle (\@tempdimb, -1ex);
    \draw[line width=2pt,color=sdapsmarkmeancolor,%
      xshift=\pgfkeysvalueof{/sdaps/mark/mean}\einheit] %Mittelwert
      (0, 0ex) -- (0, -1ex-1pt);
    \draw (+1.0\einheit,0ex) -- (5\einheit,0ex); %Rahmen.Strich
    \draw (+0.5\einheit,2pt) -- (5.5\einheit,2pt); %Rahmen.Strich
    \foreach \x in {1,...,5}
      \draw[xshift=\x\einheit] (0,0) -- (0, -1ex-1pt) node[below]{\footnotesize\x}; %Vert.Striche
  \end{tikzpicture}
}

\newenvironment{choicequestion}[1]{%
  \offinterlineskip%
  \question{#1}%
  \tabularx{\linewidth}{Yrl}
}{%
  \endtabularx%
}

\newcommand*{\choiceanswer}[2]{%
  #1 &
  \decimaltopercent{#2} &
  \begin{tikzpicture}
    \fill[color=sdapschoicebarcolor] (0, 0) rectangle (#2\answerbarwidth, 1em); %Anteil
    \draw (0, 0) rectangle (\answerbarwidth, 1em); %Rahmen.Strich
  \end{tikzpicture}\\
}

\newcommand*{\markanswer}{%
  \begin{minipage}[c]{\markdescwidth}
    \pgfkeysvalueof{/sdaps/mark/lower} -- \pgfkeysvalueof{/sdaps/mark/upper}
    \begin{compactdesc}
      \item[Antworten:] \pgfkeysvalueof{/sdaps/mark/count}
      \item[Mittelwert:] \num{\pgfkeysvalueof{/sdaps/mark/mean}}
      \item[Standardabweichung:] \num{\pgfkeysvalueof{/sdaps/mark/stddev}}
    \end{compactdesc}
  \end{minipage}
  \hfill
  \begin{minipage}[c]{\markdiawidth}
    \setlength{\einheit}{0.2\linewidth}
    \markdiagram
  \end{minipage}
  \\
}

\let\freeformsep\relax
\newcommand*{\freeform}[2]{%
  \freeformsep
  \pgfmathparse{min(#1, \linewidth)}
  \includegraphics[width=\pgfmathresult pt,keepaspectratio]{#2}\\
  \def\freeformsep{\rule{\linewidth}{0.5pt}\\}
}

\endinput
