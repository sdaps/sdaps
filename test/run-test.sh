#!/bin/sh

# Stop if anything goes wrong
set -e

# Executable
if [ "x$1" = "x" ]; then
	SDAPS="sdaps"
else
	SDAPS="$1"
fi

# Set VERBOSE so that LaTeX compilation results end up on the console
export VERBOSE=1

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

"$SDAPS" setup tex "$PROJECT" "data/tex/questionnaire_with_ids.tex"

# Create a cover page in projects/test/cover.pdf
"$SDAPS" cover "$PROJECT"

# Create sheets with some given IDs
"$SDAPS" stamp "$PROJECT" -f "data/tex/code128_test_ids"
"$SDAPS" ids "$PROJECT" -o "$PROJECT/ids"
diff "data/tex/code128_test_ids" "$PROJECT/ids"



# Add original PDF and convert
"$SDAPS" add "$PROJECT" --convert "$PROJECT/stamped_1.pdf"

# Recognize the empty pages (ie. the barcodes)
"$SDAPS" recognize "$PROJECT"

# Import some data
"$SDAPS" import csv "$PROJECT" data/tex/ids_test_import.csv
# Export data again
"$SDAPS" export csv "$PROJECT"
# And compare with expected result
diff -qup data/tex/ids_test_export.csv "$PROJECT/data_1.csv"

# Export all the other extra data
"$SDAPS" export csv "$PROJECT" --images --question-images --quality

# And finally, create a report with the fake result, both with tex and reportlab
"$SDAPS" report reportlab "$PROJECT"
"$SDAPS" report tex "$PROJECT"

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

"$SDAPS" setup tex "$PROJECT" "data/tex/questionnaire_without_ids.tex"

# Create a cover page in projects/test/cover.pdf
"$SDAPS" cover "$PROJECT"

# Run stamp, not neccessary
"$SDAPS" stamp "$PROJECT"

# Dump some infos
"$SDAPS" info "$PROJECT"
"$SDAPS" info "$PROJECT" title
"$SDAPS" info "$PROJECT" title "asdf"

# Add and recognize test data
#"$SDAPS" add "$PROJECT" "data/tex/test_without_ids.tif"
#"$SDAPS" recognize "$PROJECT"


# And finally, create a report with the result
#"$SDAPS" report_tex "$PROJECT"


###########################################################
# Compare info files
###########################################################

# Distributions:
# Run with
# IGNORE_PATTERN_EXTEND='\|^survey_id'
# exported in the environment to prevent situations where texlive changes
# cause build failures.

for i in projects/*; do
  success=0
  error=0
  name=`basename "$i"`
  for j in "data/info_files/$name" data/info_files/$name.*; do
    if [ ! -f "$j" ]; then
      continue;
    fi;
    # This ignores the title; for whatever reason the \LaTeX
    # is written out differently with newer latex versions.
    diff -I '^title'"$IGNORE_PATTERN_EXTEND" "$j" "$i/info" && success=1 || error=1
  done

  if [ $success -eq 0 -a $error -ne 0 ]; then
    # Throw error
    echo "None of the info files match for $name!"
    exit 1;
  fi
done

