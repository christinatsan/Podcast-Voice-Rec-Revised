from boto3 import Session
import json
import re
import subprocess
import os

basepath = os.path.dirname(__file__)
static_folderpath = os.path.abspath(os.path.join(basepath, "..", "static"))
filepath = os.path.abspath(os.path.join(basepath, "tts.sh"))



def textToSpeech():
#def main():
  session = Session(aws_access_key_id="AKIAJPFV6CEJDXCOYH6A", aws_secret_access_key="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", region_name="us-east-2")
  client = session.client('polly')
  response = client.describe_voices(LanguageCode='en-US')

  with open(static_folderpath+'/options.json', 'r') as f:
       data = json.load(f)


  file = open(static_folderpath+'/testfile.xml', 'w')
  file.write('<?xml version="1.0"?>\n\
  <speak version="1.1" \n\
         xmlns="http://www.w3.org/2001/10/synthesis"\n\
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \n\
         xsi:schemaLocation="http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis11/synthesis.xsd"\n\
         xml:lang="en-US">\n')
  for i, value in enumerate(data):
      file.write("<break time='3s'/> No. " + str(value['count'])+ "<break time='1s'/>")
      title = value["podcasts"][0]["title"]
      title = re.sub(r' - ', r' by ', title)
      title = re.sub(r'[&]', r'and', title)
      file.write(title+"\n")
  file.write("</speak>")
  file.close()

  subprocess.call([filepath])


"""
if __name__ == '__main__':
  main()
"""

