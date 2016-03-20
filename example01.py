from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
import re


def get_contents(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
    except URLError as e:
        print(e)
    else:
        pass
    return html


def build_bs(html):
    return BeautifulSoup(html.read(), "html.parser")


def get_h1(bsObj):
    try:
        title = bsObj.h1
    except AttributeError:
        return None
    return title


def print_text(bsObj, tag, attrname, attrvalue):
    datas = bsObj.findAll(tag, {attrname: attrvalue})
    for data in datas:
        print(data.text)
    return datas


def print_children(bsObj, tag, attrname, attrvalue):
    datas = bsObj.find(tag, {attrname: attrvalue})
    for child in datas.children:
        print(child)
    return datas

#TEST
html = get_contents("http://www.pythonscraping.com/pages/page1.html")
bsObj = build_bs(html)
print(get_h1(bsObj))

html = get_contents("http://www.pythonscraping.com/pages/warandpeace.html")
bsObj = build_bs(html)
print_text(bsObj, "span", "class", {"green", "red"})

html = get_contents("http://www.pythonscraping.com/pages/page3.html")
bsObj = build_bs(html)
datas = print_children(bsObj, "table", "id", "giftList")
for sibling in datas.tr.next_siblings:
    print(sibling)
