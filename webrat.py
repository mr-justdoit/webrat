from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.parse import quote_plus as q
from bs4 import BeautifulSoup
import re
import datetime
import random

internalLinks = set()
externalLinks = set()
pages = set()
random.seed(datetime.datetime.now())


def get_internal_links(bsObj, includeUrl):
    scm = urlparse(includeUrl).scheme
    loc = urlparse(includeUrl).netloc
    includeUrl = scm + "://" + loc
    global internalLinks

    reurl = re.compile("^(\/|.*" + includeUrl + ")")

    for link in bsObj.findAll("a", href=reurl):
        url = q(link.attrs['href'], safe="/:")
        if url is not None:
            if url.startswith("/"):
                the_link = includeUrl + url
            else:
                the_link = url
            if the_link not in pages:
                internalLinks.add(the_link)


def get_external_links(bsObj, excludeUrl):
    global externalLinks
    reurl = re.compile("^(http|www)((?!" + excludeUrl + ").)*$")

    for link in bsObj.findAll("a", href=reurl):
        url = q(link.attrs['href'], safe="/:")
        if url is not None:
            if url not in pages:
                externalLinks.add(url)


def get_links(startingPage):
    html = urlopen(startingPage)
    bsObj = BeautifulSoup(html, "html.parser")
    global externalLinks
    global internalLinks

    links = get_external_links(bsObj, urlparse(startingPage).netloc)
    if links is not None:
        for link in links:
            if link not in pages:
                externalLinks.add(link)

    links = get_internal_links(bsObj, startingPage)
    if links is not None:
        for link in links:
            if link not in pages:
                internalLinks.add(link)


def next_page():
    if len(externalLinks) != 0:
        page = externalLinks.pop()
        pages.add(page)
    elif len(internalLinks) != 0:
        page = internalLinks.pop()
        pages.add(page)

    return page


page = "http://kcg.edu"
externalLinks.add(page)
internalLinks.add(page)

while (len(externalLinks) != 0 and len(internalLinks) != 0):
    try:
        get_links(page)
        print(page)
    except HTTPError:
        pass
    except URLError:
        pass

    page = next_page()
