#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
import time
import requests
import base64
import sys
import traceback


urls = (
    '/api/weather/(.+)', 'weather',
    '/api/usr/clothes', 'clothes',
    '/api/usr/equip', 'equip',
    '/api/usr/caution', 'caution',
    '/api/user/login', 'user_login',
    '/api/user/logout', 'user_logout',
    '/api/user/status', 'user_status',
    '/api/user/all', 'user_all',
    '/api/user/add', 'user_add',
    '/api/user/modify', 'user_modify',
    '/api/user/delete', 'user_delete',
    '/api/msg/push', 'msg_push',
    '/api/msg/delete', 'msg_delete',
    '/api/msg/query/(.+)', 'msg_query',
    '/api/adboard/add', 'ad_add',
    '/api/adboard/delete', 'ad_delete',
    '/api/adboard/query/(.+)', 'ad_query',
)

# 天气预报的 API
weather_api = {'now': 'http://172.17.14.5:8080/teamwork2/api/weather/now',
               'further': 'http://172.17.14.5:8080/teamwork2/api/weather/further'}


class weather:
    def GET(self, key):
        # print key, weather_api
        if key not in weather_api:
            raise web.notfound()
        try:
            r = requests.get(weather_api[key])
            web.header('content-type', 'application/json')
            return r.text
        except Exception, e:
            traceback.print_exc()
            raise web.internalerror()


class clothes:
    def GET(self):
        # 计算9点到18点的平均值，因为有可能时间段缺失。
        def cal_avgtemp(weathers):
            try:
                l = [float(w['main']['temp']) for w in weathers if 9 <= int(w['dt'].split()[-1].split(':')[0]) <= 18]
                return reduce(lambda x, y: x + y, l) / len(l)
            except Exception, e:
                traceback.print_exc()
                return 0.0

        web.header('content-type', 'application/json')
        try:
            clothes_1 = ''
            clothes_2 = ''
            clothes_3 = ''
            r = requests.get(weather_api['now']).json()
            r_5 = requests.get(weather_api['further']).json()
            temp = trans_value(r['main']['temp'], float, 0.0)
            if temp < 10:
                clothes_1 = "穿衣指数：厚"
            elif temp < 20:
                clothes_1 = "穿衣指数：中"
            else:
                clothes_1 = "穿衣指数：薄"
            temp_max = trans_value(r['main']['temp_max'], float, 0.0)
            temp_min = trans_value(r['main']['temp_min'], float, 0.0)
            if temp_max - temp_min >= 5:
                clothes_2 = "夜间温差较大，注意睡眠！"
            avgtemp = [cal_avgtemp(r_5[day]) for day in ['0', '1', '2']]
            if abs(avgtemp[0] - avgtemp[1]) >= 5 or abs(avgtemp[0] - avgtemp[1]) >= 5:
                clothes_3 = "近日温差较大，注意穿衣保暖！"
            return json.dumps({
                'clothes_1': clothes_1,
                'clothes_2': clothes_2,
                'clothes_3': clothes_3})
        except Exception, e:
            return json.dumps({
                'clothes_1': '',
                'clothes_2': '',
                'clothes_3': ''})


class equip:
    def GET(self):
        web.header('content-type', 'application/json')
        try:
            equip_1 = ""
            equip_2 = ""
            r = requests.get(weather_api['now']).json()
            # TO BE CONTINUE: 查description
            # main = r.weather.description
            key = trans_value(r['weather']['main'], str.lower, '')
            if key == "clear":
                equip_1 = "天气晴朗，注意防晒！"
            elif key == "clouds":
                equip_1 = "有降雨概率，请备好伞具！"
            else:
                equip_1 = "今日有雨，备好伞具！"
                equip_2 = "雨天路滑，注意骑行！"
            return json.dumps({
                'equip_1': equip_1,
                'equip_2': equip_2
                })
        except Exception, e:
            traceback.print_exc()
            return json.dumps({
                'equip_1': '',
                'equip_2': ''
            })


class caution:
    def GET(self):
        web.header('content-type', 'application/json')
        try:
            caution_1 = ""
            caution_2 = ""
            caution_3 = ""
            r = requests.get(weather_api['now']).json()
            humidity = trans_value(r['main']['humidity'], float, 0.0)
            temp = trans_value(r['main']['temp'], float, 0.0)
            windspeed = trans_value(r['wind']['speed'], float, 0.0)
            key = trans_value(r['weather']['main'], str.lower, '')
            if humidity < 45:
                caution_1 = "天干气躁，小心上火，多喝水！"
            if humidity > 65 and temp > 30:
                caution_1 = "高温高湿，注意防暑降温，警惕心血管疾病的发生！"
            if 10.8 < windspeed < 20:
                caution_2 = "风力较大，出行注意安全！"
            if windspeed >= 20:
                caution_2 = "台风天气，谨慎出行！"
            if windspeed <= 10.8 and 10 <= temp <= 26 and (key == 'clear' or key == 'clouds'):
                caution_3 = "天气状况良好，适合出行玩乐～"
            else:
                caution_3 = "今日适宜写代码／睡觉"
            return json.dumps({
                'caution_1': caution_1,
                'caution_2': caution_2,
                'caution_3': caution_3
            })
        except Exception, e:
            traceback.print_exc()
            return json.dumps({
                'caution_1': '',
                'caution_2': '',
                'caution_3': ''
            })


class user_login:
    def POST(self):
        # print web.input()
        # print web.data()
        input_json = decode_json_post(web.data(), dict(username='', password=''))
        # print input_json
        username, password = input_json['username'], input_json['password']
        result = list(db.select(
            'user',
            where='username=$username AND password=$password',
            vars={'username': username, 'password': password}))
        if len(result) == 1:
            set_session(1, result[0].uid, result[0].username, result[0].privilege)
        else:
            set_session()
        web.header('content-type', 'application/json')
        # print session.session_id, web.config.session_parameters['cookie_name']
        return json.dumps({
            'session_cookie_name': web.config.session_parameters['cookie_name'],
            'session_id': session.session_id,
            'login': session.login,
            'uid': session.uid,
            'username': session.username,
            'privilege': int_to_privilege(session.privilege)})


class user_logout:
    def POST(self):
        web.header('content-type', 'application/json')
        try:
            set_session()
            session.kill()
        except Exception, e:
            return json.dumps({
                'success': 0,
                'msg': str(e)})
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
            'privilege': int_to_privilege(session.privilege)})


class user_add:
    def POST(self):
        web.header('content-type', 'application/json')
        try:
            input_json = decode_json_post(web.data(), dict(
                username='',
                password='',
                privilege=dict(admin=0, push=0, adboard=0)))
            has_privilege('admin')
            if input_json['username'] == '': raise Exception("username 不能为空")
            if input_json['password'] == '': raise Exception("password 不能为空")
            if type(input_json['privilege']) != dict: raise Exception("privilege 错误")
            db.insert('user',
                      username=input_json['username'],
                      password=input_json['password'],
                      privilege=privilege_to_int(input_json['privilege']))
            return json.dumps({
                'success': 1,
                'msg': ''})
        except Exception, e:
            # traceback.print_exc()
            return json.dumps({
                'success': 0,
                'msg': str(e)})


class user_all:
    def GET(self):
        web.header('content-type', 'application/json')
        try:
            has_privilege('admin')
            # ASC 正序（从小到大），DESC 逆序
            query_result = db.query("SELECT * FROM user ORDER BY username ASC")
            result = []
            for user in query_result:
                result.append({'uid': user.uid,
                               'username': user.username,
                               'privilege': int_to_privilege(user.privilege)})
            return json.dumps(result)
        except Exception, e:
            return json.dumps([])


class user_modify:
    def POST(self):
        web.header('content-type', 'application/json')
        try:
            input_json = decode_json_post(web.data(), dict(
                uid=-1,
                username='',
                password=None,
                privilege=None))
            has_privilege('admin')
            if input_json['uid'] == -1: raise Exception("uid 错误")
            if input_json['username'] == '': raise Exception("username 不能为空")
            # if input_json['password'] == '': raise Exception("password 不能为空")
            # if type(input_json['privilege']) != dict: raise Exception("privilege 错误")
            if input_json['privilege'] is not None: input_json['privilege'] = privilege_to_int(input_json['privilege'])
            if type(input_json['uid']) == str: input_json['uid'] = int(input_json['uid'])
            if len(db.select(
                    'user',
                    where='uid=$uid AND username=$username',
                    vars={'uid': input_json['uid'], 'username': input_json['username']})) != 1:
                raise Exception("uid 与 username 不匹配，请重新登录")
            db.update('user',
                      where='uid=$uid AND username=$username',
                      vars={'uid': input_json['uid'], 'username': input_json['username']},
                      **dict([(key, input_json[key]) for key in ['password', 'privilege']
                              if input_json.get(key) is not None])
                      )
            return json.dumps({
                'success': 1,
                'msg': ''})
        except Exception, e:
            # traceback.print_exc()
            return json.dumps({
                'success': 0,
                'msg': str(e)})


class user_delete:
    def POST(self):
        web.header('content-type', 'application/json')
        try:
            input_json = decode_json_post(web.data(), dict(
                uid=-1,
                username=''))
            has_privilege('admin')
            if input_json['uid'] == -1: raise Exception("uid 错误")
            if input_json['username'] == '': raise Exception("username 不能为空")
            if type(input_json['uid']) == str: input_json['uid'] = int(input_json['uid'])
            if len(db.select(
                    'user',
                    where='uid=$uid AND username=$username',
                    vars={'uid': input_json['uid'], 'username': input_json['username']})) != 1:
                raise Exception("uid 与 username 不匹配，请重新登录")
            db.delete('user',
                      where='uid=$uid AND username=$username',
                      vars={'uid': input_json['uid'], 'username': input_json['username']})
            return json.dumps({
                'success': 1,
                'msg': ''})
        except Exception, e:
            # traceback.print_exc()
            return json.dumps({
                'success': 0,
                'msg': str(e)})


class msg_push:
    def POST(self):
        def server_push(msg, url='https://api.jpush.cn/v3/push', app_key='6c2a93e704b62871e6582b58', master_secret='49c60d5092b30b66d2e46a46'):
            r = requests.post(
                url,
                headers={
                    'content-type': 'application/json',
                    'Authorization': 'Basic %s' % base64.b64encode('%s:%s' % (app_key, master_secret))
                },
                json=dict(
                    platform='all',
                    audience='all',
                    notification=dict(
                        alert='%s: %s' % (msg['editor'], msg['title']),
                        extras=dict(url=msg['url'])
                    ))
                )
            # print r.json()
            if r.status_code != 200:
                raise Exception('推送不成功')

        web.header('content-type', 'application/json')
        try:
            input_json = decode_json_post(web.data(), dict(
                title='',
                editor='',
                details='',
                url=''))
            has_privilege('push')
            if db.insert(
                    'msg',
                    title=input_json['title'],
                    editor=input_json['editor'],
                    details=input_json['details'],
                    url=input_json['url'],
                    postuser=session.username
            ) is None:
                raise Exception('数据错误')

            # 极光的 API
            server_push(dict(
                title=input_json['title'],
                editor=input_json['editor'],
                url=input_json['url']))

            return json.dumps({
                'success': 1,
                'msg': ''})
        except Exception, e:
            traceback.print_exc()
            return json.dumps({
                'success': 0,
                'msg': str(e)})


class msg_query:
    def GET(self, key):
        today_utc = time.time()
        today_utc8_gm = get_utc8_gm(today_utc)
        q = None
        if key == 'today':
            start_utc = op_utc(
                today_utc, 'minus',
                today_utc8_gm.tm_sec, today_utc8_gm.tm_min, today_utc8_gm.tm_hour)
            start = construct_localtime(start_utc)
            q = db.query("SELECT * FROM msg WHERE posttime >= '%s' ORDER BY posttime DESC" % start)
        elif key == 'week':
            start_utc = op_utc(
                today_utc, 'minus',
                today_utc8_gm.tm_sec, today_utc8_gm.tm_min, today_utc8_gm.tm_hour, today_utc8_gm.tm_wday)
            start = construct_localtime(start_utc)
            q = db.query("SELECT * FROM msg WHERE posttime >= '%s' ORDER BY posttime DESC" % start)
        elif key == 'all':
            q = db.query("SELECT * FROM msg")
        else:
            raise web.notfound()

        result = []
        for msg in q:
            result.append({
                'id': msg.id,
                'editor': msg.editor,
                'title': msg.title,
                'details': msg.details,
                'url': msg.url,
                'posttime': msg.posttime.strftime('%Y-%m-%d %H:%m')
            })
        return json.dumps(result)

class msg_delete:
    pass


class ad_add:
    # 时间都以 UTC 时间请求
    def POST(self):
        web.header('content-type', 'application/json')
        try:
            input_json = decode_json_post(web.data(), dict(
                title='',
                editor='',
                details='',
                starttime=''))
            has_privilege('adboard')
            if input_json['starttime'] == '': input_json['starttime'] = construct_localtime()
            else: input_json['starttime'] = decode_time(input_json['starttime'])
            if db.insert(
                    'adboard',
                    title=input_json['title'],
                    editor=input_json['editor'],
                    details=input_json['details'],
                    starttime=input_json['starttime'],
                    postuser=session.username
            ) is None:
                raise Exception('数据错误')
            return json.dumps({
                'success': 1,
                'msg': ''})
        except Exception, e:
            traceback.print_exc()
            return json.dumps({
                'success': 0,
                'msg': str(e)})


class ad_query:
    def GET(self, key):
        today_utc = time.time()
        today_utc8_gm = get_utc8_gm(today_utc)
        q = None
        if key == 'today':
            start_utc = op_utc(
                today_utc, 'minus',
                today_utc8_gm.tm_sec, today_utc8_gm.tm_min, today_utc8_gm.tm_hour)
            end_utc = op_utc(
                today_utc, 'add',
                60 - today_utc8_gm.tm_sec, 60 - today_utc8_gm.tm_min, 24 - today_utc8_gm.tm_hour,)
            start = construct_localtime(start_utc)
            end = construct_localtime(end_utc)
            q = db.query("SELECT * FROM adboard WHERE starttime >= '%s' AND starttime <= '%s' ORDER BY starttime DESC" % (start, end))

        elif key == 'week':
            start_utc = op_utc(
                today_utc, 'minus',
                today_utc8_gm.tm_sec, today_utc8_gm.tm_min, today_utc8_gm.tm_hour, today_utc8_gm.tm_wday)
            end_utc = op_utc(
                today_utc, 'add',
                60 - today_utc8_gm.tm_sec, 60 - today_utc8_gm.tm_min, 24 - today_utc8_gm.tm_hour,
                6 - today_utc8_gm.tm_wday)
            start = construct_localtime(start_utc)
            end = construct_localtime(end_utc)
            q = db.query("SELECT * FROM adboard WHERE starttime >= '%s' AND starttime <= '%s' ORDER BY starttime DESC" % (start, end))

        elif key == 'expired':
            t = construct_localtime()
            q = db.query("SELECT * FROM adboard WHERE starttime <= '%s' ORDER BY starttime DESC" % t)
        elif key == 'future':
            t = construct_localtime()
            q = db.query("SELECT * FROM adboard WHERE starttime >= '%s' ORDER BY starttime DESC" % t)
        elif key == 'all':
            q = db.query("SELECT * FROM adboard")
        else:
            raise web.notfound()

        result = []
        for ad in q:
            result.append({
                'id': ad.id,
                'editor': ad.editor,
                'title': ad.title,
                'details': ad.details,
                'starttime': ad.starttime.strftime('%Y-%m-%d %H:%m'),
                'posttime': ad.posttime.strftime('%Y-%m-%d %H:%m')
            })
        return json.dumps(result)


class ad_delete:
    def POST(self):
        pass


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
    return construct_localtime(
        time.mktime(
            time.strptime(time_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')))


def int_to_privilege(priv_num):
    priv_list = ['adboard', 'push', 'admin']
    if not (type(priv_num) == int or type(priv_num) == long) or priv_num < 0:
        return dict([(key, 0) for key in priv_list])
    return dict([(priv_list[-(index+1)], 1 if priv_num & (0x1 << index) else 0) for index in range(len(priv_list))])


def privilege_to_int(priv_dict):
    priv_list = ['adboard', 'push', 'admin']
    priv_num = 0
    for index in range(len(priv_list)):
        if priv_dict.get(priv_list[-(index + 1)]) == 1:
            priv_num |= (0x1 << index)
    return priv_num


def has_privilege(key):
    # 如果不读数据库的话就可以从 session 里读
    # print session.login
    if not session.login:
        raise Exception('请登录后再操作')
    result = list(db.select(
        'user',
        where='uid=$uid AND username=$username',
        vars={'uid': session.uid, 'username': session.username}))
    if len(result) == 1:
        # print int_to_privilege(result[0].privilege)
        if int_to_privilege(result[0].privilege).get(key) == 1:
            return True
        raise Exception('权限不足')
    else:
        raise Exception('登录错误，请重新登录或清空 cookies')


def arguments_verify(params):
    for param in params:
        if type(param['value']) != param['type']: raise Exception('%s 错误' % param['key'])
        if param['value'] == param['empty']: raise Exception('%s 不能为空' % param['key'])


# 如果客户端传过来的是
def decode_json_post(data, params):
    result = {}
    try:
        # print type(data), data
        # print web.ctx.env
        result = json.loads(data)
        if type(result) != dict: # double-json problem
            result = json.loads(result)
        # print type(result), result
    except Exception, e:
        # print "Error: %s" % str(e)
        traceback.print_exc()
        raise web.badrequest()
    # return dict([(key, paramsf[key]) for key in params if key not in result]
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


def trans_value(value, tran_func, default):
    try:
        return tran_func(value)
    except Exception, e:
        return default


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
    db = web.database(dbn='mysql', db='test', user='', pw='', charset='utf8')
    app.run(port=1234)


