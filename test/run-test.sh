#! /bin/sh

# Stop if anything goes wrong.
set -e

# Remove any old test_project that may exist
rm -rf ./test_project

# Setup the test_project, using the data in "data"
sdaps ./test_project setup data/debug.odt data/debug.pdf data/debug.internetquestions

# Create a cover page in ./test_project/cover.pdf
sdaps ./test_project cover

# Create 10 unique sheets that can be printed and handed out
sdaps ./test_project stamp 10

# Dumps a list of all the questionaire IDs (ie. the ideas of each of the 100 sheets)
sdaps ./test_project ids

# Import the scanned data. The data has to be a multipage 1bpp tif file.
sdaps ./test_project add data/debug.tif

# Analyse the image data
sdaps ./test_project recognize

# And finally, create a report with the result
sdaps ./test_project report

