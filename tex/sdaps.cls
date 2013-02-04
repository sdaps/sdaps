%% start of file `sdaps.cls'.
%% Copyright 2010-2011 Ferdinand Schwenk (ferdisdot@gmail.com).
%% Copyright 2011 Benjamin Berg (benjamin@sipsolutions.net).
%% Copyright 2010 Tobias Simon <tobsimon@googlemail.com>
%
% This work may be distributed and/or modified under the
% conditions of the LaTeX Project Public License version 1.3c,
% available at http://www.latex-project.org/lppl/.


%-------------------------------------------------------------------------------
% identification
%-------------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{sdaps}[2011/01/04%
                      v0.1 Class for composing questionairs for SDAPS]

% Load scrbase for keyval support
\RequirePackage{scrkbase}

%-------------------------------------------------------------------------------
% debugging
%-------------------------------------------------------------------------------
\newif\if@DEBUG\@DEBUGfalse


%-------------------------------------------------------------------------------
% option processing
%-------------------------------------------------------------------------------
% enable stamps
\newif\if@STAMP\@STAMPfalse
\DeclareOption{stamp}{\@STAMPtrue}
\DeclareOption{nostamp}{\@STAMPfalse}

% enable pagemarks
\newif\if@PAGEMARK\@PAGEMARKfalse
\DeclareOption{pagemark}{\@PAGEMARKtrue}
\DeclareOption{nopagemark}{\@PAGEMARKfalse}

% Whether sdaps should print the questionnaire id
\newif\if@PrintQuestionnaireId\@PrintQuestionnaireIdfalse
\DeclareOption{no_print_questionnaire_id}{\@PrintQuestionnaireIdfalse}
\DeclareOption{print_questionnaire_id}{\@PrintQuestionnaireIdtrue}

% Whether sdaps should print the questionnaire id
\newif\if@PrintSurveyId\@PrintSurveyIdtrue
\DeclareOption{no_print_survey_id}{\@PrintSurveyIdfalse}
\DeclareOption{print_survey_id}{\@PrintSurveyIdtrue}

% pass unknown options to scrartcl
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{scrartcl}}

\newif\if@sdaps@draft\@sdaps@drafttrue
\DeclareOption{final}{\@sdaps@draftfalse}

\newif\if@style@classic\@style@classicfalse
\newif\if@style@codecxxviii\@style@codecxxviiitrue

\DefineFamily{SDAPS}
\DefineFamilyMember{SDAPS}
\DefineFamilyKey{SDAPS}{style}[code128]%
{%
  \KOMA@set@ncmdkey{style}{@tempa}{%
    {classic}{0},%
    {code128}{1}%
  }{#1}%
  \ifcase \@tempa\relax
    \@style@classictrue
    \@style@codecxxviiifalse
  \or
    \@style@classicfalse%
    \@style@codecxxviiitrue%
  \fi
}

% If it is empty, it will not be printed out
\def\globalid{}
\def\globalidlabel{}

\DefineFamilyKey{SDAPS}{globalid}[]%
{%
  \def\globalid{#1} %
}

\DefineFamilyKey{SDAPS}{globalidlabel}[]%
{%
  \def\globalidlabel{#1} %
}

% Set default options for scrartcl. Is this done correctly?
\PassOptionsToClass{headings=small}{scrartcl}
\PassOptionsToClass{twoside}{scrartcl}
% Well, I don't think that this worked in the past ...
%\PassOptionsToClass{10pt}{scrartcl}

% process given options
\FamilyProcessOptions{SDAPS}\relax

%-------------------------------------------------------------------------------
% load base-class
%-------------------------------------------------------------------------------
\LoadClass{scrartcl}


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

% fontenc package
\RequirePackage[T1]{fontenc}

% color
\RequirePackage{color}

% Symbols (boxes)
\RequirePackage{amssymb}

% For writing out the page number of boxes
\RequirePackage{refcount}

% Defines the LastPage label
\RequirePackage{lastpage}

% Environment creation that gets the body as a macro
\RequirePackage{environ}

% pagehooks
% This is a bit weird. According to the bophook documentation it should be
% loaded after the hyperref package. However, loading it *before* the hyperref
% package fixes a warning, and everything keeps working correctly.
% From the documentation:
%  The hyperref package does a lot of modification to the LaTeX kernel. Prepare
%  for the case that it is loaded. Note that it has to be loaded prior to bophook!
\RequirePackage{bophook}

% hyperrefs
\RequirePackage{url}
\RequirePackage{hyperref}
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
      pdfsubject    = sdaps questionnaire \@title,%
      pdfkeywords   = sdaps questionnaire \@title%
    }%
  }%
}

% graphics
\RequirePackage{graphicx}

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

% format counter
\RequirePackage{fmtcount}

% Babel (needed for the translator)
\RequirePackage{babel}


% Translation
\RequirePackage{translator}
\usedictionary{translator-sdaps-dictionary}

% Zeichenprogramm
\RequirePackage{tikz}
\usetikzlibrary{calc}
\usetikzlibrary{positioning}
\usetikzlibrary{decorations.pathmorphing}

% Code 128 implementation in plain TeX
\include{code128}

% http://www.tex.ac.uk/cgi-bin/texfaq2html?label=isitanum
\def\IsPositive#1{%
  TT\fi
  \ifcat_\ifnum0<0#1 _\else A\fi
}

\def\forceLR#1{\ifx\textLR\undefined#1\else\textLR{#1}\fi}

\def\@sdaps@STAMP{%
  \begingroup
    \begin{scope}[line width=\elementlinewidth, shift={(current page.south west)}]%
      \if@style@codecxxviii
        \if@PrintQuestionnaireId
          \begin{scope}[shift={($(\edgeleftmargin, \edgebottommargin) + (\barcodehpad, \barcodevpad)$)}]%
            \node(barcode)[anchor=south west,outer sep=0,inner sep=0]{\X=\barcodebarwidth\bcorr=\barcodebcorr\barheight=\barcodeheight\expandafter\code\expandafter{\qid}};%
            \node[below=1mm of barcode,distance=0,anchor=north,outer sep=0,inner sep=0]{\usekomafont{barcodefont}\qid};%
          \end{scope}
        \fi

        % We unconditionally print this barcode, it is required for the recognition
        % process.
        \begin{scope}[shift={($(\paperwidth, 0) + (-\edgerightmargin, \edgebottommargin) + (-\barcodehpad, \barcodevpad)$)}]%
          \pgfmathsetbasenumberlength{4}%
          \pgfmathdectobase{\paddedpage}{\thepage}{10}% Yes, padding to 4 chars the hard way
          \edef\barcodechars{\surveyid\paddedpage}%
          \node(barcode)[anchor=south east,outer sep=0,inner sep=0]{\X=\barcodebarwidth\bcorr=\barcodebcorr\barheight=\barcodeheight\expandafter\code\expandafter{\barcodechars}};%
          \node[below=1mm of barcode,distance=0,anchor=north,outer sep=0,inner sep=0]{\usekomafont{barcodefont}\surveyid\,\paddedpage};%
        \end{scope}

        \ifstr{\globalid}{}{}{
          \begin{scope}[shift={($(\paperwidth/2-\edgerightmargin/2+\edgeleftmargin/2, 0) + (0, \edgebottommargin) + (0, \barcodevpad)$)}]%
            \node(barcode)[anchor=south,outer sep=0,inner sep=0]{\X=\barcodebarwidth\bcorr=\barcodebcorr\barheight=\barcodeheight\expandafter\code\expandafter{\globalid}};%
            \node[below=1mm of barcode,distance=0,anchor=north,outer sep=0,inner sep=0]{\usekomafont{barcodefont}\ifstr{\globalidlabel}{}{\globalid}{\globalidlabel}};%
          \end{scope}
        }
      \fi

      \if@style@classic
        \if@PrintQuestionnaireId%
          \if@PrintSurveyId%
            \def\@questionnaire_id_shift{\boxpaddings+\codeboxheight}
          \else
            \def\@questionnaire_id_shift{0pt}
          \fi%
          \begin{scope}[shift={($(\edgeleftmargin, \edgebottommargin) + (2*\boxpaddings, \boxpaddings) + (\cornerboxsize, \@questionnaire_id_shift)$)}]%
            \draw (0, 0) rectangle (\thecodeboxlength\codeboxstep, \codeboxheight);%
            \@tempcnta=\value{questionnaireid}%
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
          \begin{scope}[shift={($(\paperwidth, 0) + (-\edgerightmargin, \edgebottommargin) + (-2*\boxpaddings, \boxpaddings) + (-\thecodeboxlength\codeboxstep, 0) + (-\cornerboxsize, \@questionnaire_id_shift)$)}]%
            \draw (0, 0) rectangle (\thecodeboxlength\codeboxstep, \codeboxheight);%
            \@tempcnta=\value{questionnaireid}%
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
          \begin{scope}[shift={($(current page.south) + (0, \edgebottommargin) + (0, \boxpaddings) + (0 ,\@questionnaire_id_shift) + (0, 0.5\codeboxheight)$)}]%
            \pgfmathsetbasenumberlength{5}\pgfmathdectoBase{\@temphexa}{\value{questionnaireid}}{10}%
            \node{\usekomafont{questionnaireidfont}{\translate{questionnaireid} \@temphexa}};%
          \end{scope}%
        \fi%
        \if@PrintSurveyId%
          % survey-id
          \begin{scope}[shift={($(\edgeleftmargin, \edgebottommargin) + (2*\boxpaddings, \boxpaddings) + (\cornerboxsize, 0)$)}]%
            \draw (0, 0) rectangle (\thecodeboxlength\codeboxstep, \codeboxheight);%
            \@tempcnta=\value{surveyidmshw}%
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
          \begin{scope}[shift={($(\paperwidth, 0) + (-\edgerightmargin, \edgebottommargin) + (-2*\boxpaddings, \boxpaddings) + (-\thecodeboxlength\codeboxstep, 0) + (-\cornerboxsize, 0)$)}]%
            \draw (0, 0) rectangle (\thecodeboxlength\codeboxstep, \codeboxheight);%
            \@tempcnta=\value{surveyidlshw}%
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
          \begin{scope}[shift={($(current page.south) + (0, \edgebottommargin) + (0, \boxpaddings) + (0, 0.5\codeboxheight)$)}]%
            \pgfmathsetbasenumberlength{4}\pgfmathdectoBase{\@temphexa}{\value{surveyidlshw}}{16}%
            \pgfmathsetbasenumberlength{4}\pgfmathdectoBase{\@temphexb}{\value{surveyidmshw}}{16}%
            \node{\usekomafont{surveyidfont}{\translate{surveyid} \@temphexb\@temphexa}};%
          \end{scope}%
        \fi%
      \fi
    \end{scope}%
  \endgroup
}

\PageLayout{%
  \begin{tikzpicture}[remember picture,overlay]%
    %---------------------------------------------------------------------------
    % pagemark
    %---------------------------------------------------------------------------
    \if@PAGEMARK
      \begin{scope}[line width=\elementlinewidth, line join=miter]%
        \begin{scope}[shift={($(current page.north west) + (\edgeleftmargin, -\edgetopmargin)$)}]%
          \draw (0,-\edgelen) -- (0, 0) -- (\edgelen,0);%
          \if@style@classic%
            \ifcase\thepage%
              % Case 0
              \draw (\boxpaddings, -\boxpaddings) rectangle +(\cornerboxsize,-\cornerboxsize);%
            \or%
              % Case 1
              \draw (\boxpaddings, -\boxpaddings) rectangle +(\cornerboxsize,-\cornerboxsize);%
            \or%
              % Case 2
              \fill (\boxpaddings, -\boxpaddings) rectangle +(\cornerboxsize,-\cornerboxsize);%
            \or%
              % Case 3
              \fill (\boxpaddings, -\boxpaddings) rectangle +(\cornerboxsize,-\cornerboxsize);%
            \or%
              % Case 4
              \fill (\boxpaddings, -\boxpaddings) rectangle +(\cornerboxsize,-\cornerboxsize);%
            \or%
              % Case 5
              \fill (\boxpaddings, -\boxpaddings) rectangle +(\cornerboxsize,-\cornerboxsize);%
            \or%
              % Case 6
              \draw (\boxpaddings, -\boxpaddings) rectangle +(\cornerboxsize,-\cornerboxsize);%
            \else%
              % Optional
              \draw (\boxpaddings, -\boxpaddings) rectangle +(\cornerboxsize,-\cornerboxsize);%
            \fi%
          \fi%
        \end{scope}%
        \begin{scope}[shift={($(current page.north east) + (-\edgerightmargin, -\edgetopmargin)$)}]%
          \draw (0,-\edgelen) -- (0,0) -- (-\edgelen,0);%
          \if@style@classic%
            \ifcase\thepage%
              % Case 0
              \draw (-\boxpaddings, -\boxpaddings) rectangle +(-\cornerboxsize,-\cornerboxsize);%
            \or%
              % Case 1
              \fill (-\boxpaddings, -\boxpaddings) rectangle +(-\cornerboxsize,-\cornerboxsize);%
            \or%
              % Case 2
              \fill (-\boxpaddings, -\boxpaddings) rectangle +(-\cornerboxsize,-\cornerboxsize);%
            \or%
              % Case 3
              \draw (-\boxpaddings, -\boxpaddings) rectangle +(-\cornerboxsize,-\cornerboxsize);%
            \or%
              % Case 4
              \draw (-\boxpaddings, -\boxpaddings) rectangle +(-\cornerboxsize,-\cornerboxsize);%
            \or%
              % Case 5
              \draw (-\boxpaddings, -\boxpaddings) rectangle +(-\cornerboxsize,-\cornerboxsize);%
            \or%
              % Case 6
              \draw (-\boxpaddings, -\boxpaddings) rectangle +(-\cornerboxsize,-\cornerboxsize);%
            \else%
              % Optional
              \draw (-\boxpaddings, -\boxpaddings) rectangle +(-\cornerboxsize,-\cornerboxsize);%
            \fi%
          \fi%
        \end{scope}%
        \begin{scope}[shift={($(current page.south west) + (\edgeleftmargin, \edgebottommargin)$)}]%
          \draw (0,\edgelen) -- (0, 0) -- (\edgelen,0);%
          \if@style@classic%
            \ifcase\thepage%
              % Case 0
              \draw (\boxpaddings, \boxpaddings) rectangle +(\cornerboxsize,\cornerboxsize);%
            \or%
              % Case 1
              \fill (\boxpaddings, \boxpaddings) rectangle +(\cornerboxsize,\cornerboxsize);%
            \or%
              % Case 2
              \draw (\boxpaddings, \boxpaddings) rectangle +(\cornerboxsize,\cornerboxsize);%
            \or%
              % Case 3
              \fill (\boxpaddings, \boxpaddings) rectangle +(\cornerboxsize,\cornerboxsize);%
            \or%
              % Case 4
              \fill (\boxpaddings, \boxpaddings) rectangle +(\cornerboxsize,\cornerboxsize);%
            \or%
              % Case 5
              \draw (\boxpaddings, \boxpaddings) rectangle +(\cornerboxsize,\cornerboxsize);%
            \or%
              % Case 6
              \draw (\boxpaddings, \boxpaddings) rectangle +(\cornerboxsize,\cornerboxsize);%
            \else%
              % Optional
              \draw (\boxpaddings, \boxpaddings) rectangle +(\cornerboxsize,\cornerboxsize);%
            \fi%
          \fi%
        \end{scope}%
        \begin{scope}[shift={($(current page.south east) + (-\edgerightmargin, \edgebottommargin)$)}]%
          \draw (0,\edgelen) -- (0mm, 0mm) -- (-\edgelen,0);%
          \if@style@classic%
            \ifcase\thepage%
              % Case 0
              \draw (-\boxpaddings, \boxpaddings) rectangle +(-\cornerboxsize,\cornerboxsize);%
            \or%
              % Case 1
              \fill (-\boxpaddings, \boxpaddings) rectangle +(-\cornerboxsize,\cornerboxsize);%
            \or%
              % Case 2
              \draw (-\boxpaddings, \boxpaddings) rectangle +(-\cornerboxsize,\cornerboxsize);%
            \or%
              % Case 3
              \fill (-\boxpaddings, \boxpaddings) rectangle +(-\cornerboxsize,\cornerboxsize);%
            \or%
              % Case 4
              \draw (-\boxpaddings, \boxpaddings) rectangle +(-\cornerboxsize,\cornerboxsize);%
            \or%
              % Case 5
              \draw (-\boxpaddings, \boxpaddings) rectangle +(-\cornerboxsize,\cornerboxsize);%
            \or%
              % Case 6
              \fill (-\boxpaddings, \boxpaddings) rectangle +(-\cornerboxsize,\cornerboxsize);%
            \else%
              % Optional
              \draw (-\boxpaddings, \boxpaddings) rectangle +(-\cornerboxsize,\cornerboxsize);%
            \fi%
          \fi%
        \end{scope}%
      \end{scope}%
    \fi
    %---------------------------------------------------------------------------
    % stamp
    %---------------------------------------------------------------------------
    \if@STAMP
      \if@twoside
        \ifodd \thepage%
          \if@forceSTAMP%
            % Stamp on the last page, even if it is odd
            % This is simply a convenience to allow duplex for one paged documents
            \@sdaps@STAMP
          \fi
        \else%
          % questionnaire-id
          \@sdaps@STAMP
        \fi%
      \else
        % Always stamp in simplex mode
        \@sdaps@STAMP
      \fi
    \fi
    %---------------------------------------------------------------------------
    % watermark for non final mode
    %---------------------------------------------------------------------------
    \if@sdaps@draft %
      \node [rotate=60,scale=10,text opacity=0.2,color=red]%
      at (current page.center) {\textsc{\translate{draft}}};%
    \fi %
  \end{tikzpicture}%
}


%-------------------------------------------------------------------------------
% Declaration
%-------------------------------------------------------------------------------
\newcounter{question}
\newlength{\boxheight}

\NewEnviron{questionnaire}[1][]{
  \if@PrintQuestionnaireId
    \protectedimmediatewrite\sdapsoutfile{PrintQuestionnaireId=1}
  \else
    \protectedimmediatewrite\sdapsoutfile{PrintQuestionnaireId=0}
  \fi
  \if@PrintSurveyId
    \protectedimmediatewrite\sdapsoutfile{PrintSurveyId=1}
  \else
    \protectedimmediatewrite\sdapsoutfile{PrintSurveyId=0}
  \fi
  \protectedimmediatewrite\sdapsoutfile{Pages=\getpagerefnumber{LastPage}}
  \pgfpoint{\paperwidth}{\paperheight}
  \pgfgetlastxy{\@sdaps@width}{\@sdaps@height}
  \protectedimmediatewrite\sdapsoutfile{PageSize=\@sdaps@width, \@sdaps@height}
  \if@twoside
    \protectedimmediatewrite\sdapsoutfile{Duplex=True}
  \else
    \protectedimmediatewrite\sdapsoutfile{Duplex=False}
  \fi
  % Only one can be true ...
  \if@style@classic
    \protectedimmediatewrite\sdapsoutfile{Style=classic}
  \fi
  \if@style@codecxxviii
    \protectedimmediatewrite\sdapsoutfile{Style=code128}
  \fi
  \protectedimmediatewrite\sdapsoutfile{GlobalID=\globalid}
  \protectedimmediatewrite\sdapsoutfile{GlobalIDLabel=\globalidlabel}
  %
  \foreach \qid in \questionnaireids{%
    \@forceSTAMPfalse
    \setcounter{page}{1}
    \if\IsPositive{\qid}%
      \setcounter{questionnaireid}{\qid}%
    \else%
      \setcounter{questionnaireid}{0}%
    \fi%
    \setcounter{section}{0}

    \ifstr{#1}{noinfo}{}{
      \begin{info}
        \translate{infotext}\\
        \begin{tabularx}{\textwidth}{llcX}
          \translate{info_cross}: & \checkedbox &\quad & \translate{info_select} \\
          \translate{info_correct}: & \correctedbox & & \translate{info_mark} \\
        \end{tabularx}
      \end{info}
    }

    \BODY

    % Force a stamp on the next last page of the questionnaire
    \@forceSTAMPtrue

    \clearpage

    \protectedimmediatewrite\sdapsoutfile{}
    % Just close the file here so nothing is written anymore ...
    % It would be good to also redefine the protectedimmediatewrite macro,
    % but not sure how that can be done.
    \immediate\closeout\sdapsoutfile%
  }
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

\newif\if@forceSTAMP\@forceSTAMPfalse

\newlength{\edgeleftmargin}
\setlength{\edgeleftmargin}{10mm}
\newlength{\edgerightmargin}
\setlength{\edgerightmargin}{10mm}
\newlength{\edgetopmargin}
\setlength{\edgetopmargin}{12mm}
\newlength{\edgebottommargin}
\setlength{\edgebottommargin}{12mm}
\newlength{\edgelen}
\setlength{\edgelen}{2.00cm}
\newlength{\elementlinewidth}
\setlength{\elementlinewidth}{1.0bp}
\newlength{\boxsize}
\setlength{\boxsize}{3.5mm}
\newlength{\boxpaddings}
\setlength{\boxpaddings}{3mm}
\addtolength{\boxsize}{-\elementlinewidth}

% Settings for cornerboxes (used in classic style)

\newlength{\cornerboxsize}
\setlength{\cornerboxsize}{3.5mm}

% Settings for codeboxes (used in classic style)
\newcounter{codeboxlength}
\setcounter{codeboxlength}{16}
\newlength{\codeboxstep}
\setlength{\codeboxstep}{3.5mm}
\newlength{\codeboxheight}
\setlength{\codeboxheight}{3.5mm}

% Settings for code128 barcodes (used in code128 style, who would have thought?)
\newlength{\barcodeheight}
\setlength{\barcodeheight}{6.5mm}
% This is the same as the default
\newlength{\barcodebarwidth}
\setlength{\barcodebarwidth}{0.33mm}
% Same as default. Barwidth is decreased for printing by this value.
\newlength{\barcodebcorr}
\setlength{\barcodebcorr}{0.020mm}

% The padding on the left/right of a barcode. This is the distance that the
% barcodes will be printed from the cornermarks
% Choosen to be the same as the barcode height. Note that the Code-128
% standard requires a quiet zone of max(10*modulesize, ~6.4mm).
\newlength{\barcodehpad}
\setlength{\barcodehpad}{6.5mm}

% This needs to be smaller than 6.5mm because otherwise the content is too close.
% We set it so that it forms a golden ratio 6.5mm*(sqrt(5/4)-0.5). This means
% we have about 4.5mm padding to the content.
\newlength{\barcodevpad}
\setlength{\barcodevpad}{4.02mm}

\newkomafont{barcodefont}{\ttfamily\footnotesize}

% we need one to consume in the for loop
\def\questionnaireids{NONE}

% TODO: We could support arbitrary IDs in code128 mode, maybe get rid of
% this counter, or add a macro for the id and simply not use it in code128 mode?
\newcounter{questionnaireid}
\setcounter{questionnaireid}{21845}
\newkomafont{questionnaireidfont}{\ttfamily\textbf}

\newcounter{surveyidmshw}
\setcounter{surveyidmshw}{52197}
\newcounter{surveyidlshw}
\setcounter{surveyidlshw}{39284}
\def\surveyid{3420821876}
\newkomafont{surveyidfont}{\ttfamily\textbf}

\newcounter{choicegroupnumchoices}
\setcounter{choicegroupnumchoices}{-1}

\newcounter{checkboxnum}
\setcounter{checkboxnum}{0}

\newcounter{textboxnum}
\setcounter{textboxnum}{0}

\definecolor{sectionbgcolor}{gray}{0.8}
\definecolor{sectionfgcolor}{gray}{0.0}

% Execute sdaps.opt file to allow SDAPS to override any options
\InputIfFileExists{sdaps.opt}{}{}

\long\def \protectedimmediatewrite#1#2{%
  \begingroup
    \let\protect\noexpand%
    \immediate\write#1{#2}%
  \endgroup
}

%common font settings
\newkomafont{questionfont}{}
\newkomafont{choicefont}{}
%singlemark
\newkomafont{singlemarkquestionfont}{\usekomafont{questionfont}}
\newkomafont{singlemarkchoicefont}{\usekomafont{choicefont}}
%markgroup
\newkomafont{marklinequestionfont}{\usekomafont{questionfont}}
\newkomafont{marklinechoicefont}{\usekomafont{choicefont}}
%choicequestion
\newkomafont{choiceitemfont}{\usekomafont{choicefont}}
%choicegroup
\newkomafont{choicegroupchoicefont}{\usekomafont{questionfont}}
\newkomafont{choicegrouplinefont}{\usekomafont{choicefont}}


%-------------------------------------------------------------------------------
%                style commands definitions
%-------------------------------------------------------------------------------
\providecommand{\addinfo}[2]{%
  \protectedimmediatewrite\sdapsoutfile{#1=#2}%
}

\providecommand{\checkbox}{\@ifstar
    \checkboxStar%
    \checkboxNoStar%
}

\providecommand{\checkboxNoStar}{%
  \forceLR{%
  \mbox{\label{checkbox\thecheckboxnum}\pgfsys@markposition{checkbox\thecheckboxnum}%
  \pgfsys@getposition{pgfpageorigin}{\@sdaps@pageorigin}%
  \pgfsys@getposition{checkbox\thecheckboxnum}{\@sdaps@checkboxpos}%
  \pgfpointadd{\@sdaps@checkboxpos}{%
    \pgfpointadd{\@sdaps@pageorigin}{\pgfpoint{0pt}{0.5\boxsize-0.5em+0.5\elementlinewidth + 0.5\elementlinewidth+\boxsize}}%
  }%
  \pgfgetlastxy{\@sdaps@x}{\@sdaps@y}%
  \pgfpoint{\boxsize+\elementlinewidth}{\boxsize+\elementlinewidth}%
  \pgfgetlastxy{\@sdaps@width}{\@sdaps@height}%
  \protectedimmediatewrite\sdapsoutfile{Box=Checkbox, \getpagerefnumber{checkbox\thecheckboxnum}, \@sdaps@x, \@sdaps@y, \@sdaps@height, \@sdaps@width}%
  \tikz[baseline=-0.5\boxsize+0.5em-0.5\elementlinewidth]{%
    \draw[line width=\elementlinewidth] (0, 0) rectangle (\boxsize, \boxsize);%
  }\addtocounter{checkboxnum}{1}}%
}}
\providecommand{\checkboxStar}{%
  \tikz[baseline=-0.5\boxsize+0.5em-0.5\elementlinewidth]{%
    \draw[line width=\elementlinewidth] (0, 0) rectangle (\boxsize, \boxsize);%
  }%
}
\providecommand{\checkedbox}{%
  \hspace{-2pt}%
  \tikz[baseline=-0.5\boxsize+0.5em-0.5\elementlinewidth]{%
    \draw[line width=\elementlinewidth] (0, 0) rectangle (\boxsize, \boxsize);%
    \begin{scope}[decoration={random steps,segment length=4pt,amplitude=1pt}]
      \draw[line width=\elementlinewidth, decorate] ($(0, 0) - (2pt,2pt)$) -- ($(\boxsize, \boxsize) + (2pt,2pt)$);%
      \draw[line width=\elementlinewidth, decorate] ($(0, \boxsize) + (-2pt,2pt)$)-- ($(\boxsize, 0) + (2pt,-2pt)$);%
    \end{scope}
  }%
}
\providecommand{\correctedbox}{%
  \hspace{-2pt}%
  \tikz[baseline=-0.5\boxsize+0.5em-0.5\elementlinewidth]{%
    \begin{scope}[decoration={random steps,segment length=4pt,amplitude=1pt}]
      \draw[line width=\elementlinewidth, decorate] ($(0, 0) - (2pt,2pt)$) -- ($(\boxsize, \boxsize) + (2pt,2pt)$);%
      \draw[line width=\elementlinewidth, decorate] ($(0, \boxsize) + (-2pt,2pt)$)-- ($(\boxsize, 0) + (2pt,-2pt)$);%
    \end{scope}
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
\renewcommand{\author}[1]{\def\@author{#1}\protectedimmediatewrite\sdapsoutfile{Author=#1}}
\renewcommand{\title}[1]{\def\@title{#1}\protectedimmediatewrite\sdapsoutfile{Title=#1}}

\def\question#1{\subsection{\usekomafont{questionfont}#1}}

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
\providecommand{\textbox}{\@ifstar
    {\sdaps@textbox{}}%
    {\sdaps@textbox{\cleaders\sides\vfill}}%
}
\providecommand{\sdaps@textbox}[3]{%
  % Both baselineskip and lineskip?
  \question{#3}%
  \protectedimmediatewrite\sdapsoutfile{QObject-Text=\arabic{section}.\arabic{subsection}. #3} %
  \label{textbox\thetextboxnum}%
  \pgfsys@getposition{pgfpageorigin}{\@sdaps@pageorigin}%
  \pgfsys@getposition{textboxtop\thetextboxnum}{\@sdaps@textboxtoppos}%
  \pgfpointadd{\@sdaps@textboxtoppos}{%
    \pgfpointadd{\@sdaps@pageorigin}{\pgfpoint{0.5\elementlinewidth}{-0.5\elementlinewidth}}%
  }%
  \pgfgetlastxy{\@sdaps@x}{\@sdaps@y}%
%
  \pgfsys@getposition{textboxbottom\thetextboxnum}{\@sdaps@textboxbottompos}%
  \pgfpointadd{\@sdaps@textboxtoppos}{%
    \pgfpointadd{\pgfpointscale{-1}{\@sdaps@textboxbottompos}}{
      \pgfpoint{\linewidth-\elementlinewidth}{-\elementlinewidth}%
    }%
  }%
  \pgfgetlastxy{\@sdaps@width}{\@sdaps@height}%
  \protectedimmediatewrite\sdapsoutfile{Box=Textbox, \getpagerefnumber{textbox\thetextboxnum}, \@sdaps@x, \@sdaps@y, \@sdaps@width, \@sdaps@height} %
  \vspace{-\lineskip}%
  \begingroup %
    \setlength\@tempdima{#2}%
    \def\sides{%
      \hbox to\linewidth {%
        \vrule depth 0pt height \@tempdima width \elementlinewidth %
        \hfill%
        \vrule depth 0pt width \elementlinewidth%
      }%
    }%
    \offinterlineskip %
    \pgfsys@markposition{textboxtop\thetextboxnum}%
    \hrule width \linewidth height \elementlinewidth %
    %\kern -\elementlinewidth%
    \sides %
    \kern-0.5\@tempdima %
    #1 %
    \kern-0.5\@tempdima %
    \nobreak %
    \sides %
    %\kern -\elementlinewidth%
    \hrule width \linewidth height \elementlinewidth %
    \pgfsys@markposition{textboxbottom\thetextboxnum}%
    \addtocounter{textboxnum}{1}%
    %
  \endgroup %
  \vspace{\baselineskip}%
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
  \protectedimmediatewrite\sdapsoutfile{}
  \protectedimmediatewrite\sdapsoutfile{QObject-Head=\arabic{section}. #1}
}


\newenvironment{choicegroup}[1]{%
  \offinterlineskip%
  \question{#1}%
  \protectedimmediatewrite\sdapsoutfile{QObject-Head=\arabic{section}.\arabic{subsection}. #1} %
  \setcounter{choicegroupnumchoices}{0} %
  \global\def\@sdaps@choicegroup@start{\tabularx{\linewidth}{X*{\thechoicegroupnumchoices}{c}}} %
  \global\def\@sdaps@choicegroup@boxes{} %
}{%
  \ifnum\thechoicegroupnumchoices>-1 %
    % Throw error \@ehb == you have lost some text
    \PackageError{sdaps}{Got a choicegroup without any choice lines!}\@ehb %
  \fi %
  \endtabularx%
}

\providecommand*{\choiceline}[1]{%
  \@sdaps@choicegroup@start %
  \global\def\@sdaps@choicegroup@start{} %
  % This is not really elegant, couldn't we just check whether choicegroup@start
  % is empty?
  \ifnum\thechoicegroupnumchoices>0
    \\ %
    \setcounter{choicegroupnumchoices}{-1} %
  \fi %
  \protectedimmediatewrite\sdapsoutfile{QObject-Choice=#1}%
  % First move to the next line (as it is not part of the @start macro)
  {\usekomafont{choicegrouplinefont}#1} \@sdaps@choicegroup@boxes \\ %
}

\providecommand*{\groupaddchoice}[1]{%
  \ifnum\thechoicegroupnumchoices<0
    % Throw error \@ehb == you have lost some text
    % Why is this emitted multiple times? And can one create a multiline message?
    \PackageError{sdaps}{Tried to add a new choice, but not at the beginning of a choicegroup environment!}\@ehb
  \else
    \stepcounter{choicegroupnumchoices}%
    \g@addto@macro{\@sdaps@choicegroup@start}{& {\usekomafont{choicegroupchoicefont}#1}}%
    \g@addto@macro{\@sdaps@choicegroup@boxes}{& \protectedimmediatewrite\sdapsoutfile{Answer-Choice=#1} \checkbox}%
  \fi
}


\newenvironment{markgroup}[1]{%
  \offinterlineskip%
  \question{#1}%
  \protectedimmediatewrite\sdapsoutfile{QObject-Head=\arabic{section}.\arabic{subsection}. #1}
  \tabularx{\linewidth}{Xr*{5}{c}l}
}{%
  \endtabularx%
}

\providecommand*{\markline}[3]{%
  \protectedimmediatewrite\sdapsoutfile{QObject-Mark=#1}%
  \protectedimmediatewrite\sdapsoutfile{Answer-Mark=#2}%
  \protectedimmediatewrite\sdapsoutfile{Answer-Mark=#3}%
  {\usekomafont{marklinequestionfont}#1} & {\usekomafont{marklinechoicefont}#2} & {\usekomafont{marklinechoicefont}\checkbox} & {\usekomafont{marklinechoicefont}\checkbox} & {\usekomafont{marklinechoicefont}\checkbox} & {\usekomafont{marklinechoicefont}\checkbox} & {\usekomafont{marklinechoicefont}\checkbox} & {\usekomafont{marklinechoicefont}#3}\\%
}

%\providecommand*{\singlemark}[3]{\begin{markquestion}{#1}\markline{}{#2}{#3}\end{markquestion}}

\providecommand*{\singlemark}[3]{%
  \question{#1}%
  \protectedimmediatewrite\sdapsoutfile{QObject-Mark=\arabic{section}.\arabic{subsection}. #1}%
  \protectedimmediatewrite\sdapsoutfile{Answer-Mark=#2}%
  \protectedimmediatewrite\sdapsoutfile{Answer-Mark=#3}%
  %\offinterlineskip%
  \begin{tabularx}{\linewidth}{Y*{5}{c}X}%
    {\usekomafont{singlemarkchoicefont}#2} & {\usekomafont{singlemarkchoicefont}\checkbox} & {\usekomafont{singlemarkchoicefont}\checkbox} & {\usekomafont{singlemarkchoicefont}\checkbox} & {\usekomafont{singlemarkchoicefont}\checkbox} & {\usekomafont{singlemarkchoicefont}\checkbox} & {\usekomafont{singlemarkchoicefont}#3}%
  \end{tabularx}%
}

\newcounter{choiceitems}
\newcounter{maxchoiceitems}
\newenvironment{choicequestion}[2][3]{%
  \offinterlineskip%
  \setcounter{choiceitems}{1}%
  \setcounter{maxchoiceitems}{#1}%
  \question{#2}%
  \protectedimmediatewrite\sdapsoutfile{QObject-Choice=\arabic{section}.\arabic{subsection}. #2}%
  \tabularx{\linewidth}{*{\themaxchoiceitems}{X}}%
  % We insert dummy elements into each cell, because otherwise there may be
  % layouting issues.
  \global\def\@sdaps@choiceitems@dummy{}%
  \loop{}%
  \ifnum\thechoiceitems<\themaxchoiceitems{\addtocounter{choiceitems}{1}} \global\edef\@sdaps@choiceitems@dummy{\@sdaps@choiceitems@dummy &}%
  \repeat%
  \@sdaps@choiceitems@dummy%
   \rule[-1em]{0pt}{3em}% Insert known space (1em below, 2em above the baseline)
   \cr%
  \noalign{\vspace{-\extrarowheight}\vspace{-3.0em}}% Subtract known space again.
  \setcounter{choiceitems}{1}%
}{%
  \endtabularx%
}

\providecommand*{\choiceitem}[1]{%
  \protectedimmediatewrite\sdapsoutfile{Answer-Choice=#1}%
  \ifthenelse{\thechoiceitems=\themaxchoiceitems}{%
    \setcounter{choiceitems}{1}%
    {\usekomafont{choiceitemfont}\checkbox~#1} \\%
  }{%
    \addtocounter{choiceitems}{1}%
    {\usekomafont{choiceitemfont}\checkbox~#1} &%
  }%
}

\providecommand*{\choicemulticolitem}[2]{%
  \multicolumn{#1}{l}{%
    \addtocounter{choiceitems}{#1}%
    \protectedimmediatewrite\sdapsoutfile{Answer-Choice=#2}%
    {\usekomafont{choiceitemfont}\checkbox~#2}%
  }
  \ifthenelse{\thechoiceitems>\themaxchoiceitems}{%
    \setcounter{choiceitems}{1}%
    \\
  }{%
    &
  }
}

% We need to declare them outside, they seem to be leaked or something like that
\newdimen\@tempdimlower%
\newdimen\@tempdimboxlower%
\newdimen\@tempdimheight%
\newdimen\@tempdimruleheight%
\providecommand{\choiceitemtext}[3]{%
  \multicolumn{#2}{l}{%
    \addtocounter{choiceitems}{#2}%
    \begingroup%
      {\usekomafont{choiceitemfont}#3}~%
      %
      \setlength\@tempdimheight{#1}%
      %
      \setlength\@tempdimlower{0pt}%
      \advance\@tempdimlower by -0.5\@tempdimheight%
      \advance\@tempdimlower by 0.8ex%
      %
      \setlength\@tempdimboxlower\@tempdimlower%
      \advance\@tempdimboxlower by -\smallskipamount%
      %
      \setlength\@tempdima{2cm}%
      \@tempdimruleheight=\@tempdimheight%
      \advance\@tempdimruleheight by +2.0\elementlinewidth%
      \advance\@tempdimruleheight by \@tempdimlower%
      %
      \protectedimmediatewrite\sdapsoutfile{Answer-Choice=#3}%
      %
      \label{textbox\thetextboxnum}%
      \pgfsys@getposition{pgfpageorigin}{\@sdaps@pageorigin}%
      \pgfsys@getposition{textboxleft\thetextboxnum}{\@sdaps@textboxleftpos}%
      \pgfpointadd{\@sdaps@textboxleftpos}{%
        \pgfpointadd{\@sdaps@pageorigin}{\pgfpoint{0.5\elementlinewidth}{\@tempdimruleheight-0.5\elementlinewidth}}%
      }%
      \pgfgetlastxy{\@sdaps@x}{\@sdaps@y}%
      %
      \pgfsys@getposition{textboxright\thetextboxnum}{\@sdaps@textboxrightpos}%
      \pgfpointadd{\@sdaps@textboxrightpos}{%
        \pgfpointadd{\pgfpointscale{-1}{\@sdaps@textboxleftpos}}{
          \pgfpoint{-\elementlinewidth}{#1+\elementlinewidth}%
        }%
      }%
      \pgfgetlastxy{\@sdaps@width}{\@sdaps@height}%
      \protectedimmediatewrite\sdapsoutfile{Box=Textbox, \getpagerefnumber{textbox\thetextboxnum}, \@sdaps@x, \@sdaps@y, \@sdaps@width, \@sdaps@height}%
      %
      \def\horizontallines{%
        \hbox{%
          \raise\@tempdimboxlower\vbox{%
            \hrule width \@tempdima height \elementlinewidth %
            \vspace \@tempdimheight%
            \hrule height \elementlinewidth%
            \vspace\smallskipamount%
          }%
        }%
      }%
      \pgfsys@markposition{textboxleft\thetextboxnum}%
      \vrule depth -\@tempdimlower width \elementlinewidth height \@tempdimruleheight %
      %\kern -\elementlinewidth%
      \horizontallines%
      \kern-0.5\@tempdima%
      \cleaders\horizontallines\hfill%
      \kern-0.5\@tempdima%
      \horizontallines%
      %\kern -\elementlinewidth%
      \vrule depth -\@tempdimlower width \elementlinewidth height \@tempdimruleheight%
      \pgfsys@markposition{textboxright\thetextboxnum}%
      \addtocounter{textboxnum}{1}%
    \endgroup%
  }%
  \ifthenelse{\thechoiceitems>\themaxchoiceitems}{%
    \setcounter{choiceitems}{1}%
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

\newwrite\sdapsoutfile%
\immediate\openout\sdapsoutfile=\jobname.sdaps%


\endinput
