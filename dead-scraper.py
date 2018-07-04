import io
from bs4 import BeautifulSoup
import requests
import re
import sys
import os
import datetime

def getHrefFromTtl(ttl): 
    return ttl.find(href=True)['href']

if len(sys.argv) < 3:
    print "Usage: python gdscraper.py <date> <destinationPath>"
    print "<date> in format yyyy-MM-dd"
    exit()


#todo: validate
#todo: D&C based on date
date = sys.argv[1]


outputPath = sys.argv[2] + os.path.sep

if os.path.exists(outputPath):
    if os.path.isfile(outputPath):
        print("Can't write to %s because it's an existing file" % outputPath)
        exit()
else:
    os.makedirs(outputPath)


domain = 'https://archive.org'
queryPrefix1 = '/details/'
queryPrefix2 = '?and[]=date%3A'
querySuffix = '*&sort=-downloads'

#todo allow passing in of band
band = 'GratefulDead'
parsedDate = datetime.datetime.strptime(date, '%Y-%m-%d')
if parsedDate > datetime.datetime.strptime('2015-01-01', '%Y-%m-%d'):
    band = 'DeadAndCompany'

queryUrl = domain + queryPrefix1 + band + queryPrefix2 + date + querySuffix
print(queryUrl)

soup = BeautifulSoup(requests.get(queryUrl).text, 'html.parser')

itemTtlTags = soup.find_all(class_ = ' item-ttl C C2 ')

hrefs = map(getHrefFromTtl, itemTtlTags)
if (len(hrefs) < 1):
    print("No download links found!")
    exit()

collectionUrl = domain + str(hrefs[0])

collectionSoup = BeautifulSoup(requests.get(collectionUrl).text, 'html.parser')

#todo: handle case where there's only direct download, no streaming
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

