import io
from bs4 import BeautifulSoup
import requests
import re
import sys
import os

def getHrefFromTtl(ttl): 
    return ttl.find(href=True)['href']

if len(sys.argv) < 3:
    print "Usage: python gdscraper.py <date> <destinationPath>"
    print "<date> in format yyyy-MM-dd"
    exit()


#todo: validate
#todo: D&C based on date
date = sys.argv[1]
#todo: create dir if doesn't exist
outputPath = sys.argv[2] + os.path.sep

if os.path.exists(outputPath):
    if os.path.isfile(outputPath):
        print("Can't write to %s because it's an existing file" % outputPath)
        exit()
else:
    os.makedirs(outputPath)


domain = 'https://archive.org'
queryPrefix = '/details/GratefulDead?and%5B%5D=date%3A'
querySuffix = '%2A&sort=-downloads'

queryUrl = domain + queryPrefix + date + querySuffix

r = requests.get(queryUrl)

soup = BeautifulSoup(requests.get(queryUrl).text, 'html.parser')

itemTtlTags = soup.find_all(class_ = ' item-ttl C C2 ')

hrefs = map(getHrefFromTtl, itemTtlTags)
if (len(hrefs) < 1):
    print("No download links found!")

collectionUrl = domain + str(hrefs[0])

collectionSoup = BeautifulSoup(requests.get(collectionUrl).text, 'html.parser')

m3uRef = collectionSoup.find(href=re.compile("m3u"))['href']
m3u = requests.get(domain + m3uRef)
for mp3Url in m3u.text.split('\n'):
    if len(mp3Url) is 0:
        continue
    fileName = mp3Url.split('/')[-1]
    outFile = outputPath + fileName 
    print("Downloading and writing " + outFile)
    mp3 = requests.get(mp3Url)
    with io.open(outFile, 'wb') as f:
        f.write(mp3.content)

