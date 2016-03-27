from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import requests
import sqlite3
import yaml
import datetime


class Crawler:
    def __init__(self, page, onion, internal):
        self.internalLinks = set()
        self.externalLinks = set()
        self.pages = set()
        self.bsObj = None
        self.onion = onion
        self.internal = internal
        self.current_page = page
        self.conn = sqlite3.connect('web.db')
        if page is None:
            self.load_data()

    def load_data(self):
        with open("save.yml", 'r') as data:
            data = yaml.load(data)
        self.current_page = data["current_page"]
        self.internalLinks = data["internalLinks"]
        self.externalLinks = data["externalLinks"]
        self.pages = data["pages"]
        self.onion = self.onion if self.onion else data["onion"]
        self.internal = self.internal if self.internal else data["internal"]

    def get_internal_links(self, includeUrl):
        includeUrl = urlparse(includeUrl).scheme + "://" + urlparse(
            includeUrl).netloc

        reurl = re.compile("^(\/|.*" + includeUrl + ")")

        for link in self.bsObj.findAll("a", href=reurl):
            if link.attrs['href'].startswith("/"):
                the_link = includeUrl + link.attrs['href']
            else:
                the_link = link.attrs['href']

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
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:38.0) "
                                 "Gecko/20100101 Firefox/38.0",
                   "Accept": "text/html,application/xhtml+xml,application/xml;"
                             "q=0.9,image/webp,*/*;q=0.8"}
        html = session.get(self.current_page, headers=headers, timeout=30)
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
        else:
            self.current_page = None
        return self.current_page

    def next_page(self):
        if self.onion:
            while (".onion" not in self.pop_page()):
                pass
        else:
            self.pop_page()

        if self.current_page is not None:
            self.pages.add(self.current_page)

        return self.current_page

    def send_query_to_db(self, query, data):
        c = self.conn.cursor()
        c.execute(query, data)
        self.conn.commit()
        c.close()

    def insert_data(self):
        query = 'INSERT INTO Pages(url, title) VALUES (?,?)'
        data = (self.current_page, self.bsObj.head.title.get_text())
        self.send_query_to_db(query, data)

    def update_data(self):
        query = 'UPDATE Pages SET title=? WHERE url=?'
        data = (self.bsObj.head.title.get_text(), self.current_page)
        self.send_query_to_db(query, data)

    def get_page_id(self):
        c = self.conn.cursor()
        c.execute("SELECT id FROM Pages WHERE url=?", [self.current_page])
        pid = c.fetchone()[0]
        c.close()
        return pid

    def insert_cache(self):
        query = 'INSERT INTO Caches(page_id, html) VALUES (?,?)'
        data = (self.get_page_id(), str(self.bsObj.html))
        self.send_query_to_db(query, data)

    def save_log(self):
        data = {"current_page": self.current_page,
                "externalLinks": self.externalLinks,
                "internalLinks": self.internalLinks,
                "pages": self.pages,
                "onion": self.onion,
                "internal": self.internal}

        with open("save.yml", 'w') as yml_file:
            yml_file.write(yaml.dump(data,
                                     allow_unicode=True,
                                     default_flow_style=False))
        yml_file.close()

    def error_log(self, e):
        with open("error.log", "a") as err_file:
            err_file.write(str(e) + "," + self.current_page + "," + str(
                datetime.datetime.now()) + "\n")
        err_file.close()

    def run(self):
        self.get_links()
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
            finally:
                pass
