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

"$SDAPS" "$PROJECT" setup "data/tex/questionnaire_with_ids.tex"

# Create a cover page in projects/test/cover.pdf
"$SDAPS" "$PROJECT" cover

# Create sheets with some given IDs
"$SDAPS" "$PROJECT" stamp -f "data/tex/code128_test_ids"
"$SDAPS" "$PROJECT" ids -o "$PROJECT/ids"
diff "data/tex/code128_test_ids" "$PROJECT/ids"



# Add original PDF and convert
"$SDAPS" "$PROJECT" add --convert "$PROJECT/stamped_1.pdf"

# Recognize the empty pages (ie. the barcodes)
"$SDAPS" "$PROJECT" recognize

# Import some data
"$SDAPS" "$PROJECT" csv import data/tex/ids_test_import.csv
# Export data again
"$SDAPS" "$PROJECT" csv export
# And compare with expected result
diff -qup data/tex/ids_test_export.csv "$PROJECT/data_1.csv"

# Export all the other extra data
"$SDAPS" "$PROJECT" csv export --images --question-images --quality

# And finally, create a report with the fake result, both with tex and reportlab
"$SDAPS" "$PROJECT" report
"$SDAPS" "$PROJECT" report_tex

###########################################################
# Test Tex with IDs (classic mode)
###########################################################

PROJECT="projects/test-tex-classic"

# Create projects dir if it does not exist
if [ ! -e `dirname $PROJECT` ]; then
	mkdir -p `dirname $PROJECT`
fi

# Remove project dir that may exist
rm -rf "$PROJECT"

"$SDAPS" "$PROJECT" setup "data/tex/questionnaire_classic.tex"

# Create 10 unique sheets that can be printed and handed out
"$SDAPS" "$PROJECT" stamp --random 10

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

"$SDAPS" "$PROJECT" setup "data/tex/questionnaire_without_ids.tex"

# Create a cover page in projects/test/cover.pdf
"$SDAPS" "$PROJECT" cover

# Run stamp, not neccessary
"$SDAPS" "$PROJECT" stamp

# Dump some infos
"$SDAPS" "$PROJECT" info
"$SDAPS" "$PROJECT" info title
"$SDAPS" "$PROJECT" info --set title "asdf"

# Add and recognize test data
#"$SDAPS" "$PROJECT" add "data/tex/test_without_ids.tif"
#"$SDAPS" "$PROJECT" recognize


# And finally, create a report with the result
#"$SDAPS" "$PROJECT" report_tex


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

