#!/usr/local/bin/python
# -*- coding: utf-8 -*-


import time
import BaseHTTPServer
import re
import requests
from bs4 import BeautifulSoup, element

HOST_NAME = '127.0.0.1'
PORT_NUMBER = 8000
URL = 'https://habrahabr.ru'
TAGS_IGNORE = ('script', 'style', 'pre', 'code', 'iframe')
WORDS_SIX_CHARS = re.compile(r'(\b\w{6}\b)', flags=(re.UNICODE))
HABR_LINKS_RE = re.compile(r'^https?://habrahabr\.ru')


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        """Respond to a GET request."""

        r = requests.get(URL + self.path)
        self.send_response(r.status_code)
        self.send_header("Content-type", r.headers.get('content-type'))
        self.end_headers()

        if r.headers.get('content-type') == 'text/html; charset=UTF-8':

            soup = BeautifulSoup(r.text, 'html.parser')

            for tag in soup.find_all('a', href=HABR_LINKS_RE):
                tag.attrs['href'] = HABR_LINKS_RE.sub(u'', tag.attrs['href'])

            for node in soup.find_all(text=True):
                if node.string.strip() and not isinstance(node, element.PreformattedString) \
                        and node.parent.name not in TAGS_IGNORE:
                    node.string.replace_with(WORDS_SIX_CHARS.sub(u'\\1™', node.string))

            self.wfile.write(soup.encode(formatter=None))
        else:
            self.wfile.write(r.content)


if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
