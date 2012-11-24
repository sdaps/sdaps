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
"$SDAPS" "$PROJECT" setup --style=classic --print-questionnaire-id --no-print-survey-id "data/odt/debug.odt" "data/odt/debug.pdf" "data/odt/debug.internetquestions"

# Create a cover page in projects/test/cover.pdf
"$SDAPS" "$PROJECT" cover

# Create 10 unique sheets that can be printed and handed out
"$SDAPS" "$PROJECT" stamp --random 10

# Dumps a list of all the questionaire IDs (ie. the ids of each of the 10 sheets)
#"$SDAPS" "$PROJECT" ids

# Import the scanned data. The data has to be a multipage 1bpp tif file.
"$SDAPS" "$PROJECT" add "data/odt/debug.tif"

# Analyse the image data
"$SDAPS" "$PROJECT" recognize

# Export to CSV
"$SDAPS" "$PROJECT" csv export

# And finally, create a report with the result
"$SDAPS" "$PROJECT" report

###########################################################
# LibreOffice 3.5 PDF export
###########################################################

PROJECT="projects/test-odt-lo35"

# Remove project dir that may exist
rm -rf "$PROJECT"

# Setup the test project, using the data in "data"
# By disabling the surveyid and enable the questionnaire id we test more
# unsual code paths, and we don't have a problem because the survey id
# changed ...
# Also test code128 style for ODT support
"$SDAPS" "$PROJECT" setup --style="code128" --global-id="SDAPS!" --print-questionnaire-id "data/odt-3/debug.odt" "data/odt-3/debug.pdf" "data/odt-3/debug.internetquestions"
"$SDAPS" "$PROJECT" stamp --file "data/odt-3/questionnaire_ids"
"$SDAPS" "$PROJECT" ids -o "$PROJECT/ids"
diff "data/odt-3/questionnaire_ids" "$PROJECT/ids"


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
"$SDAPS" "$PROJECT" stamp --random 10

# Add dummy tiff
"$SDAPS" "$PROJECT" add "data/tex/test_with_ids.tif"

# Recognize the empty image (ie. the barcodes)
"$SDAPS" "$PROJECT" recognize

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

# Dump some infos
"$SDAPS" "$PROJECT" info
"$SDAPS" "$PROJECT" info title
"$SDAPS" "$PROJECT" info --set title "asdf"

# And finally, create a report with the result
"$SDAPS" "$PROJECT" report_tex

