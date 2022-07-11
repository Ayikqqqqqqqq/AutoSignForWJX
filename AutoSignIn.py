#! usr/bin/python
# -*- coding: utf-8 -*-

import os
import requests
import json

headers = os.environ['qlist_header']
url = os.environ['qlist_url']

if __name__ == '__main__':
    #r = requests.get(url)
    print(url)
    headers = json.dumps(headers)
    print(headers['Sec-Fetch-Site'])
