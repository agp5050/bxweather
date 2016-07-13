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
    '/api/usr/clothes','clothes',
    '/api/usr/equip', 'equip',
    '/api/usr/caution', 'caution',
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

class clothes:
    def GET(self, key):
        if key not in weather_api:
            raise web.notfound()
        r = requests.get(weather_api['now'])
        r_5 = request.get(weather_api['further'])
        if r.temp < 10:
            clothes_1 = "穿衣指数：厚"
        else:
            if r.temp < 20:
                clothes_1 = "穿衣指数：中"
            else:
                clothes_1 = "穿衣指数：薄"
        if r.temp_max - r.temp_min >= 5:
            clothes_2 = "夜间温差较大，注意睡眠！"
        else:
            clothes_2 = ""
        if (abs(r_5[1].temp - r_5[0].temp) > 5) or (abs(r_5[2].temp - r_5[0].temp) > 5):
            clothes_3 = "近日温差较大，注意穿衣保暖！"
        else:
            clothes_3 = ""
        web.header('content-type', 'application/json')
        return json.dumps({
            'clothes_1': clothes_1,
            'clothes_2': clothes_2,
            'clothes_3': clothes_3})

class equip:
    def GET(self,key):
        if key not in weather_api:
            raise web.notfound()
        r = requests.get(weather_api['now'])
        main = r.weather.description
        equip_1 = ""
        equip_2 = ""
        if r.weather.main == "clear":
            equip_1 = "天气晴朗，注意防晒！"
        else:
            if r.weather.main == "clouds":
                equip_1 = "有降雨概率，请备好伞具！"
            else:
                equip_1 = "今日有雨，备好伞具！"
                equip_2 = "雨天路滑，注意骑行！"

        return json.dumps({
            'equip_1': equip_1,
            'equip_2': equip_2
            })

class caution:
    def GET(self,key):
        if key not in weather_api:
            raise web.notfound()
        r = requests.get(weather_api['now'])
        caution_1 = ""
        caution_2 = ""
        if r.main.humidity < 45:
            caution_1 = "天干气躁，小心上火，多喝水！"
        if r.main.huminity > 65 and r.main.temp > 30:
            caution_1 = "高温高湿，注意防暑降温，警惕心血管疾病的发生！"
        if r.wind.speed > 10.8 and r.wind.speed < 20:
            caution_2 = "风力较大，出行注意安全！"
        if r.wind.speed > 20:
            caution_2 = "台风天气，谨慎出行！"
        if r.wind.speed < 10.8 and t.main.temp > 10 and t.main.temp < 26 and  (r.weather.main == "clear" or r.weather.main == "Clouds" or r.weather.main == "Clear"):
            caution_3 = "天气状况良好，适合出行玩乐～"
        else:
            caution_3 = "今日适宜写代码／睡觉"



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


