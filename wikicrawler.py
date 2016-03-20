#!/usr/bin/python
# coding:utf-8
from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys
import getopt
import re
import random
import datetime

pages = set()


def get_links(urltxt):
    global pages
    url = "http://en.wikipedia.org" + urltxt
    html = urlopen(url)
    bsObj = BeautifulSoup(html, "html.parser")
    try:
        print(bsObj.h1.get_text())
        print(bsObj.find(id="mw-content-text").findAll("p")[0])
        print(bsObj.find(id="ca-edit").find("span").find("a").attrs['href'])
    except AttributeError:
        print("wrong")

    for link in bsObj.findAll("a", href=re.compile("^(/wiki/)")):
        if 'href' in link.attrs:
            if link.attrs['href'] not in pages:
                newPage = link.attrs['href']
                print("----------\n" + newPage)
                pages.add(newPage)
                get_links(newPage)


def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'u:h')
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    random.seed(datetime.datetime.now())

    for o, a in opts:
        if o == "-u":
            get_links(a)


if __name__ == "__main__":
    main()
