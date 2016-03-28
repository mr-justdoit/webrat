#!/usr/bin/python
# coding: utf-8
import socks
import socket
import sys
import getopt
import os
from crawler import Crawler


def connect_tor():
    # connect TOR
    socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
    socket.socket = socks.socksocket

    def getaddrinfo(*args):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '',
                 (args[0], args[1]))]

    socket.getaddrinfo = getaddrinfo


def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'u:p:t:h')
    except getopt.GetoptError as err:
        print(str(err))
        # usage()
        sys.exit(2)

    url = None
    onion = False
    internal = False

    for o, a in opts:
        if o == "-u":
            url = a
        if o == "-p":
            if a == "tor" or a == "onion":
                connect_tor()
            if a == "onion":
                onion = True
        if o == "-t":
            if a == "i":
                internal = True

    Crawler(url, onion, internal).run()


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webrat.settings")
    main()

# test crawling
# crawler = Crawler("http://skunksworkedp2cg.onion")
# crawler.run()
