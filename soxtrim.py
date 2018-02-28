import sox
trans = sox.Transformer()
trans.trim(0,15)
trans.build('./static/audio/Cults.mp3','out-test.mp3')

