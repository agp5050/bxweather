#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
import requests
import sys
import traceback


urls = (
    '/api/weather/(.+)', 'weather',
    '/api/user/login', 'user_login',
    '/api/user/logout', 'user_logout',
    '/api/user/status', 'user_status',
    '/api/user/add', 'user_add',
    '/api/user/modify', 'user_modify',
    '/api/user/delete', 'user_delete',
    '/api/msg/push', 'msg_push',
)

# 天气预报的 API
weather_api = {'now': 'http://127.0.0.1:8080/api/weather/now',
               'further': 'http://127.0.0.1:8080/api/weather/further'}


class weather:
    def GET(self, key):
        # print key, weather_api
        if key not in weather_api:
            raise web.notfound()
        r = requests.get(weather_api['now'])
        web.header('content-type', 'application/json')
        return r.json()


class user_login:
    def POST(self):
        # print web.input()
        # print web.data()
        web.data()
        username, password = web.input().username, web.input().password
        result = list(db.select(
            'user',
            where='username=$username AND password=$password',
            vars={'username': username, 'password': password}))
        if len(result) == 1:
            set_session(1, result[0].uid, result[0].username, result[0].privilege)
        else:
            set_session()
        web.header('content-type', 'application/json')
        return json.dumps({
            'login': session.login,
            'uid': session.uid,
            'username': session.username,
            'privilege': session.privilege})


class user_logout:
    def POST(self):
        web.header('content-type', 'application/json')
        try:
            set_session()
            session.kill()
        except Exception, e:
            return json.dumps({
                'success': 0,
                'msg': e.message})
        return json.dumps({
            'success': 1,
            'msg': ''})


class user_status:
    def GET(self):
        # print web.input(**{'id':123, 'qq':987})
        web.header('content-type', 'application/json')
        return json.dumps({
            'login': session.login,
            'uid': session.uid,
            'username': session.username,
            'privilege': session.privilege})


class user_add:
    def POST(self):
        try:

        pass

class user_modify:
    def POST(self):
        pass

class user_delete:
    def POST(self):
        pass

class msg_push:
    def POST(self):
        pass


def int_to_privilege(priv):
    priv_list = ['adboard', 'push', 'user']
    if type(priv) == int or type(priv) == long or priv < 0:
        return dict([(key, 0) for key in priv_list])
    return dict([(priv_list[-(index+1)], 1 if priv & (0x1 << index) else 0) for index in range(len(priv_list))])


def privilege_to_int(priv_dict):
    priv_list = ['adboard', 'push', 'user']
    priv_num = 0
    for index in range(len(priv_list)):
        if priv_dict.get(priv_list[-(index + 1)]) == 1:
            priv_num |= (0x1 << index)
    return priv_num


def has_privilege(key):
    # 如果不读数据库的话就可以从 session 里读
    if not session.login:
        raise Exception('请登录后再操作')
    result = list(db.select(
        'user',
        where='uid=$uid AND username=$username',
        vars={'uid': session.uid, 'username': session.username}))
    if len(result) == 1:
        if int_to_privilege(result[0].privilege).get(key) == 1:
            return True
        raise Exception('权限不足')
    else:
        raise Exception('登录错误，请重新登录或清空 cookies')


# 如果客户端传过来的是
def decode_json_post(data, params):
    result = {}
    try:
        result = json.loads(data)
    except Exception, e:
        print "Error: %s" % e.message
        traceback.print_exc()
        raise web.badrequest()
    #return dict([(key, paramsf[key]) for key in params if key not in result]
    #            + [(key, result[key]) for key in result])
    for key in params:
        if key not in result:
            result[key] = params[key]
    return result


def set_session(login=0, uid=0, username='', privilege=0):
    session.login = login
    session.uid = uid
    session.username = username
    session.privilege = privilege


class MyApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf8')
    # 关闭调试信息
    web.config.debug = False
    app = MyApplication(urls, globals())
    session = web.session.Session(
        app,
        web.session.DiskStore('sessions'),
        initializer={'login': 0, 'uid': 0, 'username': '', 'privilege': 0})
    db = web.database(dbn='mysql', db='test', user='', pw='')
    app.run(port=1234)


