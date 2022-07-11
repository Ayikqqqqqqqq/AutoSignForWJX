#! usr/bin/python
# -*- coding: utf-8 -*-

import os
import requests

headers = os.environ['qlist_header']

if __name__ == '__main__':
    r = requests.get('https://www.baidu.com')
    print(r.text)
