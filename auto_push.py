#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
import time
import requests



# 返回 'yyyy-mm-dd hh:mm:ss'
# 例如 '2016-07-14 13:58:00'
# 传入 UTC 时间，返回中国标准时间
def op_utc(utc, op, s=0, m=0, h=0, d=0):
    delta = s + m * 60 + h * 60 * 60 + d * 24 * 60 * 60
    if op == 'add':
        utc += delta
    elif op == 'minus':
        utc -= delta
    return utc


def get_utc8_gm(utc=None):
    if utc is None: utc = time.time()
    utc += 8 * 60 * 60  # UTF+8
    return time.gmtime(utc)


def construct_localtime(utc=None):
    s = get_utc8_gm(utc)
    return '%4d-%02d-%02d %02d:%02d:%02d' % (
        s[0], s[1], s[2], s[3], s[4], s[5]
    )


# 转化 '2016-07-14T13:58:00.000Z'
def decode_time(time_str):
    return construct_localtime(time.mktime(
        time.strptime(time_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')) - time.timezone)


# 返回经过的秒数
def auto_push():
    db = web.database(dbn='mysql', db='test', user='', pw='', charset='utf8')
    query = db.query
    today_utc = time.time()
    today_utc8_gm = get_utc8_gm(today_utc)

    # 获取当前分钟内的 adboard
    start_utc = op_utc(today_utc, 'minus', today_utc8_gm.tm_sec)
    end_utc = op_utc(today_utc, 'add', 60 - today_utc8_gm.tm_sec)
    start = construct_localtime(start_utc)
    end = construct_localtime(end_utc)
    query = db.query("SELECT * FROM adboard WHERE starttime >= '%s' AND starttime < '%s' ORDER BY starttime DESC" % (
    start, end))
    ad_list = [q for q in query]

    # 获取 2 小时后当前分钟内的 adboard
    start_utc = op_utc(start_utc, 'add', 0, 0, 2)
    end_utc = op_utc(end_utc, 'add', 0, 0, 2)
    start = construct_localtime(start_utc)
    end = construct_localtime(end_utc)
    query = db.query("SELECT * FROM adboard WHERE starttime >= '%s' AND starttime < '%s' ORDER BY starttime DESC" % (
    start, end))
    ad_list += [q for q in query]

    r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='1234')))
    cookies = dict(webpy_session_id=r.cookies['webpy_session_id'])
    for ad in ad_list:
        r = requests.post(
            'http://127.0.0.1:1234/api/msg/push', cookies=cookies,
            json=json.dumps(dict(title=ad.title, editor=ad.editor, details=ad.starttime.strftime('%Y-%m-%d %H:%M'), url='')))
        print 'push %s: response code = %s, text = %s' % (ad.title, r, r.text)
        time.sleep(1)
    return time.time() - today_utc


if __name__ == '__main__':
    while True:
        cost_sec = auto_push()
        sleep_sec = 60 - cost_sec
        if sleep_sec <= 0:
            continue
        else:
            print 'cost sec: %.3f, sleep sec: %.3f' % (cost_sec, sleep_sec)
            time.sleep(sleep_sec)
