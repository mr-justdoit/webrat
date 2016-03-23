#!/usr/bin/python
# coding: utf-8
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
import sqlite3
import sys
import getopt


class Crawler:
    def __init__(self, page):
        self.internalLinks = set()
        self.externalLinks = set()
        self.pages = set()
        self.bsObj = None
        self.current_page = page
        self.conn = sqlite3.connect('web.db')
        random.seed(datetime.datetime.now())

    def get_internal_links(self, includeUrl):
        scm = urlparse(includeUrl).scheme
        loc = urlparse(includeUrl).netloc
        includeUrl = scm + "://" + loc

        reurl = re.compile("^(\/|.*" + includeUrl + ")")

        for link in self.bsObj.findAll("a", href=reurl):
            url = q(link.attrs['href'], safe="/:")
            if url.startswith("/"):
                the_link = includeUrl + url
            else:
                the_link = url
            if the_link not in self.pages:
                self.internalLinks.add(the_link)

    def get_external_links(self, excludeUrl):
        reurl = re.compile("^(http|www)((?!" + excludeUrl + ").)*$")

        for link in self.bsObj.findAll("a", href=reurl):
            url = q(link.attrs['href'], safe="/:")
            if url not in self.pages:
                self.externalLinks.add(url)

    def build_bsObj(self):
        session = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:38.0)"
                                 "Gecko/20100101 Firefox/38.0",
                   "Accept": "text/html,application/xhtml+xml,application/xml;"
                             "q=0.9,image/webp,*/*;q=0.8"}
        html = session.get(self.current_page, headers=headers, timeout=30)
        self.bsObj = BeautifulSoup(html.text, "html.parser")

    def get_links(self):
        self.build_bsObj()
        self.get_external_links(urlparse(self.current_page).netloc)
        self.get_internal_links(self.current_page)

    def next_page(self):
        if len(self.externalLinks) != 0:
            self.current_page = self.externalLinks.pop()
            self.pages.add(self.current_page)
        elif len(self.internalLinks) != 0:
            self.current_page = self.internalLinks.pop()
            self.pages.add(self.current_page)
        return self.current_page

    def insert_data(self):
        c = self.conn.cursor()
        data = (self.current_page, self.bsObj.head.title.get_text(),
                str(self.bsObj.body))
        c.execute('INSERT INTO web(url, title, body) VALUES (?,?,?)', data)
        self.conn.commit()
        c.close()

    def update_data(self):
        c = self.conn.cursor()
        c.execute("UPDATE web SET title=?,body=? WHERE url=?",
                  (self.bsObj.head.title.get_text(), str(self.bsObj.body),
                   self.current_page))
        self.conn.commit()
        c.close()

    def run(self):
        self.externalLinks.add(self.current_page)
        self.internalLinks.add(self.current_page)
        while (self.next_page() is not None):
            try:
                print(self.current_page)
                self.get_links()
                try:
                    self.insert_data()
                except Exception as e:
                    if 'UNIQUE' in str(e):
                        self.update_data()
                    else:
                        self.conn = sqlite3.connect('web.db')
                        print(e)
            except HTTPError:
                pass
            except URLError:
                pass
            except Exception as e:
                print(e)
                pass


def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'u:p:h')
    except getopt.GetoptError as err:
        print(str(err))
        # usage()
        sys.exit(2)

    url = "http://www.google.com"
    proxy = ["localhost", 9150]
    global socket

    for o, a in opts:
        if o == "-u":
            url = a
        if o == "-p":
            if a == "tor":
                # connect TOR
                socks.set_default_proxy(socks.SOCKS5, proxy[0], proxy[1])
                socket.socket = socks.socksocket
                
                def getaddrinfo(*args):
                    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '',
                             (args[0], args[1]))]

                socket.getaddrinfo = getaddrinfo

    Crawler(url).run()


if __name__ == "__main__":
    main()

# test crawling
# crawler = Crawler("http://skunksworkedp2cg.onion")
# crawler.run()
