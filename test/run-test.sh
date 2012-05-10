#!/bin/sh

# Stop if anything goes wrong
set -e

# Executable
if [ "x$1" = "x" ]; then
	SDAPS="sdaps"
else
	SDAPS="$1"
fi

PROJECT="projects/test-odt"

# Create projects dir if it does not exist
if [ ! -e `dirname $PROJECT` ]; then
	mkdir -p `dirname $PROJECT`
fi

# Remove project dir that may exist
rm -rf "$PROJECT"

# Setup the test project, using the data in "data"
# By disabling the surveyid and enable the questionnaire id we test more
# unsual code paths, and we don't have a problem because the survey id
# changed ...
"$SDAPS" "$PROJECT" setup --print-questionnaire-id --no-print-survey-id "data/odt/debug.odt" "data/odt/debug.pdf" "data/odt/debug.internetquestions"

# Create a cover page in projects/test/cover.pdf
"$SDAPS" "$PROJECT" cover

# Create 10 unique sheets that can be printed and handed out
"$SDAPS" "$PROJECT" stamp 10

# Dumps a list of all the questionaire IDs (ie. the ids of each of the 10 sheets)
"$SDAPS" "$PROJECT" ids

# Import the scanned data. The data has to be a multipage 1bpp tif file.
"$SDAPS" "$PROJECT" add "data/odt/debug.tif"

# Analyse the image data
"$SDAPS" "$PROJECT" recognize

# And finally, create a report with the result
"$SDAPS" "$PROJECT" report

###########################################################
# Test Tex with IDs
###########################################################

PROJECT="projects/test-tex-ids"

# Create projects dir if it does not exist
if [ ! -e `dirname $PROJECT` ]; then
	mkdir -p `dirname $PROJECT`
fi

# Remove project dir that may exist
rm -rf "$PROJECT"

"$SDAPS" "$PROJECT" setup_tex "data/tex/questionnaire_with_ids.tex"

# Create a cover page in projects/test/cover.pdf
"$SDAPS" "$PROJECT" cover

# Create 10 unique sheets that can be printed and handed out
"$SDAPS" "$PROJECT" stamp 10

# And finally, create a report with the result
"$SDAPS" "$PROJECT" report_tex

###########################################################
# Test Tex without IDs
###########################################################

PROJECT="projects/test-tex-no-ids"

# Create projects dir if it does not exist
if [ ! -e `dirname $PROJECT` ]; then
	mkdir -p `dirname $PROJECT`
fi

# Remove project dir that may exist
rm -rf "$PROJECT"

"$SDAPS" "$PROJECT" setup_tex "data/tex/questionnaire_without_ids.tex"

# Create a cover page in projects/test/cover.pdf
"$SDAPS" "$PROJECT" cover

# Run stamp, not neccessary
"$SDAPS" "$PROJECT" stamp

# And finally, create a report with the result
"$SDAPS" "$PROJECT" report_tex
