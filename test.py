#!usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

# status
r = requests.get('http://127.0.0.1:1234/api/user/status')
print r.json()

# login
# false
r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='12344')))
print r.json()
# true
r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='1234')))
print r.json()
cookies = dict(webpy_session_id=r.cookies['webpy_session_id'])

# logout
r = requests.post('http://127.0.0.1:1234/api/user/logout', cookies=cookies)
print r.json()
