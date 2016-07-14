#!usr/bin/env python
# -*- coding: utf-8 -*-

import json
import web
import requests


db = web.database(dbn='mysql', db='test', user='', pw='')
urls = {
    'user_login': 'http://127.0.0.1:1234/api/user/login',
    'user_logout': 'http://127.0.0.1:1234/api/user/logout',
    'user_status': 'http://127.0.0.1:1234/api/user/status',
    'user_add': 'http://127.0.0.1:1234/api/user/add',
    'user_modify': 'http://127.0.0.1:1234/api/user/modify',
    'user_delete': 'http://127.0.0.1:1234/api/user/delete',
    'msg_push': 'http://127.0.0.1:1234/api/msg/push'
}

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

# true if not exist
test_add = 'test_add'
r = requests.post('http://127.0.0.1:1234/api/user/add', cookies=cookies, json=dict(
    username=test_add, password=test_add, privilege=dict(admin=0, push=1, adboard=1)))
print 'true user add:\t', r.json()
query_result = db.select('user', where='username=$username', vars={'username': test_add})[0]
requests.post('http://127.0.0.1:1234/api/user/delete', cookies=cookies, json=dict(
    uid=query_result.uid, username=query_result.username))


# user_update
r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='1234')))
cookies = dict(webpy_session_id=r.cookies['webpy_session_id'])
# false
r = requests.post('http://127.0.0.1:1234/api/user/modify', json=dict(
    uid=39, username='test', password='1234', privilege=dict(admin=1, push=1, adboard=1)))
print 'false user update:\t', r.json()

r = requests.post('http://127.0.0.1:1234/api/user/modify', cookies=cookies, json=dict(
    uid=0, username='test', password='1234', privilege=dict(admin=1, push=1, adboard=1)))
print 'false user update:\t', r.json()

r = requests.post('http://127.0.0.1:1234/api/user/modify', cookies=cookies, json=dict(
    password='1234', privilege=dict(admin=1, push=1, adboard=1)))
print 'false user update:\t', r.json()

r = requests.post('http://127.0.0.1:1234/api/user/modify', cookies=cookies, json=dict(
    uid=1, username='test', password='1234', privilege=dict(admin=1, push=1, adboard=1)))
print 'false user update:\t', r.json()

# true
r = requests.post('http://127.0.0.1:1234/api/user/modify', cookies=cookies, json=dict(
    uid=39, username='test', password='5678', privilege=dict(admin=0, push=0, adboard=0)))
print 'true user update:\t', r.json()

r = requests.post('http://127.0.0.1:1234/api/user/modify', cookies=cookies, json=dict(
    uid=39, username='test', privilege=dict(admin=1, push=1, adboard=1)))
print 'true user update:\t', r.json()

r = requests.post('http://127.0.0.1:1234/api/user/modify', cookies=cookies, json=dict(
    uid=39, username='test', password='1234'))
print 'true user update:\t', r.json()


# user_delete
r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='1234')))
cookies = dict(webpy_session_id=r.cookies['webpy_session_id'])
# false
r = requests.post('http://127.0.0.1:1234/api/user/delete', json=dict(
    uid=39, username='test'))
print 'false user delete:\t', r.json()

r = requests.post('http://127.0.0.1:1234/api/user/delete', cookies=cookies, json=dict(
    uid=39))
print 'false user delete:\t', r.json()

# true
test_delete = 'test_delete'
requests.post('http://127.0.0.1:1234/api/user/add', cookies=cookies, json=dict(
    username=test_delete, password=test_delete, privilege=dict(admin=0, push=0, adboard=0)))
query_result = db.select('user', where='username=$username', vars={'username': test_delete})[0]
r = requests.post('http://127.0.0.1:1234/api/user/delete', cookies=cookies, json=dict(
    uid=query_result.uid, username=query_result.username))
print 'true user delete:\t', r.json()


# user_all
r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='1234')))
cookies = dict(webpy_session_id=r.cookies['webpy_session_id'])
# false
r = requests.get('http://127.0.0.1:1234/api/user/all')
print 'false user all:\t', r.json()

# true
r = requests.get('http://127.0.0.1:1234/api/user/all', cookies=cookies)
print 'true user all:\t', r.json()


# clothes, equip, caution
# clothes
r = requests.get('http://127.0.0.1:1234/api/usr/clothes')
print 'true clothes:\t', r.json()

# equip
r = requests.get('http://127.0.0.1:1234/api/usr/equip')
print 'true equip:\t', r.json()

# caution
r = requests.get('http://127.0.0.1:1234/api/usr/caution')
print 'true caution:\t', r.json()


# msg_push
r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='1234')))
cookies = dict(webpy_session_id=r.cookies['webpy_session_id'])
# false
r = requests.post(
    'http://127.0.0.1:1234/api/msg/push',
    json=json.dumps(dict(title='title 测试', editor='editor 测试', details='details 测试', url='')))
print 'false msg push:\t', r.json()

# true
r = requests.post(
    'http://127.0.0.1:1234/api/msg/push', cookies=cookies,
    json=json.dumps(dict(title='title 测试', editor='editor 测试', details='details 测试', url='')))
print 'true msg push:\t', r.json()


# msg_delete
r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='1234')))
cookies = dict(webpy_session_id=r.cookies['webpy_session_id'])
q = db.query('SELECT * FROM msg ORDER BY id DESC')[0]
# false
r = requests.post(
    'http://127.0.0.1:1234/api/msg/delete',
    json=json.dumps(dict(id=q.id)))
print 'false msg delete:\t', r.json()

r = requests.post(
    'http://127.0.0.1:1234/api/msg/delete', cookies=cookies,
    json=json.dumps(dict(id=-2)))
print 'false msg delete:\t', r.json()

# true
r = requests.post(
    'http://127.0.0.1:1234/api/msg/delete', cookies=cookies,
    json=json.dumps(dict(id=q.id)))
print 'true msg delete:\t', r.json()


# msg_query
r = requests.get('http://127.0.0.1:1234/api/msg/query/abcd')
print 'false msg query:\t', r

# true
r = requests.get('http://127.0.0.1:1234/api/msg/query/today')
print 'true msg query:\t', r

r = requests.get('http://127.0.0.1:1234/api/msg/query/week')
print 'true msg query:\t', r.json()

r = requests.get('http://127.0.0.1:1234/api/msg/query/all')
print 'true msg query:\t', r.json()


# adboard_add
r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='1234')))
cookies = dict(webpy_session_id=r.cookies['webpy_session_id'])
# false
r = requests.post(
    'http://127.0.0.1:1234/api/adboard/add',
    json=json.dumps(dict(title='title 测试', editor='editor 测试', details='details 测试', starttime='2016-07-14T13:58:00.000Z')))
print 'false adboard add:\t', r.json()

# true
r = requests.post(
    'http://127.0.0.1:1234/api/adboard/add', cookies=cookies,
    json=json.dumps(dict(title='title 测试', editor='editor 测试', details='details 测试', starttime='2016-07-14T13:58:00.000Z')))
print 'true adboard add:\t', r.json()

# adboard_delete
r = requests.post('http://127.0.0.1:1234/api/user/login', json=json.dumps(dict(username='admin', password='1234')))
cookies = dict(webpy_session_id=r.cookies['webpy_session_id'])
q = db.query('SELECT * FROM adboard ORDER BY id DESC')[0]
# false
r = requests.post(
    'http://127.0.0.1:1234/api/adboard/delete',
    json=json.dumps(dict(id=q.id)))
print 'false adboard delete:\t', r.json()

r = requests.post(
    'http://127.0.0.1:1234/api/adboard/delete', cookies=cookies,
    json=json.dumps(dict(id=-2)))
print 'false adboard delete:\t', r.json()

# true
r = requests.post(
    'http://127.0.0.1:1234/api/adboard/delete', cookies=cookies,
    json=json.dumps(dict(id=q.id)))
print 'true adboard delete:\t', r.json()


# adboard_query
# false
r = requests.get('http://127.0.0.1:1234/api/adboard/query/abcd')
print 'false adboard query:\t', r

# true
r = requests.get('http://127.0.0.1:1234/api/adboard/query/today')
print 'true adboard query:\t', r.json()

r = requests.get('http://127.0.0.1:1234/api/adboard/query/week')
print 'true adboard query:\t', r.json()

r = requests.get('http://127.0.0.1:1234/api/adboard/query/expired')
print 'true adboard query:\t', r.json()

r = requests.get('http://127.0.0.1:1234/api/adboard/query/future')
print 'true adboard query:\t', r.json()

r = requests.get('http://127.0.0.1:1234/api/adboard/query/all')
print 'true adboard query:\t', r.json()
