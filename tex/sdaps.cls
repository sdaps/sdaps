%% start of file `sdaps.cls'.
%% Copyright 2010-2013 Ferdinand Schwenk (ferdisdot@gmail.com).
%% Copyright 2011-2013 Benjamin Berg (benjamin@sipsolutions.net).
%% Copyright 2010 Tobias Simon <tobsimon@googlemail.com>
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
\ProvidesClass{sdaps}[2013/03/10%
                      v1.0 Class for composing questionairs for SDAPS]

% Load scrbase for keyval support
\RequirePackage{scrkbase}
\RequirePackage{xargs}

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
\newif\if@style@qr\@style@qrfalse
\def\@sdaps@style{code128}%

\newif\if@checkmode@checkcorrect\@checkmode@checkcorrecttrue
\newif\if@checkmode@check\@checkmode@checkfalse
\newif\if@checkmode@fill\@checkmode@fillfalse
\def\@sdaps@checkmode{checkcorrect}%


\DefineFamily{SDAPS}
\DefineFamilyMember{SDAPS}
\DefineFamilyKey{SDAPS}{style}[code128]%
{%
  \KOMA@set@ncmdkey{style}{@tempa}{%
    {classic}{0},%
    {code128}{1},%
    {custom}{2},%
    {qr}{3}%
  }{#1}%
  \ifcase \@tempa\relax
    \@style@classictrue%
    \@style@codecxxviiifalse%
    \@style@qrfalse%
    \def\@sdaps@style{classic}%
  \or
    \@style@classicfalse%
    \@style@codecxxviiitrue%
    \@style@qrfalse%
    \def\@sdaps@style{code128}%
  \or
    \@style@classicfalse%
    \@style@codecxxviiifalse%
    \@style@qrfalse%
    \def\@sdaps@style{custom}%
  \or
    \@style@classicfalse%
    \@style@codecxxviiifalse%
    \@style@qrtrue%
    \def\@sdaps@style{qr}%
  \fi
}

\DefineFamilyKey{SDAPS}{checkmode}[checkcorrect]%
{%
  \KOMA@set@ncmdkey{checkmode}{@tempa}{%
    {checkcorrect}{0},%
    {check}{1},%
    {fill}{2}%
  }{#1}%
  \ifcase \@tempa\relax
    \def\@sdaps@checkmode{checkcorrect}%
    \@checkmode@checkcorrecttrue%
    \@checkmode@checkfalse%
    \@checkmode@fillfalse%
  \or
    \def\@sdaps@checkmode{check}%
    \@checkmode@checkcorrectfalse%
    \@checkmode@checktrue%
    \@checkmode@fillfalse%
  \or
    \def\@sdaps@checkmode{fill}%
    \@checkmode@checkcorrectfalse%
    \@checkmode@checkfalse%
    \@checkmode@filltrue%
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

% headers and footers
\usepackage{scrpage2}
\clearscrheadings
  \chead[\@author\\\@title]{\@author\\\@title}
  \cfoot{\sdapspagemark}
\pagestyle{scrheadings}

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

% graphics
\RequirePackage{graphicx}

% Section formatting
\RequirePackage{sectsty}

% table of fixed width
\RequirePackage{tabularx}
% display content vertical centered
\renewcommand\tabularxcolumn[1]{m{#1}}
\newcolumntype{Y}{>{\raggedleft}X}

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

% The pgfgetlastxy macro was only added on 2010-04-09
% By copying its definition here we can support older PGF versions
\ifx\pgfgetlastxy\undefined
  % The definition from newer pgf versions.
  \def\pgfgetlastxy#1#2{%
          \edef#1{\the\pgf@x}%
          \edef#2{\the\pgf@y}%
  }%
\fi

% QR Code implementation
\RequirePackage{qrcode}

% Code 128 implementation in plain TeX
\input{code128}

% http://www.tex.ac.uk/cgi-bin/texfaq2html?label=isitanum
\def\IsPositive#1{%
  TT\fi
  \ifcat_\ifnum0<0#1 _\else A\fi
}

\def\@sdaps@STAMP{%
  \begingroup
    \begin{scope}[line width=\elementlinewidth, shift={(current page.south west)}]%
      \if@style@qr
        \if@PrintQuestionnaireId
          \begin{scope}[shift={($(\edgeleftmargin, \edgebottommargin)$)}]%
            \node(barcode)[anchor=south west,outer sep=0,inner sep=0]{\qrcode[version=2,level=H,padding,height=10mm]{\qid}};%
          \end{scope}
        \fi

        % We unconditionally print this barcode, it is required for the recognition
        % process.
        \begin{scope}[shift={($(\paperwidth, 0) + (-\edgerightmargin, \edgebottommargin)$)}]%
          \pgfmathsetbasenumberlength{4}%
          \pgfmathdectobase{\paddedpage}{\thepage}{10}% Yes, padding to 4 chars the hard way
          \edef\barcodechars{\surveyid\paddedpage}%
          \node(barcode)[anchor=south east,outer sep=0,inner sep=0]{\qrcode[version=2,level=H,padding,height=10mm]{\barcodechars}};%
        \end{scope}

        \ifstr{\globalid}{}{}{
          \begin{scope}[shift={($(\paperwidth/2-\edgerightmargin/2+\edgeleftmargin/2, \edgebottommargin)$)}]%
            \node(barcode)[anchor=south,outer sep=0,inner sep=0]{\qrcode[version=2,level=H,padding,height=10mm]{\globalid}};%
          \end{scope}
        }
      \fi

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

% This needs to be called once for each page!
\def\sdapspagemark{%
  \normalfont%
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
          \if@sdaps@lastpage%
            \ifnum \thepage=1
              % if we have a one page document, just always stamp the last
              % page. This means that SDAPS can fall back to simplex mode
              % automatically.
              \@sdaps@STAMP
            \fi
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
  \hypersetup{%
    pdfauthor     = \@author,%
    pdftitle      = \@title,%
    pdfsubject    = sdaps questionnaire \@title,%
    pdfkeywords   = sdaps questionnaire \@title%
  }%
  %
  \if@PrintQuestionnaireId
    \immediate\write\sdapsoutfile{PrintQuestionnaireId=1}
  \else
    \immediate\write\sdapsoutfile{PrintQuestionnaireId=0}
  \fi
  \if@PrintSurveyId
    \immediate\write\sdapsoutfile{PrintSurveyId=1}
  \else
    \immediate\write\sdapsoutfile{PrintSurveyId=0}
  \fi
  \immediate\write\sdapsoutfile{Pages=\getpagerefnumber{LastPage}}
  \pgfpoint{\paperwidth}{\paperheight}
  \pgfgetlastxy{\@sdaps@width}{\@sdaps@height}
  \immediate\write\sdapsoutfile{PageSize=\@sdaps@width, \@sdaps@height}
  \if@twoside
    \immediate\write\sdapsoutfile{Duplex=True}
  \else
    \immediate\write\sdapsoutfile{Duplex=False}
  \fi
  \immediate\write\sdapsoutfile{Style=\@sdaps@style}%
  \immediate\write\sdapsoutfile{CheckMode=\@sdaps@checkmode}%
  \immediate\write\sdapsoutfile{GlobalID=\globalid}%
  \immediate\write\sdapsoutfile{GlobalIDLabel=\globalidlabel}%
  %
  \foreach \qid in \questionnaireids{%
    \@sdaps@lastpagefalse
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
        \if@checkmode@checkcorrect
          \begin{tabularx}{\textwidth}{llcX}
              \translate{info-cross}: & \checkedbox &\quad & \translate{info-select} \\
              \translate{info-correct}: & \correctedbox & & \translate{info-mark} \\
          \end{tabularx}
        \else
          \PackageError{sdaps}{Sorry, there is no help text for the checkmode you have choosen right now! Please pass the noinfo optional argument to the questionnaire environment!}\@ehb %
        \fi
      \end{info}
    }

    \BODY

    % Force a stamp on the next last page of the questionnaire
    \@sdaps@lastpagetrue

    \clearpage

    \immediate\write\sdapsoutfile{}
    % Just close the file here so nothing is written anymore ...
    \immediate\closeout\sdapsoutfile%
    % Do not generate position information from now on
    \global\@sdaps@outputfalse%
    % Reset counters for testing purposes
    \setcounter{checkboxnum}{0}%
    \setcounter{textboxnum}{0}%
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
\setlength{\parskip}{1.0ex \@plus 1.5ex \@minus -0.25ex}
%\setlength{\parskip}{0pt}
\setlength\columnsep{10\p@}
\setlength\columnseprule{0\p@}
% Redefine the spacings for \subsection ie. \questions.
\renewcommand\section{\@startsection {section}{1}{\z@}%
      {-\parskip}%
      {\parskip}%
      {\normalfont\Large\bfseries\SS@sectfont}}
\renewcommand\subsection{
  \@startsection{subsection}{2}{\z@}%
      {0.5\parskip}%
      {0.25\parskip}% These are deleted again for questions
      {}%
}
\pagestyle{scrheadings}
\pagenumbering{arabic}
\raggedbottom
%\flushbottom
\onecolumn

\newif\if@sdaps@lastpage\@sdaps@lastpagefalse

% Most of these lengths are hardcoded in the defs.py too. So
% any modification here will need a corresponding change in
% defs.py.
% If you want to make this more configurable, patches are always welcome :-)
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
\newlength{\checkboxsize}
\setlength{\checkboxsize}{3.5mm}
\newlength{\boxpaddings}
\setlength{\boxpaddings}{3mm}
% Subtract outline width
\addtolength{\checkboxsize}{-\elementlinewidth}

% This padding is applied at the bottom of textboxes (similar to a strut)
% as they do not have a sane baseline.
\newlength{\textboxbottompad}
\setlength{\textboxbottompad}{0.5ex \@plus 1ex \@minus 0.2ex}

% How to draw the checkbox, either "box" or "ellipse" (though ellipse is a circle,
% because we don't support non-square sizes here for now).
\def\checkboxstyle{box}

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

% Variables for markquestions with arbitrary range
\newcounter{markcheckboxcount}
\setcounter{markcheckboxcount}{5}
\newif\if@sdaps@markenvactive\@sdaps@markenvactivefalse

\definecolor{sectionbgcolor}{gray}{0.8}
\definecolor{sectionfgcolor}{gray}{0.0}

% Execute sdaps.opt file to allow SDAPS to override any options
\InputIfFileExists{sdaps.opt}{}{}

% Old helper macro, do not use anymore!
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

\newif\if@sdaps@output\@sdaps@outputtrue

%-------------------------------------------------------------------------------
%                style commands definitions
%-------------------------------------------------------------------------------
\providecommand{\addinfo}[2]{%
  \immediate\write\sdapsoutfile{\unexpanded{#1}=\unexpanded{#2}}%
}

\providecommand{\checkbox}{\@ifstar
    \checkboxStar%
    \checkboxNoStar%
}

\providecommand{\@sdaps@drawbox}{
  \ifstr{\checkboxstyle}{box}{
    \draw[line width=\elementlinewidth,fill=white] (0.5\elementlinewidth, 0) rectangle +(\checkboxsize, \checkboxsize);%
  }{}
  \ifstr{\checkboxstyle}{ellipse}{
    \draw[line width=\elementlinewidth,fill=white] ($(0.5\elementlinewidth, 0) + (0.5\checkboxsize, 0.5\checkboxsize)$) circle (0.5\checkboxsize);%
  }{}
}

\providecommand{\@sdaps@drawfilledbox}{
  \ifstr{\checkboxstyle}{box}{
    \draw[fill,line width=\elementlinewidth] (0.5\elementlinewidth, 0) rectangle +(\checkboxsize, \checkboxsize);%
  }{}
  \ifstr{\checkboxstyle}{ellipse}{
    \draw[fill,line width=\elementlinewidth] ($(0.5\elementlinewidth, 0) + (0.5\checkboxsize, 0.5\checkboxsize)$) circle (0.5\checkboxsize);%
  }{}
}

\providecommand{\@sdaps@drawcheck}{
  \begin{scope}[overlay,decoration={random steps,segment length=4pt,amplitude=1pt}]
    \draw[line width=\elementlinewidth, decorate] ($(0, 0) - (2pt,2pt)$) -- (0.5\checkboxsize, 0.5\checkboxsize) -- ($(\checkboxsize, \checkboxsize) + (2pt,2pt)$);%
    \draw[line width=\elementlinewidth, decorate] ($(0, \checkboxsize) + (-2pt,2pt)$) -- (0.5\checkboxsize, 0.5\checkboxsize) -- ($(\checkboxsize, 0) + (2pt,-2pt)$);%
  \end{scope}
}


\providecommand{\checkboxNoStar}{%
  \mbox{%
  \def\@sdaps@tmp{}%
  \if@sdaps@output%
    \label{checkbox\thecheckboxnum}%
    \def\@sdaps@tmp{remember picture}%
  \fi%
  \tikz[baseline={max(0ex, 0.5\checkboxsize-1ex+0.5\elementlinewidth)},\@sdaps@tmp]{%
    \@sdaps@drawbox%
    %
    \if@sdaps@output%
      \pgfsys@getposition{pgfpageorigin}{\@sdaps@pageorigin}%
      \pgfsys@getposition{\pgfpictureid}{\@sdaps@checkboxpos}%
      \pgfpointadd{\@sdaps@checkboxpos}{%
        \pgfpointadd{\@sdaps@pageorigin}{\pgfpoint{0}{-max(0ex, 0.5\checkboxsize-1ex+0.5\elementlinewidth) + \checkboxsize + 0.5\elementlinewidth}}%
      }%
      \pgfgetlastxy{\@sdaps@x}{\@sdaps@y}%
      \pgfpoint{\checkboxsize+\elementlinewidth}{\checkboxsize+\elementlinewidth}%
      \pgfgetlastxy{\@sdaps@width}{\@sdaps@height}%
      \immediate\write\sdapsoutfile{Box=Checkbox, \getpagerefnumber{checkbox\thecheckboxnum}, \@sdaps@x, \@sdaps@y, \@sdaps@height, \@sdaps@width, \checkboxstyle}%
    \fi%
  }%
  \addtocounter{checkboxnum}{1}}%
  \ignorespaces
}
\providecommand{\checkboxStar}{%
  \tikz[baseline={max(0ex, 0.5\checkboxsize-1ex+0.5\elementlinewidth)}]{%
    \@sdaps@drawbox
  }%
  \ignorespaces
}
\providecommand{\checkedbox}{%
  \tikz[baseline={max(0ex, 0.5\checkboxsize-1ex+0.5\elementlinewidth)}]{%
    \@sdaps@drawbox
    \@sdaps@drawcheck
  }%
  \ignorespaces
}
\providecommand{\filledbox}{%
  \tikz[baseline={max(0ex, 0.5\checkboxsize-1ex+0.5\elementlinewidth)}]{%
    \@sdaps@drawfilledbox
  }%
  \ignorespaces
}
\providecommand{\correctedbox}{%
  \tikz[baseline={max(0ex, 0.5\checkboxsize-1ex+0.5\elementlinewidth)}]{%
    \@sdaps@drawfilledbox
    \@sdaps@drawcheck
  }%
  \ignorespaces
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
\renewcommand{\author}[1]{\def\@author{#1}\immediate\write\sdapsoutfile{Author=\unexpanded{#1}}}
\renewcommand{\title}[1]{\def\@title{#1}\immediate\write\sdapsoutfile{Title=\unexpanded{#1}}}

\def\question#1{%
\ifx&#1&%
  % #1 is empty
  \refstepcounter{subsection}%
 \else%
  % #1 is nonempty
  \subsection{\usekomafont{questionfont}\strut#1\strut}%
  % This is extra spacing after the subsection is removed. By doing this we
  % get exactly one \parskip
  \nobreak%
  \vspace{-0.25\parskip}%
  \nobreak%
\fi%
}

% http://mrunix.de/forums/showthread.php?t=59943
\newenvironment{info}{%
  \vspace{\baselineskip}\vspace{\lineskip}\vspace{-1.0em}%
  \hrule height 1pt%
  \vspace{\lineskip}%
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
\newdimen\@tempdimfillwidth%
\providecommand{\sdaps@textbox}[3]{%
  % Both baselineskip and lineskip?
  \question{#3}%
  \if@sdaps@output%
    \immediate\write\sdapsoutfile{QObject-Text=\arabic{section}.\arabic{subsection}. \unexpanded{#3}} %
    \label{textbox\thetextboxnum}%
    \pgfsys@getposition{pgfpageorigin}{\@sdaps@pageorigin}%
    \pgfsys@getposition{textboxtop\thetextboxnum}{\@sdaps@textboxtoppos}%
    \pgfpointadd{\@sdaps@textboxtoppos}{%
      \pgfpointadd{\@sdaps@pageorigin}{\pgfpoint{0}{0}}%
    }%
    \pgfgetlastxy{\@sdaps@x}{\@sdaps@y}%
%
    \pgfsys@getposition{textboxbottom\thetextboxnum}{\@sdaps@textboxbottompos}%
    \pgfpointadd{\@sdaps@textboxtoppos}{%
      \pgfpointadd{\pgfpointscale{-1}{\@sdaps@textboxbottompos}}{%
        % Assume width is equal to \linewidth
        \pgfpoint{\linewidth}{0}%
      }%
    }%
    \pgfgetlastxy{\@sdaps@width}{\@sdaps@height}%
    \immediate\write\sdapsoutfile{Box=Textbox, \getpagerefnumber{textbox\thetextboxnum}, \@sdaps@x, \@sdaps@y, \@sdaps@width, \@sdaps@height}%
  \fi%
  \nobreak%
  \vspace{\parskip}%
  \nobreak%
  \begingroup %
    \setlength\@tempdima{#2}%
    \setlength\@tempdimb{\lineskip}%
    \setlength\@tempdimfillwidth{\linewidth}%
    \advance\@tempdimfillwidth by -2\elementlinewidth
    \offinterlineskip
    \def\sides{%
      \hbox{\raise -\@tempdima \hbox to\linewidth{%
        \vrule depth 0pt height \@tempdima width \elementlinewidth%
        {\color{white}\vrule depth 0pt height \@tempdima width \@tempdimfillwidth}%
        \vrule depth 0pt height \@tempdima width \elementlinewidth%
      }}%
    }%
    \if@sdaps@output%
      \pgfsys@markposition{textboxtop\thetextboxnum}%
    \fi%
    \hrule width \linewidth height \elementlinewidth depth 0pt%
    \nobreak%
    \sides%
    \nobreak%
    \kern-0.5\@tempdima%
    \nobreak%
    #1%
    \nobreak%
    \kern-0.5\@tempdima%
    \nobreak\sides\nobreak%
    % Undo the skip following \leavevmode
    \vspace{-\parskip}\nobreak%
    \vspace{-\@tempdimb}\nobreak%
    \vspace{-\@tempdima}\nobreak%
    % Not entirely sure why this is needed ... but with it the lines join
    % exactly.
    \vspace{\elementlinewidth}\nobreak%
    % This needs some explanation: ie. why do we do a leavevmode, and then
    % raisebox, etc.
    % The idea is that the baseline for the last vbox much higher than the
    % lower line of the textbox. By doing this the minimum baseline
    % distance is not taken into account for the next line after the textbox.
    % The result is that the spacing after a freeform text field, and the
    % spacing after a choicegroup with a choiceitemtext is the same.
    % Seems insane? Maybe it is :-)
    % And maybe there are better ways of doing this ...
    \leavevmode\nobreak%
    \hbox{\raise -\@tempdima \hbox to \linewidth {%
      % Mark at the bottom left (right underneath the top mark)
      \if@sdaps@output%
        \pgfsys@markposition{textboxbottom\thetextboxnum}%
      \fi%
      \cleaders\hrule height \elementlinewidth depth 0pt \hfill%
      % And add the bottom padding
      \vrule depth \textboxbottompad height 0pt width 0pt%
      }%
    }%
    \addtocounter{textboxnum}{1}%
  \endgroup%
}

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
  \immediate\write\sdapsoutfile{}
  \immediate\write\sdapsoutfile{QObject-Head=\arabic{section}. \unexpanded{#1}}
}


\newenvironmentx{choicegroup}[2][2={X*{\thechoicegroupnumchoices}{c}}]{%
  \question{#1}%
  \immediate\write\sdapsoutfile{QObject-Head=\arabic{section}.\arabic{subsection}. \unexpanded{#1}} %
  \setcounter{choicegroupnumchoices}{0} %
  \global\def\@sdaps@choicegroup@start{\tabularx{\linewidth}{#2}}%
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
    % Move to the next line (as it is not part of the @start macro)
    \\ %
    \setcounter{choicegroupnumchoices}{-1} %
  \fi %
  \immediate\write\sdapsoutfile{QObject-Choice=XAUTO. \unexpanded{#1}}%
  {\usekomafont{choicegrouplinefont}\strut#1\strut} \@sdaps@choicegroup@boxes \\ %
}

\providecommand*{\groupaddchoice}[1]{%
  \ifnum\thechoicegroupnumchoices<0
    % Throw error \@ehb == you have lost some text
    % Why is this emitted multiple times? And can one create a multiline message?
    \PackageError{sdaps}{Tried to add a new choice, but not at the beginning of a choicegroup environment!}\@ehb
  \else
    \stepcounter{choicegroupnumchoices}%
    \g@addto@macro{\@sdaps@choicegroup@start}{& {\usekomafont{choicegroupchoicefont}\strut#1}}%
    \g@addto@macro{\@sdaps@choicegroup@boxes}{& \immediate\write\sdapsoutfile{Answer-Choice=\unexpanded{#1}} \checkbox}%
  \fi
}


\providecommand*{\setmarkrange}[1]{%
  \if@sdaps@markenvactive%
    \ClassError{sdaps}{Changed markrange inside a markgroup!}{The markrange can not be changed inside an active markgroup.}%
  \else%
    \setcounter{markcheckboxcount}{#1}%
  \fi%
}

\def\@sdaps@generatemarkboxes{%
  \@tempcnta=0%
  \def\@sdaps@markboxes{}%
  \whiledo{\@tempcnta<\value{markcheckboxcount}}%
  {%
    \advance\@tempcnta by 1%
    \g@addto@macro\@sdaps@markboxes{& {\checkbox}}%
  }%
}

\newenvironment{markgroup}[1]{%
  \question{#1}%
  \immediate\write\sdapsoutfile{QObject-Head=\arabic{section}.\arabic{subsection}. \unexpanded{#1}}%
  \@sdaps@markenvactivetrue%
  \@sdaps@generatemarkboxes%
  \tabularx{\linewidth}{Xr*{\themarkcheckboxcount}{c}l}
}{%
  \endtabularx%
  \@sdaps@markenvactivefalse%
}

\providecommand*{\markline}[3]{%
  \immediate\write\sdapsoutfile{QObject-Mark=XAUTO. \unexpanded{#1}}%
  \immediate\write\sdapsoutfile{Answer-Mark=\unexpanded{#2}}%
  {\usekomafont{marklinequestionfont}\strut#1\strut} & {\usekomafont{marklinechoicefont}#2} \@sdaps@markboxes & {\usekomafont{marklinechoicefont}#3}%
  \immediate\write\sdapsoutfile{Answer-Mark=\unexpanded{#3}}%
  \\%
}

\providecommand*{\singlemark}[3]{%
  \question{#1}%
  \immediate\write\sdapsoutfile{QObject-Mark=\arabic{section}.\arabic{subsection}. \unexpanded{#1}}%
  \immediate\write\sdapsoutfile{Answer-Mark=\unexpanded{#2}}%
  \@sdaps@generatemarkboxes%
  \begin{tabularx}{\linewidth}{Y*{\themarkcheckboxcount}{c}X}
    {\usekomafont{singlemarkchoicefont}\strut#2} \@sdaps@markboxes & {\usekomafont{singlemarkchoicefont}#3}\\%
  \end{tabularx}%
  \immediate\write\sdapsoutfile{Answer-Mark=\unexpanded{#3}}%
}


\newcounter{choiceitems}
\newcounter{maxchoiceitems}
\newenvironment{choicequestion}[2][3]{%
  \setcounter{choiceitems}{1}%
  \setcounter{maxchoiceitems}{#1}%
  \question{#2}%
  \immediate\write\sdapsoutfile{QObject-Choice=\arabic{section}.\arabic{subsection}. \unexpanded{#2}}%
  \global\def\@sdaps@choiceitems@dummy{}%
  \loop{}%
  \ifnum\thechoiceitems<\themaxchoiceitems{\addtocounter{choiceitems}{1}} \global\edef\@sdaps@choiceitems@dummy{\@sdaps@choiceitems@dummy &}%
  \repeat%
  \setcounter{choiceitems}{1}%
  \tabularx{\linewidth}{*{\themaxchoiceitems}{X}}%
  % We insert dummy elements into each cell, because otherwise there may be
  % layouting issues.
  \@sdaps@choiceitems@dummy%
   \rule[-1em]{0pt}{3em}% Insert known space (1em below, 2em above the baseline)
   \cr%
  \noalign{\vspace{-\extrarowheight}\vspace{-3.0em}}% Subtract known space again.
}{%
  \endtabularx%
}

\providecommand*{\choiceitem}[1]{%
  \immediate\write\sdapsoutfile{Answer-Choice=\unexpanded{#1}}%
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
    \immediate\write\sdapsoutfile{Answer-Choice=\unexpanded{#2}}%
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
      \advance\@tempdimboxlower by -\textboxbottompad%
      %
      \setlength\@tempdima{1cm}%
      \@tempdimruleheight=\@tempdimheight%
      \advance\@tempdimruleheight by +2.0\elementlinewidth%
      \advance\@tempdimruleheight by \@tempdimlower%
      %
      \immediate\write\sdapsoutfile{Answer-Choice=\unexpanded{#3}}%
      %
      \if@sdaps@output%
        \label{textbox\thetextboxnum}%
        \pgfsys@getposition{pgfpageorigin}{\@sdaps@pageorigin}%
        \pgfsys@getposition{textboxleft\thetextboxnum}{\@sdaps@textboxleftpos}%
        \pgfpointadd{\@sdaps@textboxleftpos}{%
          \pgfpointadd{\@sdaps@pageorigin}{\pgfpoint{0}{\@tempdimruleheight}}%
        }%
        \pgfgetlastxy{\@sdaps@x}{\@sdaps@y}%
        %
        \pgfsys@getposition{textboxright\thetextboxnum}{\@sdaps@textboxrightpos}%
        \pgfpointadd{\@sdaps@textboxrightpos}{%
          \pgfpointadd{\pgfpointscale{-1}{\@sdaps@textboxleftpos}}{%
            \pgfpoint{0}{#1+2\elementlinewidth}%
          }%
        }%
        \pgfgetlastxy{\@sdaps@width}{\@sdaps@height}%
        \immediate\write\sdapsoutfile{Box=Textbox, \getpagerefnumber{textbox\thetextboxnum}, \@sdaps@x, \@sdaps@y, \@sdaps@width, \@sdaps@height}%
      \fi%
      {
      }% Yes, this inserts whitespace, because well, we had a bug and we don't
      %
      \def\horizontallines{%
        \hbox{%
          \raise\@tempdimboxlower\vbox{%
            \hrule width \@tempdima height \elementlinewidth %
            {\color{white}\hrule width \@tempdima height \@tempdimheight}%
            \hrule height \elementlinewidth%
            \vspace{\textboxbottompad}%
          }%
        }%
      }%
      \if@sdaps@output%
        \pgfsys@markposition{textboxleft\thetextboxnum}%
      \fi%
      \vrule depth -\@tempdimlower width \elementlinewidth height \@tempdimruleheight %
      %\kern -\elementlinewidth%
      \horizontallines%
      \kern-0.5\@tempdima%
      \cleaders\horizontallines\hfill%
      \kern-0.5\@tempdima%
      \horizontallines%
      %\kern -\elementlinewidth%
      \vrule depth -\@tempdimlower width \elementlinewidth height \@tempdimruleheight%
      \if@sdaps@output%
        \pgfsys@markposition{textboxright\thetextboxnum}%
      \fi%
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
