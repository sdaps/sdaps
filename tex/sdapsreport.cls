%% start of file `sdapsreport.cls'.
%% Copyright 2010-2011 Ferdinand Schwenk (ferdisdot@gmail.com).
%
% This work may be distributed and/or modified under the  
% conditions of the LaTeX Project Public License, either version 1.3c 
% of this license or (at your option) any later version.  
% The latest version of this license is in  
%   http://www.latex-project.org/lppl.txt


%-------------------------------------------------------------------------------
% identification
%-------------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{sdapsreport}[2011/12/20%
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
\LoadClass[twoside,headings=small]{scrreprt}


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

% hyperrefs
\RequirePackage{url}
\RequirePackage{hyperref}
\hypersetup{%
  breaklinks,%
  baseurl       = http://,%
  pdfborder     = 0 0 0,%
  pdfpagemode   = UseNone,%
  pdfcreator    = \LaTeX{} with `sdapsreport' class,%
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
\RequirePackage{graphicx}

% headers and footers
\usepackage{scrlayer-scrpage}
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

% Einheiten
\RequirePackage{siunitx}

% Listen
\RequirePackage{mdwlist}

% Translation
\RequirePackage{translator}
\usedictionary{translator-sdaps-dictionary}

% Zeichenprogramm
\RequirePackage{tikz}
\usetikzlibrary{calc}


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

\setkomafont{descriptionlabel}{\normalfont}

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

\global\def\@extrainfos{}
\newcommand{\addextrainfo}[2]{\global\edef\@extrainfos{\@extrainfos #1: & #2 \cr}}%\global\edef\@extrainfos{\@extrainfos #1 & #2 \\}}

\renewcommand*\maketitle[1][1]{
  \begin{titlepage}%
    \setcounter{page}{#1}%
    \null\vfill
    \begin{center}%
      \ifx\@subject\@empty \else
        {\Large \@subject \par}%
        \vskip 3em
      \fi
      {\titlefont\huge \@title\par}%
      \vskip 3em
      {\Large \lineskip 0.75em
      \begin{tabular}[t]{c}%
        \@author
      \end{tabular}\par}%
      \vskip 1.5em
      {\Large \@date \par}%
    \end{center}
    \vskip \z@ \@plus3fill
    \begin{tabular}[t]{rl}%
      \@extrainfos
    \end{tabular}%
  \end{titlepage}%
  \global\let\maketitle\relax
  \global\let\@author\@empty
  \global\let\@date\@empty
  \global\let\@title\@empty
  \global\let\@subject\@empty
  \global\let\@extrainfos\@empty
  \global\let\author\relax
  \global\let\title\relax
  \global\let\subject\relax
  \global\let\extrainfos\relax
  \global\let\date\relax
  \global\let\and\relax
}

%-------------------------------------------------------------------------------
%                structure commands definitions
%-------------------------------------------------------------------------------
\renewcommand{\author}[1]{\def\@author{#1}}
\renewcommand{\title}[1]{\def\@title{#1}}

\def\question{{\global\let\freeformsep\relax}\subsection*}

\newcommand*{\decimaltopercent}[1]{
  \pgfset{/pgf/number format/precision=0}
  \pgfmathparse{100 * #1}
  \pgfmathroundtozerofill{\pgfmathresult}
  \SI{\pgfmathresult}{\percent}
}

\newlength{\einheit}
\newcommand*{\markdiagram}{%
  \begin{tikzpicture}[semithick]
    \pgfkeysgetvalue{/sdaps/mark/range}{\range}
    \pgfkeysgetvalue{/sdaps/mark/rangemin}{\rangemin}
    \pgfkeysgetvalue{/sdaps/mark/rangemax}{\rangemax}
    \pgfmathsetlength{\einheit}{\linewidth/\range}
    % note that we iter \key, not \x here; not sure why \x does not work.
    \foreach \key in {\rangemin,...,\rangemax}
    {
      \pgfmathsetmacro\x{\key + 1 - \rangemin}
      \pgfkeysgetvalue{/sdaps/mark/\key/fraction}{\val}
      \fill[xshift=\x\einheit,yshift=2pt, color=sdapsmarkbarcolor, draw=sdapsmarkbarframecolor, very thin]
        (-0.5\einheit, 0) rectangle
        (+0.5\einheit, \val\markbarheight);
      \node[above] at (\x\einheit, \markbarheight) {\decimaltopercent{\val}};
    }
    \pgfmathparse{max(\pgfkeysvalueof{/sdaps/mark/mean}\einheit - %
      \pgfkeysvalueof{/sdaps/mark/stddev}\einheit, \einheit)}
    \pgfmathsetlength\@tempdima{\pgfmathresult}
    \pgfmathparse{min(\pgfkeysvalueof{/sdaps/mark/mean}\einheit + %
      \pgfkeysvalueof{/sdaps/mark/stddev}\einheit, \range\einheit)}
    \pgfmathsetlength\@tempdimb{\pgfmathresult}
    \fill[color=sdapsmarkstddevcolor] %Varianz
      (\@tempdima, 0ex) rectangle (\@tempdimb, -1ex);
    \draw[line width=2pt,color=sdapsmarkmeancolor,%
      xshift=\pgfkeysvalueof{/sdaps/mark/mean}\einheit] %Mittelwert
      (0, 0ex) -- (0, -1ex-1pt);
    \draw (+1.0\einheit,0ex) -- (\range\einheit,0ex); %Rahmen.Strich
%    \draw (+0.5\einheit,2pt) -- (5.5\einheit,2pt); %Rahmen.Strich
    \draw (+0.5\einheit,2pt) -- ($(\range\einheit,2pt) + (0.5\einheit,0)$); %Rahmen.Strich
    \foreach \x in {1,...,\range}
      \draw[xshift=\x\einheit] (0,0) -- (0, -1ex-1pt) node[below]{\footnotesize\x}; %Vert.Striche
  \end{tikzpicture}
}

\newenvironment{choicequestion}[1]{%
  \question{#1}%
  \tabularx{\linewidth}{Yrl}
}{%
  \endtabularx%
}

\newenvironment{embedchoicequestion}{%
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
    \begin{description*}
      \item[\translate{answers}:] \pgfkeysvalueof{/sdaps/mark/count}
      \item[\translate{mean}:] \num{\pgfkeysvalueof{/sdaps/mark/mean}}
      \item[\translate{standard-deviation}:] \num{\pgfkeysvalueof{/sdaps/mark/stddev}}
    \end{description*}
  \end{minipage}
  \hfill
  \begin{minipage}[c]{\markdiawidth}
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
\newcommand*{\freeformtext}[1]{%
  \freeformsep
  #1\\
  \def\freeformsep{\rule{\linewidth}{0.5pt}\\}
}

\endinput
