from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import datetime
import random

internalLinks = []
externalLinks = []
pages = []
random.seed(datetime.datetime.now())


def get_internal_links(bsObj, includeUrl):
    scm = urlparse(includeUrl).scheme
    loc = urlparse(includeUrl).netloc
    includeUrl = scm + "://" + loc
    global internalLinks

    reurl = re.compile("^(\/|.*" + includeUrl + ")")

    for link in bsObj.findAll("a", href=reurl):
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in internalLinks:
                if link.attrs['href'].startswith("/"):
                    internalLinks.append(includeUrl+link.attrs['href'])
                else:
                    internalLinks.append(link.attrs['href'])

def get_external_links(bsObj, excludeUrl):
    global externalLinks
    reurl = re.compile("^(http|www)((?!"+excludeUrl+").)*$")
    
    for link in bsObj.findAll("a", href=reurl):
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in externalLinks:
                externalLinks.append(link.attrs['href'])

    

def get_links(startingPage):
    html = urlopen(startingPage)
    bsObj = BeautifulSoup(html, "html.parser")
    global externalLinks
    global internalLinks

    
    links = get_external_links(bsObj, urlparse(startingPage).netloc)
    if links is not None:
        for link in links:
            if link not in externalLinks and link not in pages:
                externalLinks.append(link)

    links = get_internal_links(bsObj, startingPage)
    if links is not None:        
        for link in links:
            if link not in externalLinks and link not in pages:
                internalLinks.append(link)

def next_page():
    if len(externalLinks) != 0:
        page = externalLinks.pop()
        pages.append(page)
    elif len(internalLinks) != 0:
        page = internalLinks.pop()
        pages.append(page)
        
    return page

page = "http://oreilly.com"
externalLinks.append(page)
internalLinks.append(page)

while(len(externalLinks) != 0 and len(internalLinks) != 0):
    try:
        get_links(page)
        print(page)
    except HTTPError:
        pass
    except URLError:
        pass
    
    page = next_page()

