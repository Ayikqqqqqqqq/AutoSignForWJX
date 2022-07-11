#! usr/bin/python
# -*- coding: utf-8 -*-

import os
import requests

headers = os.environ['qlist_header']
url = os.environ['qlist_url']

if __name__ == '__main__':
    #r = requests.get(url)
    print(url)
    print(headers['Sec-Fetch-Site'])
