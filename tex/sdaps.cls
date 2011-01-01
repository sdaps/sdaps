%% start of file `sdaps.cls'.
%% Copyright 2010 Ferdinand Schwenk (ferdisdot@gmail.com).
%
% This work may be distributed and/or modified under the
% conditions of the LaTeX Project Public License version 1.3c,
% available at http://www.latex-project.org/lppl/.


%-------------------------------------------------------------------------------
% identification
%-------------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{sdaps}[2010/11/08%
                      v0.1 Class for composing questionairs for SDAPS]


%-------------------------------------------------------------------------------
% debugging
%-------------------------------------------------------------------------------
\newif\if@DEBUG\@DEBUGfalse


%-------------------------------------------------------------------------------
% option processing
%-------------------------------------------------------------------------------
% ignore oneside
\DeclareOption{oneside}{\OptionNotNeeded}
% enable stamps
\newif\if@STAMP\@STAMPfalse
\DeclareOption{stamp}{\@STAMPtrue}
% enable pagemarks
\newif\if@PAGEMARK\@PAGEMARKfalse
\DeclareOption{pagemark}{\@PAGEMARKtrue}

% pass unknown options to scrartcl
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{scrartcl}}

% execute default options
\ExecuteOptions{10pt,final}

% process given options
\ProcessOptions\relax


%-------------------------------------------------------------------------------
% load base-class
%-------------------------------------------------------------------------------
\LoadClass[a4paper,twoside,headings=small]{scrartcl}


%-------------------------------------------------------------------------------
% required packages
%-------------------------------------------------------------------------------
% geometry package
\RequirePackage{geometry}
\geometry{hmargin=13mm}
\geometry{vmargin=25mm}
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
      pdfsubject    = sdaps questionaire \@title,%
      pdfkeywords   = sdaps questionaire \@title%
    }%
  }%
}

% graphics
\ifpdf
  \RequirePackage[pdftex]{graphicx}
\else
  \RequirePackage[dvips]{graphicx}\fi

% headers and footers
\usepackage{scrpage2}
\clearscrheadings
  \chead[\@author\\\@title]{\@author\\\@title}
\pagestyle{scrheadings}

% pagehooks
\RequirePackage{bophook}

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

% Zeichenprogramm
\RequirePackage{tikz}
\usetikzlibrary{calc}
\usetikzlibrary{decorations.pathmorphing}
\AtBeginPage{%
  \begin{tikzpicture}[remember picture,overlay]%
    %---------------------------------------------------------------------------
    % pagemark
    %---------------------------------------------------------------------------
    \if@PAGEMARK
      \begin{scope}[line width=\elementlinewidth, line join=miter]%
        \begin{scope}[shift={($(current page.north west) + (10mm, -12mm)$)}]%
          \draw (0,-\edgelen) -- (0, 0) -- (\edgelen,0);%
          \begin{scope}[shift={(0.5\elementlinewidth,-0.5\elementlinewidth)}]%
            \ifodd \thepage%
              \draw (3mm, -3mm) rectangle +(\boxsize,-\boxsize);%
            \else%
              \fill (3mm, -3mm) rectangle +(\boxsize,-\boxsize);%
            \fi%
          \end{scope}%
        \end{scope}%
        \begin{scope}[shift={($(current page.north east) + (-10mm, -12mm)$)}]%
          \draw (0,-\edgelen) -- (0,0) -- (-\edgelen,0);%
          \begin{scope}[shift={(-0.5\elementlinewidth,-0.5\elementlinewidth)}]%
            \fill (-3mm, -3mm) rectangle +(-\boxsize,-\boxsize);%
          \end{scope}%
        \end{scope}%
        \begin{scope}[shift={($(current page.south west) + (10mm, 12mm)$)}]%
          \draw (0,\edgelen) -- (0, 0) -- (\edgelen,0);%
          \begin{scope}[shift={(0.5\elementlinewidth,0.5\elementlinewidth)}]%
            \ifodd \thepage%
              \fill (3mm, 3mm) rectangle +(\boxsize,\boxsize);%
            \else%
              \draw (3mm, 3mm) rectangle +(\boxsize,\boxsize);%
            \fi%
          \end{scope}%
        \end{scope}%
        \begin{scope}[shift={($(current page.south east) + (-10mm, 12mm)$)}]%
          \draw (0,\edgelen) -- (0mm, 0mm) -- (-\edgelen,0);%
          \begin{scope}[shift={(-0.5\elementlinewidth,0.5\elementlinewidth)}]%
            \ifodd \thepage%
              \fill (-3mm, 3mm) rectangle +(-\boxsize,\boxsize);%
            \else%
              \draw (-3mm, 3mm) rectangle +(-\boxsize,\boxsize);%
            \fi%
          \end{scope}%
        \end{scope}%
      \end{scope}%
    \fi
    %---------------------------------------------------------------------------
    % stamp
    %---------------------------------------------------------------------------
    \if@STAMP
      \ifodd \thepage%
        \relax%
      \else%
        % questionaire-id
        \begingroup
          \begin{scope}[shift={(current page.north west)}]%
            \begin{scope}[shift={($(\questionaireidmsbx, -\questionaireidmsby) + (0, -\codeboxheight)$)}]%
              \draw (0, 0) rectangle (\thecodeboxlength\codeboxstep, \codeboxheight);%
              \@tempcnta=\value{questionaireid}%
              \begin{scope}[shift={(\thecodeboxlength\codeboxstep, 0)}]%
                \foreach \x in {0,...,\numexpr\thecodeboxlength-1\relax}%
                {%
                  \ifodd \@tempcnta%
                    \draw[fill] (-\x\codeboxstep, 0) rectangle +(-\codeboxstep, \codeboxheight);%
                  \fi%
                  \global\divide\@tempcnta by 2
                }%
              \end{scope}%
            \end{scope}%
            \begin{scope}[shift={($(\questionaireidlsbx, -\questionaireidlsby) + (0, -\codeboxheight)$)}]%
              \draw (0, 0) rectangle (\thecodeboxlength\codeboxstep, \codeboxheight);%
              \@tempcnta=\value{questionaireid}%
              \begin{scope}[shift={(\thecodeboxlength\codeboxstep, 0)}]%
                \foreach \x in {0,...,\numexpr\thecodeboxlength-1\relax}%
                {%
                  \ifodd \@tempcnta%
                    \draw[fill] (-\x\codeboxstep, 0) rectangle +(-\codeboxstep, \codeboxheight);%
                  \fi%
                  \global\divide\@tempcnta by 2
                }%
              \end{scope}%
            \end{scope}%
            \begin{scope}[shift={($(current page.north) + (0, -\questionaireidmsby) + (0, -0.5\codeboxheight)$)}]%
              \node{\usekomafont{questionaireidfont}Fragebogen-ID: \hexadecimal{questionaireid}};%
            \end{scope}%
            % survey-id
            \begin{scope}[shift={($(\surveyidmsbx, -\surveyidmsby) + (0, -\codeboxheight)$)}]%
              \draw (0, 0) rectangle (\thecodeboxlength\codeboxstep, \codeboxheight);%
              \@tempcnta=\value{surveyidmsb}%
              \begin{scope}[shift={(\thecodeboxlength\codeboxstep, 0)}]%
                \foreach \x in {0,...,\numexpr\thecodeboxlength-1\relax}%
                {%
                  \ifodd \@tempcnta%
                    \draw[fill] (-\x\codeboxstep, 0) rectangle +(-\codeboxstep, \codeboxheight);%
                  \fi%
                  \global\divide\@tempcnta by 2
                }%
              \end{scope}%
            \end{scope}%
            \begin{scope}[shift={($(\surveyidlsbx, -\surveyidlsby) + (0, -\codeboxheight)$)}]%
              \draw (0, 0) rectangle (\thecodeboxlength\codeboxstep, \codeboxheight);%
              \@tempcnta=\value{surveyidlsb}%
              \begin{scope}[shift={(\thecodeboxlength\codeboxstep, 0)}]%
                \foreach \x in {0,...,\numexpr\thecodeboxlength-1\relax}%
                {%
                  \ifodd \@tempcnta%
                    \draw[fill] (-\x\codeboxstep, 0) rectangle +(-\codeboxstep, \codeboxheight);%
                  \fi%
                  \global\divide\@tempcnta by 2
                }%
              \end{scope}%
            \end{scope}%
            \begin{scope}[shift={($(current page.north) + (0, -\surveyidmsby) + (0, -0.5\codeboxheight)$)}]%
              \node{\usekomafont{surveyidfont}Umfrage-ID: \hexadecimal{surveyidmsb}\hexadecimal{surveyidlsb}};%
            \end{scope}%
          \end{scope}%
        \endgroup
      \fi%
    \fi
    %---------------------------------------------------------------------------
    % watermark for draftmode
    %---------------------------------------------------------------------------
    \if@draft %
      \node [rotate=60,scale=10,text opacity=0.2,color=red]%
      at (current page.center) {\textsc{Entwurf}};%
    \fi %
  \end{tikzpicture}%
}


%-------------------------------------------------------------------------------
% Declaration
%-------------------------------------------------------------------------------
\newcounter{question}
\newlength{\boxheight}

\AtBeginDocument{%
  \begin{info}
    Der Fragebogen wird maschinell erfasst. Bitte mit Kugelschreiber oder nicht zu dickem Filzstift ausf\"ullen.
    \begin{minipage}[t]{10em}
      \begin{tabbing}
        Ankreuzen:\hspace{1em}\=\checkedbox\\
        Korrigieren:\>\correctedbox
      \end{tabbing}
    \end{minipage}\hfill
    \setlength\@tempdima{\linewidth}
    \addtolength{\@tempdima}{-12em}
    \begin{minipage}[t]{\@tempdima}
      Bei Auswahlfeldern d\"urfen mehrere Antworten angekreuzt werden.\\
      Bei Bewertungsfragen (Skala 1--5) darf nur ein K\"astchen Angekreuzt werden.
    \end{minipage}\\
  \end{info}
}

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

\newlength{\edgesep}
\setlength{\edgesep}{0.25cm}
\newlength{\edgelen}
\setlength{\edgelen}{2.00cm}
\newlength{\elementlinewidth}
\setlength{\elementlinewidth}{1.0bp}
\newlength{\boxsize}
\setlength{\boxsize}{3.5mm}
%\addtolength{\boxsize}{1pt}

\newcounter{codeboxlength}
\setcounter{codeboxlength}{16}
\newlength{\codeboxstep}
\setlength{\codeboxstep}{3.5mm}
\newlength{\codeboxheight}
\setlength{\codeboxheight}{3.5mm}

\newcounter{questionaireid}
\setcounter{questionaireid}{21845}
\newlength{\questionaireidmsbx}
\setlength{\questionaireidmsbx}{19.5mm}
\newlength{\questionaireidmsby}
\setlength{\questionaireidmsby}{272.5mm}
\newlength{\questionaireidlsbx}
\setlength{\questionaireidlsbx}{134.5mm}
\newlength{\questionaireidlsby}
\setlength{\questionaireidlsby}{272.5mm}
\newkomafont{questionaireidfont}{\ttfamily\textbf}

\newcounter{surveyidmsb}
\setcounter{surveyidmsb}{52197}
\newcounter{surveyidlsb}
\setcounter{surveyidlsb}{39284}
\newlength{\surveyidmsbx}
\setlength{\surveyidmsbx}{19.5mm}
\newlength{\surveyidmsby}
\setlength{\surveyidmsby}{278.5mm}
\newlength{\surveyidlsbx}
\setlength{\surveyidlsbx}{134.5mm}
\newlength{\surveyidlsby}
\setlength{\surveyidlsby}{278.5mm}
\newkomafont{surveyidfont}{\ttfamily\textbf}


\definecolor{sectionbgcolor}{gray}{0.8}
\definecolor{sectionfgcolor}{gray}{0.0}


%-------------------------------------------------------------------------------
%                style commands definitions
%-------------------------------------------------------------------------------
% symbols used 
\providecommand{\checkbox}{%
  \immediate\write\sdapsoutfile{Box=Checkbox}%
  \tikz[baseline=0.5mm]{%
    \draw[line width=\elementlinewidth] (0, 0) rectangle (\boxsize, \boxsize);%
  }%
}
\providecommand{\checkedbox}{%
  \hspace{-2pt}%
  \tikz[baseline=0.5mm]{%
    % Note: This box is *not* detected by the PDF parser later on.
    \draw[line width=\elementlinewidth] (0, 0) rectangle (\boxsize, \boxsize);%
    \begin{scope}[decoration={random steps,segment length=4pt,amplitude=1pt}]
      \draw[line width=\elementlinewidth, decorate] ($(0, 0) - (2pt,2pt)$) -- ($(\boxsize, \boxsize) + (2pt,2pt)$);%
      \draw[line width=\elementlinewidth, decorate] ($(0, \boxsize) + (-2pt,2pt)$)-- ($(\boxsize, 0) + (2pt,-2pt)$);%
    \end{scope}
  }%
}
\providecommand{\correctedbox}{%
  \tikz[baseline=0.5mm]{%
    \fill[line width=\elementlinewidth] (0, 0) rectangle +(\boxsize, \boxsize);%
  }%
}

\def\smallskip{\vspace\smallskipamount}
\def\medskip{\vspace\medskipamount}
\def\bigskip{\vspace\bigskipamount}
\newskip\smallskipamount \smallskipamount=3pt  plus 1pt minus 1pt
\newskip\medskipamount   \medskipamount  =6pt  plus 2pt minus 2pt
\newskip\bigskipamount   \bigskipamount  =12pt plus 4pt minus 4pt

%-------------------------------------------------------------------------------
%                structure commands definitions
%-------------------------------------------------------------------------------
\renewcommand{\author}[1]{\def\@author{#1}}
\renewcommand{\title}[1]{\def\@title{#1}}

\def\question{\subsection}

% http://mrunix.de/forums/showthread.php?t=59943
\newenvironment{info}{%
  \vspace{\baselineskip}\vspace{\lineskip}\vspace{-1.0em}%
  \hrule height 1pt%
  \vspace{\lineskip}%
  \vspace{\parskip}%
}{%
  \vspace{\lineskip}%
  \leavevmode\noindent\hrule height 1pt%
  \vspace{\baselineskip}\vspace{\lineskip}\vspace{-1.0em}%
}

% commands 
\providecommand{\textbox}[2]{%
  % Both baselineskip and lineskip?
  \question{#2}%
  \immediate\write\sdapsoutfile{QObject-Text=\thesubsection. #2} %
  \immediate\write\sdapsoutfile{Box=Textbox} %
  \vspace{\baselineskip}\vspace{\lineskip}\vspace{-1.0em} %
  \begingroup %
    \setlength\@tempdima{#1}%
    \@tempdimb=\linewidth%
    \advance\@tempdimb by-1pt%
    \def\sides{%
      \hbox to\@tempdimb {%
        \vrule height \@tempdima width \elementlinewidth %
        \hfill%
        \vrule width \elementlinewidth%
      }%
    }%
    \offinterlineskip %
    \hrule width \@tempdimb height \elementlinewidth %
    \sides %
    \kern-0.5\@tempdima %
    \cleaders\sides\vfill %
    \kern-0.5\@tempdima %
    \sides %
    \hrule width \@tempdimb height \elementlinewidth %
  \endgroup %
  \vspace{\baselineskip}\vspace{\lineskip}\vspace{-1.0em} %
}

%\providecommand*{\textbox}[2]{%
%  \setlength{\boxheight}{#1}%
%  \addtolength{\boxheight}{\fill}%
%  \stepcounter{question}%
%  \immediate\write\sdapsoutfile{[\thequestion]}%
%  \immediate\write\sdapsoutfile{	height=\the\boxheight}%
%  \immediate\write\sdapsoutfile{	width=\the\linewidth}%
%  #2:\checkbox\checkedbox\correctedbox\\%
%  \frame{\parbox{\linewidth}{\vspace*{\boxheight}\vspace*{\fill}\ }}\\%
%}

\newcommand{\sectbox}[1]{%
 \noindent\protect\colorbox{sectionbgcolor}{%
   \@tempdima=\hsize
   \advance\@tempdima by-2\fboxsep
   \advance\@tempdima by-2\fboxrule
   \protect\parbox{\@tempdima}{%
     \smallskip
     \raggedright % extra commands here
     \color{sectionfgcolor}\usekomafont{section}{#1} \smallskip
    }%
  }%
}

\let\origsection\section
\renewcommand{\section}[1]{%
  \origsection{#1}
  \immediate\write\sdapsoutfile{}
  \immediate\write\sdapsoutfile{QObject-Head=\thesection. #1}
}


\newenvironment{markgroup}[1]{%
  \offinterlineskip%
  \question{#1}%
  \immediate\write\sdapsoutfile{QObject-Head=\thesubsection. #1}
  \tabularx{\linewidth}{Xr*{5}{c}l}
}{%
  \endtabularx%
}

\providecommand*{\markline}[3]{%
  \immediate\write\sdapsoutfile{QObject-Mark=#1}%
  \immediate\write\sdapsoutfile{Answer-Mark=#2}%
  \immediate\write\sdapsoutfile{Answer-Mark=#3}%
  #1 & #2 & \checkbox & \checkbox & \checkbox & \checkbox & \checkbox & #3\\%
}

%\providecommand*{\singlemark}[3]{\begin{markquestion}{#1}\markline{}{#2}{#3}\end{markquestion}}

\providecommand*{\singlemark}[3]{%
  \question{#1}%
  \immediate\write\sdapsoutfile{QObject-Mark=\thesubsection. #1}%
  \immediate\write\sdapsoutfile{Answer-Mark=#2}%
  \immediate\write\sdapsoutfile{Answer-Mark=#3}%
  %\offinterlineskip%
  \begin{tabularx}{\linewidth}{Y*{5}{c}X}%
    #2 & \checkbox & \checkbox & \checkbox & \checkbox & \checkbox & #3%
  \end{tabularx}%
}

\newcounter{choiceitems}
\newcounter{maxchoiceitems}
\newenvironment{choicequestion}[2][3]{%
  \offinterlineskip%
  \setcounter{choiceitems}{1}%
  \setcounter{maxchoiceitems}{#1}%
  \question{#2}%
  \immediate\write\sdapsoutfile{QObject-Choice=\thesubsection. #2}%
  \tabularx{\linewidth}{*{\themaxchoiceitems}{X}}%
}{%
  \endtabularx%
}

\providecommand*{\choiceitem}[1]{%
  \immediate\write\sdapsoutfile{Answer-Choice=#1}%
  \ifthenelse{\thechoiceitems=\themaxchoiceitems}{%
    \setcounter{choiceitems}{1}%
    \checkbox~#1 \\%
  }{%
    \addtocounter{choiceitems}{1}%
    \checkbox~#1 &%
  }%
}

\providecommand*{\choicemulticolitem}[2]{%
  \multicolumn{#1}{l}{%
    \addtocounter{choiceitems}{#1}%
    \immediate\write\sdapsoutfile{Answer-Choice=#2}%
    \checkbox~#2%
  }
  \ifthenelse{\thechoiceitems>\themaxchoiceitems}{%
    \\
  }{%
    &
  }
}

\providecommand{\choiceitemtext}[3]{%
  \multicolumn{#2}{l}{%
    \addtocounter{choiceitems}{#2}%
    \begingroup%
        \setlength\@tempdima{#1}%
        \advance\@tempdima by -0.5\@tempdima%
        \advance\@tempdima by -0.5ex%
        \raise\@tempdima\hbox{#3~}%
        %
        \immediate\write\sdapsoutfile{Answer-Choice=#3}%
        \immediate\write\sdapsoutfile{Box=Textbox}%
        \setlength\@tempdima{#1}%
        %\addtolength\@tempdima{20\elementlinewidth}%
        \setlength\@tempdimb{2cm}%
        \@tempdimc=\@tempdima%
        \advance\@tempdimc by +2.0\elementlinewidth%
        \def\horizontallines{%
          \vbox {%
            %\vspace \elementlinewidth%
            \hrule depth 0pt width \@tempdimb height \elementlinewidth %
            \vspace \@tempdima%
            %\vspace \elementlinewidth
            %\vspace -1.0\elementlinewidth%
            \hrule depth 0pt height \elementlinewidth%
          }%
        }%
        \offinterlineskip%
        \vrule depth 0pt width \elementlinewidth height \@tempdimc %
        \horizontallines%
        \kern-0.5\@tempdimb%
        \cleaders\horizontallines\hfill%
        \kern-0.5\@tempdimb%
        \horizontallines%
        \vrule depth 0pt width \elementlinewidth height \@tempdimc%
      %}%
    \endgroup%
  }%
  \ifthenelse{\thechoiceitems>\themaxchoiceitems}{%
    \\%
  }{%
    &%
  }%
}

\sectionfont{\sectbox}

\setkomafont{disposition}{\normalfont}
\addtokomafont{section}{\bfseries\sffamily}
%\renewcommand*{\sectionheadendvskip}{\vspace*{0p t}}


%-------------------------------------------------------------------------------
% sdaps log
%-------------------------------------------------------------------------------
\AtBeginDocument{%
  \newwrite\sdapsoutfile%
  \immediate\openout\sdapsoutfile=\jobname.sdaps%
  \immediate\write\sdapsoutfile{Author=\@author}
  \immediate\write\sdapsoutfile{Title=\@title}
}

\AtEndDocument{%
  \immediate\write\sdapsoutfile{}
  \immediate\closeout\sdapsoutfile%
}

\endinput
