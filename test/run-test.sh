#!/bin/sh

# Stop if anything goes wrong
set -e

# Executable
if [ "x$1" = "x" ]; then
	SDAPS="sdaps"
else
	SDAPS="$1"
fi

# Default project or $1
if [ "x$2" = "x" ]; then
	PROJECT="projects/test"
else
	PROJECT="$2"
fi

# Remove any old project that may exist
rm -rf "$PROJECT"

# Setup the test project, using the data in "data"
"$SDAPS" "$PROJECT" setup "data/debug.odt" "data/debug.pdf" "data/debug.internetquestions"

# Create a cover page in projects/test/cover.pdf
"$SDAPS" "$PROJECT" cover

# Create 10 unique sheets that can be printed and handed out
"$SDAPS" "$PROJECT" stamp 10

# Dumps a list of all the questionaire IDs (ie. the ids of each of the 100 sheets)
"$SDAPS" "$PROJECT" ids

# Import the scanned data. The data has to be a multipage 1bpp tif file.
"$SDAPS" "$PROJECT" add "data/debug.tif"

# Analyse the image data
"$SDAPS" "$PROJECT" recognize

# And finally, create a report with the result
"$SDAPS" "$PROJECT" report

