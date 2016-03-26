#!/usr/bin/python
# coding: utf-8
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import socks
import socket
import requests
import sqlite3
import sys
import getopt
import yaml
import datetime


class Crawler:
    def __init__(self, page, onion, internal):
        self.internalLinks = set()
        self.externalLinks = set()
        self.pages = set()
        self.bsObj = None
        self.html = None
        self.onion = onion
        self.internal = internal
        self.current_page = page
        self.conn = sqlite3.connect('web.db')
        if page is None:
            with open("save.log", 'r') as data:
                data = yaml.load(data)
            self.internalLinks = data["internalLinks"]
            self.externalLinks = data["externalLinks"]
            self.pages = data["pages"]

    def get_internal_links(self, includeUrl):
        scm = urlparse(includeUrl).scheme
        loc = urlparse(includeUrl).netloc
        includeUrl = scm + "://" + loc

        reurl = re.compile("^(\/|.*" + includeUrl + ")")

        for link in self.bsObj.findAll("a", href=reurl):
            url = link.attrs['href']
            if url.startswith("/"):
                the_link = includeUrl + url
            else:
                the_link = url
            if the_link not in self.pages:
                self.internalLinks.add(the_link)

    def get_external_links(self, excludeUrl):
        reurl = re.compile("^(http|www)((?!" + excludeUrl + ").)*$")
        links = self.bsObj.findAll("a", href=reurl)
        for link in links:
            url = link.attrs['href']
            if url not in self.pages:
                self.externalLinks.add(url)

    def build_bsObj(self):
        session = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:38.0)"
                                 "Gecko/20100101 Firefox/38.0",
                   "Accept": "text/html,application/xhtml+xml,application/xml;"
                             "q=0.9,image/webp,*/*;q=0.8"}
        html = session.get(self.current_page, headers=headers, timeout=30)
        self.html = html
        self.bsObj = BeautifulSoup(html.text, "html.parser")

    def get_links(self):
        self.build_bsObj()
        self.get_external_links(urlparse(self.current_page).netloc)
        self.get_internal_links(self.current_page)

    def pop_page(self):
        if len(self.externalLinks) != 0 and self.internal is not True:
            self.current_page = self.externalLinks.pop()
        elif len(self.internalLinks) != 0:
            self.current_page = self.internalLinks.pop()
        return self.current_page

    def next_page(self):
        if self.onion:
            while(".onion" not in self.pop_page()):
                pass
        else:
            self.pop_page()

        self.pages.add(self.current_page)
        return self.current_page

    def insert_data(self):
        c = self.conn.cursor()
        data = (self.current_page, self.bsObj.head.title.get_text())
        c.execute('INSERT INTO Pages(url, title) VALUES (?,?)', data)
        self.conn.commit()
        c.close()

    def update_data(self):
        c = self.conn.cursor()
        c.execute("UPDATE Pages SET title=? WHERE url=?",
                  (self.bsObj.head.title.get_text(), self.current_page))
        self.conn.commit()
        c.close()

    def get_page_id(self):
        c = self.conn.cursor()
        c.execute("SELECT id FROM Pages WHERE url=?", [self.current_page])
        pid = c.fetchone()[0]
        c.close()
        return pid

    def insert_cache(self):
        c = self.conn.cursor()
        data = (self.get_page_id(), str(self.bsObj.html))
        c.execute('INSERT INTO Caches(page_id, html) VALUES (?,?)', data)
        self.conn.commit()
        c.close()

    def save_log(self):
        data = {"externalLinks": self.externalLinks,
                "internalLinks": self.internalLinks,
                "pages": self.pages}

        with open("save.log", 'w') as yml_file:
            yml_file.write(
                yaml.dump(data,
                          allow_unicode=True,
                          default_flow_style=False))
        yml_file.close()

    def error_log(self, e):
        with open("error.log", "a") as err_file:
            err_file.write(str(e)+","+str(datetime.datetime.now())+"\n")
        err_file.close()

    def run(self):
        self.externalLinks.add(self.current_page)
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
                        self.error_log(e)
                        self.conn.close()
                        self.conn = sqlite3.connect('web.db')
                self.insert_cache()
            except KeyboardInterrupt:
                self.save_log()
                exit(1)
            except Exception as e:
                self.error_log(e)
                pass


def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'u:p:t:h')
    except getopt.GetoptError as err:
        print(str(err))
        # usage()
        sys.exit(2)

    url = None
    proxy = ["localhost", 9150]
    onion = False
    internal = False

    for o, a in opts:
        if o == "-u":
            url = a
        if o == "-p":
            if a == "tor" or a == "onion":
                # connect TOR
                socks.set_default_proxy(socks.SOCKS5, proxy[0], proxy[1])
                socket.socket = socks.socksocket

                def getaddrinfo(*args):
                    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '',
                             (args[0], args[1]))]

                socket.getaddrinfo = getaddrinfo
            if a == "onion":
                onion = True
        if o == "-t":
            if a == "i":
                internal = True

    Crawler(url, onion, internal).run()


if __name__ == "__main__":
    main()

# test crawling
# crawler = Crawler("http://skunksworkedp2cg.onion")
# crawler.run()
