import io
from bs4 import BeautifulSoup
import requests
import re
import sys
import os
import datetime
from tqdm import tqdm

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

# with io.open('coll.html', 'w') as f:
#     f.write(collectionSoup.prettify())

#todo: handle case where there's only direct download, no streaming
#also try direct download first to reduce bandwidth

print("Searching for flac files")
flacZipRef = collectionSoup.find_all("a", href=re.compile("formats=FLAC"))
# print(flacZipRef)
# Download zipped .flac if possible
if len(flacZipRef) > 0 :
    flacZipUrl = flacZipRef[0]['href']
    print("found " + flacZipUrl)
    outFile = outputPath + flacZipUrl.split('/')[-1]
    print("Downloading and writing " + outFile)

    flacZip = requests.get(domain + flacZipUrl, stream=True)
    total_size = int(flacZip.headers.get('content-length', 0))
    block_size = 1024 * 32
    #pbar = tqdm(total_size, unit='B', unit_scale=True, unit_divisor=1000000)
    pbar = tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024)
    with io.open(outFile, 'wb') as f:
        # f.write(flacZip.content)
        for data in flacZip.iter_content(block_size):
            f.write(data)
            pbar.update(len(data))
    pbar.close()
    if total_size != 0 and wrote != total_size:
        print("ERROR, something went wrong")  

# Otherwise get list of mp3s as m3u
else:
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

#todo handle google play oddity with temp directory
