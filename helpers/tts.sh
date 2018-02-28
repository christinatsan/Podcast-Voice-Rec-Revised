#!/bin/bash
#pwd=$PWD
#parentdir="$(dirname $pwd )"
echo $parentdir/static
aws polly synthesize-speech \
--text-type ssml \
--text file://$(pwd)/static/testfile.xml \
--output-format mp3 \
--voice-id Joanna \
$(pwd)/static/options.mp3