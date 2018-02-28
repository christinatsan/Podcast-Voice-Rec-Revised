#!/bin/bash

shopt -s nullglob
shopt -s dotglob

pwd=$PWD
parentdir="$(dirname $pwd )"

for song in $(pwd)/static/audio/*.mp3
do
    s=$(basename "$song")
    sox -V5 "$song" $(pwd)/static/audio_hold/"$s" trim 0 315 fade 0 00:05:10 5
    mv $(pwd)/static/audio_hold/"$s"  $(pwd)/static/audio/"$s"  
done

