#! usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import random
import re
import time
from urllib.parse import urlencode, quote

import execjs
import requests
import datetime
from lxml import etree

qlist_submit_data = os.environ['qlist_submit_data']
qlist_header = os.environ['qlist_header']
qlist_url = os.environ['qlist_url']


class App:
    def __init__(self):
        self.session = requests.session()
        submit_data = qlist_submit_data

        link = self.get_list()
        url_data = self.get_page(link)
        state = self.set_sign(url_data, submit_data)
        print(state)

    def get_list(self):
        url = qlist_url
        headers = json.loads(qlist_header)
        r = self.session.get(url, headers=headers).text
        # print(r)
        tree = etree.HTML(r)
        links = tree.xpath('//div[@id="ulQs"]/dl/a/@href')
        names = tree.xpath('//div[@id="ulQs"]/dl/a/span[@class="title"]/text()')
        survey = {}
        i = 0
        for link in links:
            survey[names[i]] = link
            i += 1

        link = survey.get(get_link_name())
        if link is None:
            raise Exception('没有找到当天的健康问卷')

        print('正在获取', get_link_name())
        link = link.replace("/vm", "/vj")
        return link

    def get_page(self, link: str):
        url = 'https://wjbitzh.wjx.cn' + link
        # print(url)
        r = self.session.get(url).text
        # print(r)

        wx_user_id = re.search(r'(&wxuserid=)(?P<id>\d*)', link).group('id')
        short_id = re.search(r'(j/)(?P<id>.*?)(\.)', link).group('id')
        jq_nonce = re.search(r'.{8}-.{4}-.{4}-.{4}-.{12}', r).group()
        rn = re.search(r'\d{9,10}\.\d{8}', r).group()
        activity_id = re.search(r'(var activityId =)(?P<id>\d*)(;)', r).group('id')
        start_time = re.search(r'(var starttime =")(?P<sid>.*?)(";)', r).group('sid')
        k_times = 4
        time_stamp = '{}{}'.format(int(time.time()), random.randint(100, 200))

        jq_pram = get_param(rn, start_time, decode_id(activity_id))
        jq_sign = data_enc(jq_nonce, k_times)

        url_data = {
            'shortid': short_id,  # activtyId = 173686210
            'starttime': start_time,
            'vpsiu': '1',
            'source': 'directphone',
            'submittype': '1',
            'ktimes': k_times,
            'hlv': '1',
            'rn': rn,
            'wxUserId': wx_user_id,
            'jqpram': jq_pram,
            'iwx': '1',
            't': time_stamp,
            'jqnonce': jq_nonce,
            'jqsign': jq_sign,
        }
        return url_data

    def set_sign(self, url_data, submit_data):
        content = 'submitdata=' + quote(submit_data)
        url = "https://ww.wjx.top/joinnew/processjq.ashx?" + urlencode(url_data)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        print(url_data)
        r = self.session.post(url, headers=headers, data=content)
        state = False
        if r.status_code == 200:
            print(r.text)
            state = True
        else:
            raise Exception('签到未响应')
        return state


def decode_id(did):
    res = int(did) ^ 2130030173
    return str(res)


def get_link_name():
    t = datetime.datetime.now()
    s = '学生动态调查表{}.{}.{}'.format(t.year, t.month, t.day)
    return s


def data_enc(n, k):
    c = k % 10
    if 0 == c:
        c = 1
    s = ''
    for i in n:
        s += chr(ord(i) ^ c)
    return s


def js_from_file(file_name: str):
    """
    读取js文件
    :return:
    """
    with open(file_name, 'r', encoding='UTF-8') as file:
        result = file.read()

    return result


def get_param(rn: str, t: str, aid: str):
    context1 = execjs.compile(js_from_file('./lib/get_jqparam.js'))
    result1 = context1.call("get_jqParam", rn, t, aid)
    result1 = sort_jqparam(result1)
    return result1


def sort_jqparam(jqpram):
    # 计算jqParam的ASCII数值
    asc_value = 0
    for i in jqpram:
        asc_value += ord(i)

    # ASCII数值 取模 jqParam长度，决定从哪一位开始调换顺序
    start_location = asc_value % len(jqpram)

    # 调换顺序
    e = ''
    for j in range(len(jqpram)):
        c = start_location + j
        if c >= len(jqpram):
            c -= len(jqpram)
        e += jqpram[c]
    return e


if __name__ == '__main__':
    App()
    # get_link_name()
