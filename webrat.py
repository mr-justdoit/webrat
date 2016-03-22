from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.parse import quote_plus as q
from bs4 import BeautifulSoup
import re
import datetime
import random
import socks
import socket
import requests
import time
import sys

class Crawler:
    def __init__(self, page):
        self.internalLinks = set()
        self.externalLinks = set()
        self.pages = set()
        self.current_page = page
        random.seed(datetime.datetime.now())

    def get_internal_links(self, bsObj, includeUrl):
        scm = urlparse(includeUrl).scheme
        loc = urlparse(includeUrl).netloc
        includeUrl = scm + "://" + loc

        reurl = re.compile("^(\/|.*" + includeUrl + ")")

        for link in bsObj.findAll("a", href=reurl):
            url = q(link.attrs['href'], safe="/:")
            if url is not None:
                if url.startswith("/"):
                    the_link = includeUrl + url
                else:
                    the_link = url
                if link not in self.pages:
                    self.internalLinks.add(the_link)

    def get_external_links(self, bsObj, excludeUrl):
        reurl = re.compile("^(http|www)((?!" + excludeUrl + ").)*$")

        for link in bsObj.findAll("a", href=reurl):
            url = q(link.attrs['href'], safe="/:")
            if url is not None:
                if url not in self.pages:
                    self.externalLinks.add(url)

    def get_links(self):
        # html = urlopen(self.current_page).read()
        session = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:38.0)"
                   "Gecko/20100101 Firefox/38.0",
                   "Accept": "text/html,application/xhtml+xml,application/xml;"
                   "q=0.9,image/webp,*/*;q=0.8"}
        html = session.get(self.current_page, headers=headers)
        bsObj = BeautifulSoup(html.text, "html.parser")

        links = self.get_external_links(bsObj,
                                        urlparse(self.current_page).netloc)
        if links is not None:
            for link in links:
                if link not in self.pages:
                    self.externalLinks.add(link)

        links = self.get_internal_links(bsObj, self.current_page)
        if links is not None:
            for link in links:
                if link not in self.pages:
                    self.internalLinks.add(link)

    def next_page(self):
        if len(self.externalLinks) != 0:
            self.current_page = self.externalLinks.pop()
            self.pages.add(self.current_page)
        elif len(self.internalLinks) != 0:
            self.current_page = self.internalLinks.pop()
            self.pages.add(self.current_page)
        return self.current_page

    def run(self):
        self.externalLinks.add(self.current_page)
        self.internalLinks.add(self.current_page)
        while (self.next_page() is not None):
            try:
                print(self.current_page)
                self.get_links()
            except HTTPError:
                pass
            except URLError:
                pass
            except Exception:
                pass
# connect TOR
socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
socket.socket = socks.socksocket

def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
socket.getaddrinfo = getaddrinfo

# TEST CODES 
# session = requests.Session()
# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:38.0)"
#           "Gecko/20100101 Firefox/38.0",
#           "Accept": "text/html,application/xhtml+xml,application/xml;"
#           "q=0.9,image/webp,*/*;q=0.8"}

# html = session.get("http://skunksworkedp2cg.onion:80", headers=headers)
# print(html.text)
# bsObj = BeautifulSoup(html.text, "html.parser")


# test crawler
#crawler = Crawler("http://kcg.edu")
crawler = Crawler("http://skunksworkedp2cg.onion:80")
crawler.run()

