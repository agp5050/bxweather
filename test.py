#!usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

# status
r = requests.get('http://127.0.0.1:1234/api/user/status')
print 'status:\t', r.json()

# login
# false
r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='12344')))
print 'false login:\t', r.json()
# true
r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='1234')))
print 'true login:\t', r.json()
cookies = dict(webpy_session_id=r.cookies['webpy_session_id'])

# logout
r = requests.post('http://127.0.0.1:1234/api/user/logout', cookies=cookies)
print 'logout:\t', r.json()

# user_add
r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='1234')))
cookies = dict(webpy_session_id=r.cookies['webpy_session_id'])
# false
r = requests.post('http://127.0.0.1:1234/api/user/add', cookies=cookies, json=dict(
    username='', password='', privilege=dict(admin=0, push=0, adboard=0)))
print 'false user add:\t', r.json()
r = requests.post('http://127.0.0.1:1234/api/user/add', cookies=cookies, json=dict(
    username='asdf', password='', privilege=dict(admin=0, adboard=0)))
print 'false user add:\t', r.json()
r = requests.post('http://127.0.0.1:1234/api/user/add', cookies=cookies, json=dict(
    username='adsf', password='asdf', privilege='false privilege'))
print 'false user add:\t', r.json()

# true
r = requests.post('http://127.0.0.1:1234/api/user/add', cookies=cookies, json=dict(
    username='test', password='test', privilege=dict(admin=0, push=1, adboard=1)))
print 'true user add:\t', r.json()
