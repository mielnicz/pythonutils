#!/bin/sh
#----------------------------------------------------------------------------
# 15-Feb-2013 ShaneG
#
# This script uses the 'polaroid.py' and 'corkbord.py' scripts to generate
# a corkboard from a list of images (and attributes) specified in a file.
#----------------------------------------------------------------------------

# Get the directory containing the scripts (and resources)
SCRIPT_DIR=`dirname $0`

# Make sure we have a list file specified on the command line
if [ "X$1" == "X" ]; then
  cat <<!
Usage:

  $0 listing-file

Where:

  listing-file is the file containing a list of filenames, alignments and
               captions for the files to process.
!
  exit 1
fi

# Process the list of files (create polaroids and then a corkboard)
awk -F, '{ printf("${SCRIPT_DIR}/polaroid.py %s %s %s \"%s\"\n", $2, $1, $3, $4) }' <$1 >/tmp/options.$$
source /tmp/options.$$ >/tmp/outputs.$$
${SCRIPT_DIR}/corkboard.py `awk '{ printf(" %s", $1) }' < /tmp/outputs.$$`



