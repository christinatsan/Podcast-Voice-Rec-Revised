import os
import subprocess

basepath = os.path.dirname(__file__)
audio_hold_folderpath = os.path.abspath(os.path.join(basepath, "..", "static/audio_hold"))
audio_folderpath = os.path.abspath(os.path.join(basepath, "..", "static/audio"))
dirname = os.path.dirname(os.path.realpath(__file__))


if not os.path.exists(audio_hold_folderpath):
    os.makedirs(audio_hold_folderpath)
if not os.path.exists(audio_folderpath):
    os.makedirs(audio_folderpath)


filepath = os.path.abspath(os.path.join(dirname, "sox_trim.sh"))
subprocess.call([filepath])