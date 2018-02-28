#!/usr/bin/python
import urllib.request
from urllib.request import Request, urlopen
import json
import re
import os
import sys
import xml.etree.ElementTree
from xml.dom import minidom
from xml.etree import ElementTree as etree
import feedparser
import json
import pprint
import textToSpeech



basepath = os.path.dirname(__file__)
static_folderpath = os.path.abspath(os.path.join(basepath, "..", "static"))
audio_hold_folderpath = os.path.abspath(os.path.join(basepath, "..", "static/audio"))
audio_folderpath = os.path.abspath(os.path.join(basepath, "..", "static/audio_hold"))
dirname = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(audio_hold_folderpath):
    os.makedirs(audio_hold_folderpath)
if not os.path.exists(audio_folderpath):
    os.makedirs(audio_folderpath)


# progress bar functions
"""
def _reporthook(numblocks, blocksize, filesize, url=None):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
    except:
        percent = 100
    if numblocks != 0:
        bar = '#' * int(percent/5) + '-' * int(20-percent/5)
        print('\r[%s] %s%s   ' % (bar, percent, '%')),
        sys.stdout.flush()
"""

#import requests
def geturl(url, dst):
    """
    if(os.path.isfile(dst)):
        if(input("A file already exists with that name. Continue? (y/n)").lower() == 'n'):
            print("Move the file and try again")
            sys.exit(0)
    """
    try:
        urllib.request.urlretrieve(url, dst.encode("ascii", "ignore"))
                       #lambda nb, bs, fs, url=url: _reporthook(nb,bs,fs,url))
    except IOError:
        print("There was an error retrieving the data. Check your internet connection and try again.")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nYou have interrupted an active download.\n Cleaning up files now.")
        os.remove(dst)
        sys.exit(1)
    

def parseFeed(url):    
    feed = feedparser.parse(url)
    with open(static_folderpath+'/optionsA.json', 'w') as outfile:
        json.dump(feed, outfile, indent=4, sort_keys=True)

    with open(static_folderpath+'/optionsA.json', 'r') as infile:
        data = json.load(infile)

        p_ids = []
        title_list = data['entries']
        for item in title_list:
            a = dict(item)
            url = a.get('link')
            title = a.get('title')
            url_split = re.split('/', url)
            elements = [re.findall('\id\d+', s) for s in url_split]
            el = [e for e in elements if len(e)][0][0]
            pod_id = re.split('id', el)[-1]
            add_id = [{'title': title, 'id':pod_id}]
            p_ids.append(add_id)
    return p_ids

def trim():
    import subprocess
    filepath = os.path.abspath(os.path.join(dirname, "sox_trim.sh"))
    subprocess.call([filepath])


def main():
#def rss_parser():
    link = 'https://rss.itunes.apple.com/api/v1/us/podcasts/top-podcasts/all/200/non-explicit.rss'
    pod_ids = parseFeed(link)
    result = []
    count = 1
    c = 0

    # grab podcast feed
    for cast in pod_ids:
        c += 1
        podcastName = cast[0]['title']
        podcastId = cast[0]['id']

        url = "https://itunes.apple.com/lookup?id=" + str(podcastId) + "&entity=podcast"
        try:
            with urllib.request.urlopen(url) as url2:
                response = url2.read().decode(url2.headers.get_content_charset())
        except IOError:
            print("There was an error retrieving the data. Check your internet connection and try again.")
            sys.exit(0)
        

        data = json.loads(response)
        rss = data["results"][0]["feedUrl"]
        #print (rss)

        # grab all podcast .mp3 files
        url_str = rss
        
        #print (xml_str)

        try:
            req = Request(url_str, headers={'User-Agent': 'Mozilla/5.0'})
            xml_str = urlopen(req).read()
            #xml_str = urllib.request.urlopen(url_str).read()
        except IOError:
            print("There was an error retrieving the data. Check your internet connection and try again.")
        
        try:
            xmldoc = minidom.parseString(xml_str)
        except xml.parsers.expat.ExpatError:
            print ("Invalid string")
            print ('{}: {}'.format(c, url_str))


        values = xmldoc.getElementsByTagName('enclosure')
        titles = xmldoc.getElementsByTagName('title')

        # append the title list such that the correct title is corresponding to the
        # equivlanet .mp3 link

        nameChecker = True
        counter = 1

        while nameChecker:
            if podcastName == titles[counter].firstChild.nodeValue:
                counter = counter + 1
            else:
                nameChecker = False

        titles = titles[counter:]

        # insert mp3 list into mp3list array
        mp3list = []
        for val in values:
            mp3list.append(val.attributes['url'].value)

        saveLoc = os.path.join(audio_hold_folderpath, titles[0].firstChild.nodeValue + ".mp3")

        #os.path.join(SITE_ROOT, "static", "options.json")
        pod_dict={}
        pod_dict['count'] = count
        stitle =  titles[0].firstChild.nodeValue.encode('ascii','ignore').decode('unicode_escape')
        #pod_dict['podcasts'] = [{'title': podcastName, 'file-name': titles[0].firstChild.nodeValue + ".mp3"}]
        pod_dict['podcasts'] = [{'title': podcastName, 'file-name': stitle + ".mp3"}]
        count += 1

        result.append(pod_dict)
        geturl(mp3list[0], saveLoc)

    with open(static_folderpath+'/options.json', 'w') as outfile:
        json.dump(result, outfile, indent=4, sort_keys=True)

    trim()


if __name__ == '__main__':
    try:
        main()
        textToSpeech.textToSpeech()
    except KeyboardInterrupt:
        print('\n')
        sys.exit(0)


