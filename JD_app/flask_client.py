import logging
import random
from flask import Flask, request, render_template, jsonify, make_response, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_, text, func
import time
import jwt
import hashlib
# from JDapp import app
from get_order import get_order
from flask_cors import CORS
import urllib.parse
import requests
from deal_html import deal_html
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://yisa_oe:yisa_oe@192.168.9.108:3306/yisa_oe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = 'yisa123456'
CORS(app, supports_credentials=True)
db = SQLAlchemy(app)
r = requests.Session()


# 接受数据
def get_message(data):
    data = data.decode()
    print(data)
    str = data.split('&')
    data = {}
    for i in str:
        str1 = i.split('=')
        str1[1] = urllib.parse.unquote(str1[1])
        data[str1[0]] = str1[1]
    return data


# 清理冗杂数据
def clear_info():
    now = datetime.now()
    task_info = User_task.query.filter(User_task.com_time <= now - timedelta(days=15)).all()
    for i in task_info:
        db.session.delete(i)
    db.session.commit()


# 登录状态的装饰器
def login_check(func):
    def wrapper(*args, **kwargs):
        # 在session对象中获取提交过来的token
        key = '123456'
        token = session.get('token')
        if token == "":
            result = {'status': 1, 'message': '请先登录!'}
            return jsonify(result)
        # token的效验
        try:
            # decode方法中　首先会验签　签名是否有效 验签成功后　从payload获取有效期　判断tokn是否在有效期
            payload = jwt.decode(token, key, algorithms='HS256')
        except:
            result = {'status': 1, 'message': '登录失效，请重新登录!'}
            return jsonify(result)
        # 从结果中获取私有申明
        # name = payload['name']
        # 根据用户名称获取用户对象
        # user = User.query.filter(User.name == name).first()
        # 将用户对象作为request的附加属性
        # request.myuser = user
        # 调用所修饰的函数
        return func(*args, **kwargs)

    return wrapper


# APP用户表
class User(db.Model):
    __tablename__ = 'zz_user_info'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), nullable=True)
    password = db.Column(db.String(32))
    re_phone = db.Column(db.String(11))
    id_code = db.Column(db.String(18))
    name = db.Column(db.String(8))
    zt = db.Column(db.Integer)
    local_time = db.Column(db.DateTime)
    register_time = db.Column(db.DateTime)
    user_code = db.Column(db.Integer)
    head_pho = db.Column(db.String(128))
    login_time = db.Column(db.Integer)

    def __init__(self, username, password, id_code, re_phone, zt, local_time, name, register_time, user_code,
                 head_pho, login_time):
        self.username = username
        self.password = password
        self.id_code = id_code
        self.re_phone = re_phone
        self.zt = zt
        self.local_time = local_time
        self.name = name
        self.register_time = register_time
        self.user_code = user_code
        self.head_pho = head_pho
        self.login_time = login_time


# 积分商品表
class Pro_info(db.Model):
    __tablename__ = 'zz_pro_info'
    id = db.Column(db.Integer, primary_key=True)
    pro_name = db.Column(db.String(32))
    pro_code = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    name = db.Column(db.String(16))
    pro_text = db.Column(db.String(255))
    img_url = db.Column(db.String(64))

    def __init__(self, pro_name, pro_code, create_time, name, pro_text, img_url):
        self.pro_name = pro_name
        self.pro_code = pro_code
        self.create_time = create_time
        self.name = name
        self.pro_text = pro_text
        self.img_url = img_url


# 工作表
class Com_info(db.Model):
    __tablename__ = 'zz_com_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))
    com_name = db.Column(db.String(32))
    com_introduce = db.Column(db.String(32))
    com_welfare = db.Column(db.String(32))
    com_job = db.Column(db.String(16))
    com_respon = db.Column(db.String(32))
    job_require = db.Column(db.String(32))
    com_pay = db.Column(db.String(16))
    job_address = db.Column(db.String(32))
    com_contact = db.Column(db.String(16))
    com_phone = db.Column(db.String(11))
    zt = db.Column(db.String(1))
    local_time = db.Column(db.DateTime)

    def __init__(self, name, com_name, com_introduce, com_welfare, com_job, com_respon, job_require, com_pay,
                 job_address,
                 com_contact, com_phone, zt, local_time):
        self.name = name
        self.com_name = com_name
        self.com_introduce = com_introduce
        self.com_welfare = com_welfare
        self.com_job = com_job
        self.com_respon = com_respon
        self.job_require = job_require
        self.com_pay = com_pay
        self.job_address = job_address
        self.com_contact = com_contact
        self.com_phone = com_phone
        self.zt = zt
        self.local_time = local_time


# 地址表
class User_add(db.Model):
    __tablename__ = 'zz_user_add'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    re_phone = db.Column(db.String(11))
    consignee = db.Column(db.String(16))
    phone = db.Column(db.String(11))
    area_address = db.Column(db.String(32))
    deta_address = db.Column(db.String(32))
    default_address = db.Column(db.String(1))

    def __init__(self, name, consignee, phone, area_address, deta_address, default_address, re_phone):
        self.name = name
        self.re_phone = re_phone
        self.consignee = consignee
        self.phone = phone
        self.area_address = area_address
        self.deta_address = deta_address
        self.default_address = default_address


# 收藏表
class User_col(db.Model):
    __tablename__ = 'zz_user_col'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    re_phone = db.Column(db.String(11))
    art_id = db.Column(db.Integer)
    col_time = db.Column(db.DateTime)

    def __init__(self, name, art_id, col_time, re_phone):
        self.name = name
        self.re_phone = re_phone
        self.art_id = art_id
        self.col_time = col_time


# 系统用户表
class PC_user(db.Model):
    __tablename__ = 'zz_operator'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    sys_name = db.Column(db.String(16))
    password = db.Column(db.String(16))
    reg_time = db.Column(db.DateTime)
    zt = db.Column(db.String(1))

    def __init__(self, name, sys_name, password, reg_time, zt):
        self.name = name
        self.sys_name = sys_name
        self.password = password
        self.reg_time = reg_time
        self.zt = zt


# 商品兑换表
class Pro_change(db.Model):
    __tablename__ = 'zz_pro_change'
    id = db.Column(db.Integer, primary_key=True)
    pro_name = db.Column(db.String(16))
    name = db.Column(db.String(10))
    re_phone = db.Column(db.String(11))
    add_pho = db.Column(db.String(32))
    tra_num = db.Column(db.String(16))
    c_time = db.Column(db.DateTime)
    zt = db.Column(db.String(1))

    def __init__(self, pro_name, name, add_pho, tra_num, c_time, re_phone, zt):
        self.pro_name = pro_name
        self.name = name
        self.re_phone = re_phone
        self.add_pho = add_pho
        self.tra_num = tra_num
        self.c_time = c_time
        self.zt = zt


# 地区省市表
class Region(db.Model):
    __tablename__ = 'region'
    code = db.Column(db.String(6), primary_key=True)
    full_name = db.Column(db.String(50))
    name = db.Column(db.String(30))
    pcode = db.Column(db.String(6))
    level = db.Column(db.Integer)
    error = db.Column(db.String(45))
    longitude = db.Column(db.Numeric)
    latitude = db.Column(db.Numeric)

    def __init__(self, code, full_name, name, pcode, level, error, longitude, latitude):
        self.code = code
        self.full_name = full_name
        self.name = name
        self.pcode = pcode
        self.level = level
        self.error = error
        self.longitude = longitude
        self.latitude = latitude


# 任务表
class Task(db.Model):
    __tablename__ = 'zz_man_task'
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(16))
    task_num = db.Column(db.Integer)
    task_time = db.Column(db.Integer)

    def __int__(self, task_name, task_num, task_time, taks_code):
        self.task_name = task_name
        self.task_num = task_num
        self.task_time = task_time


# 用户完成任务表
class User_task(db.Model):
    __tablename__ = "zz_com_task"
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(10))
    name = db.Column(db.String(10))
    re_phone = db.Column(db.String(11))
    com_num = db.Column(db.Integer)
    com_time = db.Column(db.DateTime)
    tid = db.Column(db.Integer)

    def __int__(self, task_name, name, com_time, re_phone, tid, com_num):
        self.task_name = task_name
        self.name = name
        self.com_num = com_num
        self.com_time = com_time
        self.re_phone = re_phone
        self.tid = tid


# 文章详情表
class Art_info(db.Model):
    __tablename__ = 'zz_art_info'
    id = db.Column(db.Integer, primary_key=True)
    art_title = db.Column(db.String(16))
    cname = db.Column(db.String(10))
    local_time = db.Column(db.DateTime)
    art_type = db.Column(db.String(10))
    zt = db.Column(db.String(1))
    vid_info = db.Column(db.String(128))
    art_read = db.Column(db.Integer)
    art_like = db.Column(db.Integer)
    comments = db.Column(db.Integer)
    share = db.Column(db.Integer)
    art_cont = db.Column(db.Text)

    def __init__(self, art_title, cname, local_time, art_type, zt, vid_info, art_read, art_like, comments, share,
                 art_cont):
        self.art_title = art_title
        self.cname = cname
        self.local_time = local_time
        self.art_type = art_type
        self.zt = zt
        self.vid_info = vid_info
        self.art_read = art_read
        self.art_like = art_like
        self.comments = comments
        self.share = share
        self.art_cont = art_cont


# 允许注册表
class Register(db.Model):
    __tablename__ = 'zz_register'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))
    id_code = db.Column(db.String(32))

    def __init__(self, name, id_code):
        self.name = name
        self.id_code = id_code


# app注册
@app.route('/register', methods=['POST'])
def register():
    re_phone = request.form.get('re_phone')
    name = request.form.get('name')
    id_code = request.form.get('id_code')
    password = request.form.get('password')
    db.reflect()
    old_phone = User.query.filter(User.re_phone == re_phone).first()
    old_name = User.query.filter(User.name == name).first()
    old_id_code = User.query.filter(User.id_code == id_code).first()
    # got_true = Register.query.filter(and_(Register.name == name, Register.id_code == id_code)).first()
    if old_phone:
        result = {'status': 1, 'message': '该手机号已被注册'}
        return jsonify(result)
    elif old_id_code:
        result = {'status': 1, 'message': '该身份信息已被注册'}
        return jsonify(result)
    # else:
    #    if got_true:
    #        md5 = hashlib.md5()
    #        md5.update(password.encode())
    #        password_h = md5.hexdigest()
    #        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #        user_info = User(username=name, password=password_h, re_phone=re_phone, id_code=id_code, name=name, zt=1,
    #                         register_time=now_time, local_time=now_time, user_code=0, head_pho="", login_time=0)
    #        db.session.add(user_info)
    #        db.session.commit()
    #        result = {'status': 0, 'message': '成功'}
    #    else:
    #        result = {'status': 1, 'message': '注册人员信息不符'}
    else:
        md5 = hashlib.md5()
        md5.update(password.encode())
        password_h = md5.hexdigest()
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        user_info = User(username=name, password=password_h, re_phone=re_phone, id_code=id_code, name=name, zt=1,
                         register_time=now_time, local_time=now_time, user_code=0, head_pho="", login_time=0)
        db.session.add(user_info)
        db.session.commit()
        result = {'status': 0, 'message': '成功'}
        return jsonify(result)


# app登录
@app.route('/login', methods=["GET", 'POST'])
def denglu_solution():
    re_phone = request.form.get('re_phone')
    password = request.form.get('password')
    db.reflect()
    try:
        user_info = User.query.filter(User.re_phone == re_phone).first()
        user_password = user_info.password
        if user_info.zt == '0':
            result = {'status': 1, 'message': '该账号已被停用'}
            return jsonify(result)
    except:
        result = {'status': 1, 'message': '手机号未注册,请先注册'}
        return jsonify(result)
    md5 = hashlib.md5()
    md5.update(password.encode())
    password_h = md5.hexdigest()
    if password_h == user_password:
        name = user_info.name
        re_phone = user_info.re_phone
        # r.headers.update({'token': token})
        # print(r.headers)
        id = user_info.id
        # print('----------', token)
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        token = make_token(name, re_phone, now)
        session['token'] = token
        local_time = User.query.filter(User.id == id).first()
        local_time.local_time = now
        local_time.login_time += 1
        local_time.zt = '2'
        db.session.commit()
        result = {'status': 0, 'message': '成功',
                  'data': [{'token': token, 'uid': id, 'name': name, 're_phone': re_phone}]}
        return jsonify(result)
    else:
        result = {'status': 1, 'message': '用户名或密码错误'}
        return jsonify(result)


# app个人中心界面
@app.route('/person_center', methods=['GET', 'POST'])
@login_check
def person_center():
    id = request.form.get('id')
    user_info = User.query.filter(User.id == id).first()
    task_info = Task.query.order_by(text('-id'))
    user_info_show = []
    c = {}
    code = 0
    all_code = 0
    c['user_code'] = user_info.user_code
    c['username'] = user_info.username
    c['head_pho'] = user_info.head_pho
    now = time.strftime("%Y-%m-%d", time.localtime())
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    for task in task_info:
        all_code += int(task.task_num) * int(task.task_time)
        try:
            info = User_task.query.filter(
                and_(User_task.task_name == task.task_name, User_task.com_time.between(now, now_time))).order_by(
                text('-com_num')).first()
            code += int(info.com_num) * int(task.task_num)
        except:
            code += 0
            continue
    c['get_code'] = code
    c['all_code'] = all_code
    user_info_show.append(c)
    result = {'status': 0, 'message': '成功'}
    result['data'] = user_info_show
    return jsonify(result)


# app忘记密码
@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    name = request.form.get('name')
    id_code = request.form.get('id_code')
    user_info = User.query.filter(and_(User.name == name, User.id_code == id_code)).first()
    if user_info:
        id = user_info.id
        result = {'status': 0, 'message': '成功', 'data': [{'id': id}]}
        return jsonify(result)
    else:
        result = {'status': 1, 'message': '输入的用户信息有误'}
        return jsonify(result)


# app忘记密码-修改密码
@app.route('/forget_change', methods=['GET', 'POST'])
def forget_change():
    id = request.form.get('id')
    new_password = request.form.get('password')
    user_info = User.query.filter(User.id == id).first()
    md5 = hashlib.md5()
    md5.update(new_password.encode())
    password_h = md5.hexdigest()
    user_info.password = password_h
    db.session.commit()
    result = {'status': 0, 'message': '成功'}
    return jsonify(result)


# app修改用户名
@app.route('/change_username', methods=['GET', 'POST'])
def change_username():
    # data = request.get_data()
    # data = get_message(data)
    username = request.form.get('username')
    name = request.form.get('name')
    re_phone = request.form.get('re_phone')
    user_info = User.query.filter(and_(User.name == name, User.re_phone == re_phone)).first()
    user_info.username = username
    db.session.commit()
    result = {'status': 0, 'message': '成功'}
    return jsonify(result)


# app修改密码
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    # data = request.get_data()
    # data = get_message(data)
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    name = request.form.get('name')
    re_phone = request.form.get('re_phone')
    try:
        user_info = User.query.filter(and_(User.name == name, User.re_phone == re_phone)).first()
    except:
        result = {'status': 1, 'message': '用户信息输入有误'}
        return jsonify(result)
    md5 = hashlib.md5()
    md5.update(old_password.encode())
    password_h = md5.hexdigest()
    if password_h != user_info.password:
        result = {'status': 1, 'message': '原密码输入错误'}
        return jsonify(result)
    else:
        md5 = hashlib.md5()
        md5.update(new_password.encode())
        password_n = md5.hexdigest()
        user_info.password = password_n
        db.session.commit()
        result = {'status': 0, 'message': '成功'}
        return jsonify(result)


# app头像修改
@app.route('/change_avatar', methods=['GET', 'POST'])
def change_avatar():
    # img_file = request.files['img_file'].read()
    filepath = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '/imgs/'
    f = request.files['img_file']
    img = f.filename
    f.save(filepath + img)
    head_pho = "http://192.168.9.108:8089/imgs/" + img
    # try:
    #    files = {'file': ('image.jpg', img_file)}
    #    weed_url1 = 'http://192.168.0.60:9333/dir/assign?ttl=3M'  # weed存储地址
    #    weed_url2 = 'http://192.168.0.60:9081/'
    #    weed_res1 = requests.post(weed_url1, {}, timeout=10)
    #    weed_res1 = weed_res1.json()
    #    weed_res2 = requests.post(weed_url2 + weed_res1['fid'], files=files, timeout=10)
    #    kt_img_url = weed_res1['publicUrl'] + weed_res1['fid'] + '.jpg'
    #    head_pho = kt_img_url
    # except (Exception) as e:
    #    logging.exception("图片存weed错误:%s", str(e))
    #    return 'error'
    name = request.form.get('name')
    re_phone = request.form.get('re_phone')
    user_info = User.query.filter(and_(User.name == name, User.re_phone == re_phone)).first()
    user_info.head_pho = head_pho
    db.session.commit()
    result = {'status': 0, 'message': '成功'}
    return jsonify(result)


# app地址管理展示
@app.route('/address_manage', methods=['GET', 'POST'])
def address_manage():
    address_info_show = []
    name = request.form.get('name')
    re_phone = request.form.get('re_phone')
    db.reflect()
    add_info = User_add.query.order_by(text('-id')).filter(
        and_(User_add.name == name, User_add.re_phone == re_phone)).all()
    for data in add_info:
        c = {}
        c['id'] = data.id
        c['consignee'] = data.consignee
        c['phone'] = data.phone
        c['address'] = data.area_address + data.deta_address
        c['default_address'] = data.default_address
        address_info_show.append(c)
    result = {'status': 0, 'message': '成功'}
    result['data'] = address_info_show
    return jsonify(result)


# app地址编辑
@app.route('/address_edit', methods=['GET', 'POST'])
def address_edit():
    add_info_show = []
    # data = request.get_data()
    # data = get_message(data)
    id = request.form.get('id')
    add_info = User_add.query.filter(User_add.id == id).first()
    c = {}
    c['consignee'] = add_info.consignee
    c['phone'] = add_info.phone
    c['area_address'] = add_info.area_address
    c['deta_address'] = add_info.deta_address
    c['name'] = add_info.name
    c['re_phone'] = add_info.re_phone
    c['default_address'] = add_info.default_address
    add_info_show.append(c)
    result = {'status': 0, 'message': '成功'}
    result['data'] = add_info_show
    return jsonify(result)


# app地址删除
@app.route('/address_delete', methods=['GET', 'POST'])
def address_delete():
    # data = request.get_data()
    # data = get_message(data)
    id = request.form.get('id')
    add_info = User_add.query.filter(User_add.id == id).first()
    db.session.delete(add_info)
    db.session.commit()
    result = {'status': 0, 'message': '成功'}
    return jsonify(result)


# 省市区信息展示
@app.route('/address_info', methods=['GET', 'POST'])
def address_info():
    region_info_show = []
    db.reflect()
    region_info = Region.query.order_by(text('code'))
    for data in region_info:
        c = {}
        c['code'] = data.code
        c['full_name'] = data.full_name
        c['name'] = data.name
        c['pcode'] = data.pcode
        region_info_show.append(c)
    result = {'status': 0, 'message': '成功'}
    result['data'] = region_info_show
    return jsonify(result)


# app地址添加
@app.route('/address_add', methods=['GET', 'POST'])
def address_add():
    id = request.form.get('id')
    consignee = request.form.get('consignee')
    phone = request.form.get('phone')
    area_address = request.form.get('area_address')
    deta_address = request.form.get('deta_address')
    name = request.form.get('name')
    re_phone = request.form.get('re_phone')
    default_address = request.form.get('default_address')
    if not id:
        old_address = User_add.query.filter(
            and_(User_add.name == name, User_add.consignee == consignee, User_add.phone == phone,
                 User_add.area_address == area_address,
                 User_add.deta_address == deta_address)).first()
        if old_address:
            result = {'status': 1, 'message': '地址已经存在'}
            return jsonify(result)
        else:
            if default_address == '1':
                info = User_add.query.filter(User_add.default_address == '1').first()
                if info:
                    info.default_address = '0'
                    db.session.commit()
            address_info = User_add(name=name, consignee=consignee, phone=phone, area_address=area_address,
                                    deta_address=deta_address, default_address=default_address, re_phone=re_phone)
            db.session.add(address_info)
            db.session.commit()
            result = {'status': 0, 'message': '新建成功'}
            return jsonify(result)
    else:
        address_info = User_add.query.filter(User_add.id == id).first()
        if default_address == '1':
            info = User_add.query.filter(User_add.default_address == '1').first()
            if info:
                info.default_address = '0'
            db.session.commit()
        address_info.consignee = consignee
        address_info.phone = phone
        address_info.area_address = area_address
        address_info.deta_address = deta_address
        address_info.default_address = default_address
        db.session.commit()
        result = {'status': 0, 'message': '更新成功'}
        return jsonify(result)


# app兑换中心
@app.route('/change_center', methods=['GET', 'POST'])
def change_center():
    pro_info_show = []
    db.reflect()
    # data = request.get_data()
    # data = get_message(data)
    name = request.form.get('name')
    re_phone = request.form.get('re_phone')
    page_num = request.form.get('page_num')
    page_size = request.form.get('page_size')
    key_word = request.form.get('key_word')
    user_info = User.query.filter(and_(User.name == name, User.re_phone == re_phone)).first()
    user_code = user_info.user_code
    total = Pro_info.query.order_by(text('-create_time')).count()
    if not key_word:
        pro_info = Pro_info.query.order_by(text('-create_time'))[
                   ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        for b in pro_info:
            c = {}
            c['id'] = b.id
            c['pro_name'] = b.pro_name
            c['pro_code'] = b.pro_code
            c['img_url'] = b.img_url.split('**')
            pro_info_show.append(c)
        result = {'status': 0, 'message': '成功', 'total': total, 'data': [{}]}
        result['data'][0]['user_code'] = user_code
        result['data'][0]['pro_info'] = pro_info_show
        return jsonify(result)
    else:
        try:
            pro_info = Pro_info.query.filter(Pro_info.pro_name.like(f'%{key_word}%')).all()[
                       ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        except:
            result = {'status': 1, 'message': '未查询到结果', 'data': []}
            return jsonify(result)
        for b in pro_info:
            c = {}
            c['id'] = b.id
            c['pro_name'] = b.pro_name
            c['pro_code'] = b.pro_code
            c['img_url'] = b.img_url.split('**')
            pro_info_show.append(c)
        result = {'status': 0, 'message': '成功', 'total': total, 'data': [{}]}
        result['data'][0]['user_code'] = user_code
        result['data'][0]['pro_info'] = pro_info_show
        return jsonify(result)


# app兑换商品详情
@app.route('/pro_details', methods=['GET', 'POST'])
def app_pro_details():
    pro_info_show = []
    # data = request.get_data()
    # data = get_message(data)
    id = request.form.get('id')
    pro_info = Pro_info.query.filter(Pro_info.id == id).first()
    c = {}
    p_text = deal_html(pro_info.pro_text)
    c['pro_name'] = pro_info.pro_name
    c['pro_code'] = pro_info.pro_code
    c['pro_text'] = p_text[0:-1]
    c['img_url'] = p_text[-1]
    pro_info_show.append(c)
    result = {'status': 0, 'message': '成功'}
    result['data'] = pro_info_show
    return jsonify(result)


# app兑换商品选择地址
@app.route('/get_address', methods=['GET', 'POST'])
def get_address():
    add_info_show = []
    name = request.form.get('name')
    re_phone = request.form.get('re_phone')
    add_info = User_add.query.filter(and_(User_add.name == name, User_add.re_phone == re_phone)).all()
    for c in add_info:
        b = {}
        b['consignee'] = c.consignee
        b['area_address'] = c.area_address
        b['deta_address'] = c.deta_address
        add_info_show.append(b)
    result = {'status': 0, 'message': '成功'}
    result['data'] = add_info_show
    return jsonify(result)


# app兑换商品地址入库
@app.route('/address_into', methods=['GET', 'POST'])
def address_into():
    id = request.form.get('id')
    name = request.form.get('name')
    re_phone = request.form.get('re_phone')
    consignee = request.form.get('consignee')
    address = request.form.get('address')
    pro_info = Pro_info.query.filter(Pro_info.id == id).first()
    pro_name = pro_info.pro_name
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    pro_change_info = Pro_change(pro_name=pro_name, name=name, add_pho=consignee + address,
                                 c_time=now_time, tra_num='', re_phone=re_phone, zt='0')
    user_info = User.query.filter(and_(User.name == name, User.re_phone == re_phone)).first()
    if (user_info.user_code - pro_info.pro_code) < 0:
        result = {'status': 1, 'message': '积分不足,兑换失败'}
        return jsonify(result)
    else:
        user_info.user_code -= pro_info.pro_code
        db.session.add(pro_change_info)
        db.session.commit()
        result = {'status': 0, 'message': '成功'}
        return jsonify(result)


# app订单中心
@app.route('/order_center', methods=['GET', 'POST'])
def order_center():
    order_info_show = []
    # data = request.get_data()
    # data = get_message(data)
    name = request.form.get('name')
    re_phone = request.form.get('re_phone')
    page_num = request.form.get('page_num')
    page_size = request.form.get('page_size')
    zt = request.form.get('zt')
    order_info = Pro_change.query.order_by(text('-c_time')).filter(
        and_(Pro_change.name == name, Pro_change.re_phone == re_phone, Pro_change.zt == zt)).all()[
                 ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
    total = Pro_change.query.filter(
        and_(Pro_change.name == name, Pro_change.re_phone == re_phone, Pro_change.zt == zt)).count()
    for c in order_info:
        b = {}
        pro_info = Pro_info.query.filter(Pro_info.pro_name == c.pro_name).first()
        b['id'] = c.id
        b['goods_id'] = pro_info.id
        b['pro_name'] = c.pro_name
        b['img_url'] = pro_info.img_url.split('**')
        b['tra_num'] = c.tra_num
        order_info_show.append(b)
    result = {'status': 0, 'message': '成功', 'total': total}
    result['data'] = order_info_show
    return jsonify(result)


# app确定收货
@app.route('/get_pro', methods=['GET', 'POST'])
def get_pro():
    id = request.form.get('id')
    change_info = Pro_change.query.filter(Pro_change.id == id).first()
    change_info.zt = 1
    db.session.commit()
    result = {'status': 0, 'message': '成功'}
    return jsonify(result)


# app查看物流信息
@app.route('/logistics_info', methods=['GET', 'POST'])
def logistics_info():
    logistics_info_show = []
    # data = request.get_data()
    # data = get_message(data)
    tra_num = request.form.get('tra_num')
    if not tra_num:
        result = {'status': 0, 'message': '快递正在等待揽件'}
        return jsonify(result)
    else:
        res = get_order(tra_num)
        c = {}
        c['state'] = res['state']
        c['wl_info'] = res['data']
        c['tra_num'] = tra_num
        logistics_info_show.append(c)
        result = {'status': 0, 'message': '成功'}
        result['data'] = logistics_info_show
        return jsonify(result)


# app任务获取
@app.route('/get_task', methods=['GET', 'POST'])
def get_task():
    task_info_show = []
    name = request.form.get('name')
    re_phone = request.form.get('re_phone')
    task_info = Task.query.order_by(text('id')).all()
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    now = time.strftime("%Y-%m-%d", time.localtime())
    for b in task_info:
        c = {}
        c['id'] = b.id
        c['task_name'] = b.task_name
        c['task_num'] = b.task_num * b.task_time
        c['task_time'] = b.task_time
        user_task = User_task.query.filter(
            and_(User_task.task_name == b.task_name, User_task.name == name,
                 User_task.re_phone == re_phone, User_task.com_time.between(now, now_time))).all()
        num = 0
        for i in user_task:
            if i.com_num > 0:
                num += i.com_num
        if not num or num < 0:
            c['flish_time'] = 0
        elif num >= b.task_time:
            c['flish_time'] = b.task_time
        else:
            c['flish_time'] = num
        task_info_show.append(c)
    result = {'status': 0, 'message': '成功'}
    result['data'] = task_info_show
    return jsonify(result)


# app任务中心
@app.route('/task_center', methods=['GET', 'POST'])
def task_center():
    name = request.form.get('name')
    re_phone = request.form.get('re_phone')
    # task_name = request.form.get('task_name')
    task_id = request.form.get('id')
    tid = request.form.get('tid')
    action = request.form.get('action')
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    now = time.strftime("%Y-%m-%d", time.localtime())
    user_info = User.query.filter(and_(User.name == name, User.re_phone == re_phone)).first()
    task_info = Task.query.filter(Task.id == task_id).first()
    if not action:
        user_task = User_task.query.filter(
            and_(User_task.task_name == task_info.task_name, User_task.name == name,
                 User_task.re_phone == re_phone, User_task.tid == tid,
                 User_task.com_time.between(now, now_time))).first()
        test_info = User_task.query.filter(
            and_(User_task.task_name == task_info.task_name, User_task.name == name, User_task.re_phone == re_phone,
                 User_task.com_time.between(now, now_time))).all()
        num = 0
        for i in test_info:
            if i.com_num > 0:
                num += i.com_num
        try:
            if num < task_info.task_time and str(user_task.tid) != tid:
                new_user_task = User_task(task_name=task_info.task_name, name=name, re_phone=re_phone,
                                          com_time=now_time,
                                          tid=tid, com_num=1)
                user_info.user_code += task_info.task_num
                db.session.add(new_user_task)
                db.session.commit()
            else:
                pass
        except:
            new_user_task = User_task(task_name=task_info.task_name, name=name, re_phone=re_phone, com_time=now_time,
                                      tid=tid, com_num=1)
            db.session.add(new_user_task)
            db.session.commit()
    else:
        user_task = User_task.query.filter(and_(User_task.task_name == task_info.task_name, User_task.name == name,
                                                User_task.re_phone == re_phone, User_task.tid == tid,
                                                User_task.com_time.between(now, now_time))).first()
        if user_task:
            db.session.delete(user_task)
            db.session.commit()
            user_info.user_code -= task_info.task_num
        else:
            new_user_task = User_task(task_name=task_info.task_name, name=name, re_phone=re_phone, com_time=now_time,
                                      tid=tid, com_num=-1)
            db.session.add(new_user_task)
            db.session.commit()

    result = {'status': 0, 'message': '成功'}
    return jsonify(result)


# app收藏中心
@app.route('/col_center', methods=['GET', 'POST'])
def col_center():
    col_info_show = []
    # data = request.get_data()
    # data = get_message(data)
    name = request.form.get('name')
    re_phone = request.form.get('re_phone')
    page_num = request.form.get('page_num')
    page_size = request.form.get('page_size')
    key_word = request.form.get('key_word')
    if not key_word:
        col_info = User_col.query.order_by(text('-col_time')).filter(
            and_(User_col.name == name, User_col.re_phone == re_phone)).all()[
                   ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        col_info1 = User_col.query.filter(and_(User_col.name == name, User_col.re_phone == re_phone)).all()
        for b in col_info:
            c = {}
            try:
                art_info = Art_info.query.filter(Art_info.id == b.art_id).first()
                c['art_title'] = art_info.art_title
                art_text = deal_html(art_info.art_cont)
                c['art_cont'] = art_text[0:-1]
                if c['art_cont']:
                    c['art_conts'] = c['art_cont'][0][0]
                else:
                    c['art_conts'] = ''
                c['local_time'] = str(art_info.local_time)
                c['username'] = art_info.cname
                c['id'] = art_info.id
                col_info_show.append(c)
            except:
                continue
        result = {'status': 0, 'message': '成功', 'total': len(col_info1)}
        result['data'] = col_info_show
        return jsonify(result)
    else:
        art_info = Art_info.query.filter(Art_info.art_title.like(f'%{key_word}%')).all()
        col_info = User_col.query.filter(and_(User_col.name == name, User_col.re_phone == re_phone)).all()
        total = 0
        for i in art_info:
            c = {}
            for j in col_info:
                if i.id == j.art_id:
                    total += 1
                    c['art_title'] = i.art_title
                    art_text = deal_html(i.art_cont)
                    c['art_cont'] = art_text[0:-1]
                    if c['art_cont']:
                        c['art_conts'] = c['art_cont'][0][0]
                    else:
                        c['art_conts'] = ''
                    c['local_time'] = str(i.local_time)
                    c['username'] = i.cname
                    c['id'] = i.id
                    col_info_show.append(c)
                else:
                    continue
        result = {'status': 0, 'message': '成功', 'total': total}
        result['data'] = col_info_show
        return jsonify(result)


# app版本信息
@app.route('/grade_info', methods=['GET', 'POST'])
def grade_info():
    try:
        file_name = '../apps/update.json'
        with open(file_name, encoding='utf-8') as f:
            info = json.load(f)
        result = {'status': 0, 'message': '成功', 'data': info}
    except:
        result = {'status': 1, 'message': '获取版本信息出错'}
    return jsonify(result)


# app退出登录
@app.route('/login_out', methods=['GET', 'POST'])
def login_out():
    id = request.form.get('id')
    user_info = User.query.filter(User.id == id).first()
    if user_info.zt == '0':
        user_info.zt = '0'
    else:
        user_info.zt = '1'
    db.session.commit()
    session['token'] = ""
    result = {'status': 0, 'message': '退出登录'}
    return jsonify(result)


# app就业信息搜索
@app.route('/search_cominfo', methods=['GET', 'POST'])
def search_cominfo():
    key_word = request.form.get('key_word')
    pn = request.form.get('pn')
    size = request.form.get('size')
    com_info_show = []
    if not key_word:
        key_word = None
    com_info = Com_info.query.filter(
        and_(or_(Com_info.com_name.like("%{com_name}%".format(com_name=key_word)),
                 Com_info.com_job.like("%{com_job}%".format(com_job=key_word))),
             Com_info.zt == 1)).all()[((int(pn) - 1) * int(size)):int(pn) * int(size)]
    if not com_info:
        result = {'status': 0, 'message': '搜索为空', 'data': []}
        return jsonify(result)
    else:
        for info in com_info:
            c = {}
            c["com_job"] = info.com_job
            c["com_name"] = info.com_name
            c["com_pay"] = info.com_pay
            c["com_respon"] = info.com_respon
            c["id"] = info.id
            c["time"] = str(info.local_time)
            com_info_show.append(c)
        result = {'status': 0, 'message': '成功', 'data': com_info_show}
        return jsonify(result)


# pc_登录
@app.route('/pc_login', methods=['GET', 'POST'])
def pc_login():
    # data = request.get_data()
    # data = get_message(data)
    sys_name = request.form.get('sys_name')
    password = request.form.get('password')
    db.reflect()
    # print(PC_user.query.filter(PC_user.sys_name == sys_name).first())
    try:
        user_info = PC_user.query.filter(PC_user.sys_name == sys_name).first()
        if user_info:
            user_password = user_info.password
        else:
            result = {'status': 1, 'message': '无此账号'}
            return jsonify(result)
    except:
        result = {'status': 1, 'message': '用户名或密码错误'}
        return jsonify(result)
    user_password = user_info.password
    md5 = hashlib.md5()
    md5.update(password.encode())
    password_h = md5.hexdigest()
    if password_h == user_password:
        name = user_info.name
        id = user_info.id
        token = make_token(name, re_phone=0)
        if user_info.zt == '2':
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            user_info.reg_time = now
            db.session.commit()
            result = {'status': 0, 'message': '成功', 'data': {'token': token, 'name': name, 'id': id}}
            return jsonify(result)
        else:
            result = {'status': 1, 'message': '账户已被停用'}
            return jsonify(result)
    else:
        result = {'status': 1, 'message': '用户名或密码错误'}
        return jsonify(result)


# pc_app用户管理
@app.route('/page1', methods=['GET', 'POST'])
def yhgl_solution():
    name = request.form.get('name')
    if not name:
        name = None
    id_code = request.form.get('id_code')
    if not id_code:
        id_code = None
    re_phone = request.form.get('re_phone')
    if not re_phone:
        re_phone = None
    zt = request.form.get('zt')
    if not zt:
        zt = None
    if zt == '1':
        zt = '2'
    page_num = request.form.get('page_num')
    page_size = request.form.get('page_size')
    db.reflect()
    user_info_show = []
    if name and id_code and re_phone and zt:
        if zt == 0 or zt == 1:
            info = User.query.filter(
                and_(User.name.like("%{name}%".format(name=name)),
                     User.id_code.like("%{id_code}%".format(id_code=id_code)),
                     User.re_phone.like("%{name}%".format(name=name)), or_(User.zt == 0, User.zt == 1))).all()[
                   ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
            total = len(info)
        else:
            info = User.query.filter(
                and_(User.name.like("%{name}%".format(name=name)),
                     User.id_code.like("%{id_code}%".format(id_code=id_code)),
                     User.re_phone.like("%{name}%".format(name=name)), User.zt == zt)).all()[
                   ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
            total = len(info)
        if info:
            for c in info:
                b = {}
                b['name'] = c.name
                b['id_code'] = c.id_code
                b['re_phone'] = c.re_phone
                b['zt'] = c.zt
                b['local_time'] = str(c.local_time)
                user_info_show.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = user_info_show
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    elif (name and id_code and re_phone) or (name and id_code and zt) or (name and re_phone and zt) or (
            id_code and re_phone and zt):
        if zt == '1' or zt == '0':
            info = User.query.filter(
                or_(and_(User.name.like("%{name}%".format(name=name)),
                         User.id_code.like("%{id_code}%".format(id_code=id_code)),
                         User.re_phone.like("%{re_phone}%".format(re_phone=re_phone))),
                    and_(User.name.like("%{name}%".format(name=name)),
                         User.id_code.like("%{id_code}%".format(id_code=id_code)), or_(User.zt == '0', User.zt == '1')),
                    and_(User.name.like("%{name}%".format(name=name)),
                         User.re_phone.like("%{re_phone}%".format(re_phone=re_phone)),
                         or_(User.zt == '0', User.zt == '1')),
                    and_(User.re_phone.like("%{re_phone}%".format(re_phone=re_phone)),
                         User.id_code.like("%{id_code}%".format(id_code=id_code)),
                         or_(User.zt == '0', User.zt == '1')))).all()[
                   ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
            total = len(info)
        else:
            info = User.query.filter(
                or_(and_(User.name.like("%{name}%".format(name=name)),
                         User.id_code.like("%{id_code}%".format(id_code=id_code)),
                         User.re_phone.like("%{re_phone}%".format(re_phone=re_phone))),
                    and_(User.name.like("%{name}%".format(name=name)),
                         User.id_code.like("%{id_code}%".format(id_code=id_code)), User.zt == zt),
                    and_(User.name.like("%{name}%".format(name=name)),
                         User.re_phone.like("%{re_phone}%".format(re_phone=re_phone)), User.zt == zt),
                    and_(User.re_phone.like("%{re_phone}%".format(re_phone=re_phone)),
                         User.id_code.like("%{id_code}%".format(id_code=id_code)),
                         User.zt == zt))).all()[
                   ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
            total = len(info)
        if info:
            for c in info:
                b = {}
                b['name'] = c.name
                b['id_code'] = c.id_code
                b['re_phone'] = c.re_phone
                b['zt'] = c.zt
                b['local_time'] = str(c.local_time)
                user_info_show.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = user_info_show
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    elif (name and id_code) or (name and re_phone) or (name and zt) or (id_code and re_phone) or (
            id_code and zt) or (re_phone and zt):
        if zt == '1' or zt == '2':
            info = User.query.filter(
                or_(and_(User.name.like("%{name}%".format(name=name)),
                         User.id_code.like("%{id_code}%".format(id_code=id_code))),
                    and_(User.name.like("%{name}%".format(name=name)),
                         User.re_phone.like("%{re_phone}%".format(re_phone=re_phone))),
                    and_(User.name.like("%{name}%".format(name=name)), or_(User.zt == '0', User.zt == '1')),
                    and_(User.re_phone.like("%{re_phone}%".format(re_phone=re_phone)),
                         User.id_code.like("%{id_code}%".format(id_code=id_code))),
                    and_(User.id_code.like("%{id_code}%".format(id_code=id_code)), or_(User.zt == '0', User.zt == '1')),
                    and_(User.re_phone.like("%{re_phone}%".format(re_phone=re_phone)),
                         or_(User.zt == '0', User.zt == '1')))).all()[
                   ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
            total = len(info)
        else:
            info = User.query.filter(
                or_(and_(User.name.like("%{name}%".format(name=name)),
                         User.id_code.like("%{id_code}%".format(id_code=id_code))),
                    and_(User.name.like("%{name}%".format(name=name)),
                         User.re_phone.like("%{re_phone}%".format(re_phone=re_phone))),
                    and_(User.name.like("%{name}%".format(name=name)), User.zt == zt),
                    and_(User.re_phone.like("%{re_phone}%".format(re_phone=re_phone)),
                         User.id_code.like("%{id_code}%".format(id_code=id_code))),
                    and_(User.id_code.like("%{id_code}%".format(id_code=id_code)), User.zt == zt),
                    and_(User.re_phone.like("%{re_phone}%".format(re_phone=re_phone)), User.zt == zt))).all()[
                   ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
            total = len(info)
        if info:
            for c in info:
                b = {}
                b['name'] = c.name
                b['id_code'] = c.id_code
                b['re_phone'] = c.re_phone
                b['zt'] = c.zt
                b['local_time'] = str(c.local_time)
                user_info_show.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = user_info_show
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    elif name or id_code or re_phone or zt:
        if zt == '0' or zt == '1':
            info = User.query.filter(
                or_(User.name.like("%{name}%".format(name=name)),
                    User.id_code.like("%{id_code}%".format(id_code=id_code)),
                    User.re_phone.like("%{re_phone}%".format(re_phone=re_phone)),
                    or_(User.zt == '0', User.zt == '1'))).all()[
                   ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
            total = len(info)
        else:
            info = User.query.filter(
                or_(User.name.like("%{name}%".format(name=name)),
                    User.id_code.like("%{id_code}%".format(id_code=id_code)),
                    User.re_phone.like("%{re_phone}%".format(re_phone=re_phone)),
                    User.zt == zt)).all()[
                   ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
            total = len(info)
        if info:
            for c in info:
                b = {}
                b['name'] = c.name
                b['id_code'] = c.id_code
                b['re_phone'] = c.re_phone
                b['zt'] = c.zt
                b['local_time'] = str(c.local_time)
                user_info_show.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = user_info_show
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    else:
        if not (page_num and page_size):
            page_num = 1
            page_size = 10
            all_data = User.query.order_by(text('-local_time'))[
                       ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        else:
            all_data = User.query.order_by(text('-local_time'))[
                       ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        for data in all_data:
            c = {}
            c['name'] = data.name
            c['id_code'] = data.id_code
            c['re_phone'] = data.re_phone
            c['zt'] = data.zt
            c['local_time'] = str(data.local_time)
            user_info_show.append(c)
        data_total = User.query.order_by(text('-local_time')).count()
        result = {'status': 0, 'message': '成功', 'total': data_total}
        result['data'] = user_info_show
        return jsonify(result)


# pc_app用户停用与启用
@app.route('/page1/user_enable', methods=['GET', 'POST'])
def user_enable():
    # data = request.get_data()
    # data = get_message(data)
    id_code = request.form.get('id_code')
    try:
        user_info = User.query.filter(User.id_code == id_code).first()
        if user_info.zt == '0':
            user_info.zt = '1'
        else:
            user_info.zt = '0'
        db.session.commit()
        result = {'status': 0, 'message': '成功'}
        return jsonify(result)
    except:
        print('数据出错')


# pc_app用户信息详情
@app.route('/page1/user_details', methods=['GET', 'POST'])
def user_details():
    user_info_show = []
    # data = request.get_data()
    # data = get_message(data)
    id_code = request.form.get('id_code')
    user_info = User.query.filter(User.id_code == id_code).first()
    local_time = user_info.local_time
    # print(local_time)
    c = {}
    c['username'] = user_info.username
    c['re_phone'] = user_info.re_phone
    c['name'] = user_info.name
    c['id_code'] = user_info.id_code
    c['local_time'] = str(local_time)
    c['register_time'] = str(user_info.register_time)
    c['user_code'] = user_info.user_code
    user_info_show.append(c)
    result = {'status': 0, 'message': '成功'}
    result['data'] = user_info_show
    return jsonify(result)


# pc_弹窗显示
@app.route('/info_show', methods=['GET', 'POST'])
def info_show():
    id = request.form.get('id')
    user_info = PC_user.query.filter(PC_user.id == id).first()
    c = {}
    c['sys_name'] = user_info.sys_name
    c['reg_time'] = str(user_info.reg_time)
    result = {'status': 0, 'message': '成功'}
    result['data'] = c
    return jsonify(result)


# pc_弹窗修改密码
@app.route('/info_change', methods=['GET', 'POST'])
def info_change():
    id = request.form.get('id')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    user_info = PC_user.query.filter(PC_user.id == id).first()
    if old_password != user_info.password:
        result = {'status': 1, 'message': '原始密码输入错误'}
        return jsonify(result)
    else:
        user_info.password = new_password
        db.session.commit()
        result = {'status': 0, 'message': '修改成功'}
        return jsonify(result)


# pc_积分商城的展示与查询
@app.route('/pagea', methods=['GET', 'POST'])
def app_solution():
    pro_name = request.form.get('pro_name')
    if not pro_name:
        pro_name = None
    name = request.form.get('name')
    if not name:
        name = None
    page_num = request.form.get('page_num')
    page_size = request.form.get('page_size')
    db.reflect()
    pro_info_show = []
    if pro_name and name:
        info = Pro_info.query.filter(and_(Pro_info.pro_name.like("%{pro_name}%".format(pro_name=pro_name)),
                                          Pro_info.name.like("%{name}%".format(name=name)))).all()[
               ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        if info:
            total = Pro_info.query.filter(and_(Pro_info.pro_name.like("%{pro_name}%".format(pro_name=pro_name)),
                                               Pro_info.name.like("%{name}%".format(name=name)))).count()
            for c in info:
                b = {}
                b['id'] = c.id
                b['pro_name'] = c.pro_name
                b['pro_code'] = c.pro_code
                b['create_time'] = str(c.create_time)
                b['name'] = c.name
                # c['pro_info'] = data.pro_info
                pro_info_show.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = pro_info_show
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    elif pro_name or name:
        info = Pro_info.query.filter(or_(Pro_info.pro_name.like("%{pro_name}%".format(pro_name=pro_name)),
                                         Pro_info.name.like("%{name}%".format(name=name)))).all()[
               ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        if info:
            total = Pro_info.query.filter(or_(Pro_info.pro_name.like("%{pro_name}%".format(pro_name=pro_name)),
                                              Pro_info.name.like("%{name}%".format(name=name)))).count()
            for c in info:
                b = {}
                b['id'] = c.id
                b['pro_name'] = c.pro_name
                b['pro_code'] = c.pro_code
                b['create_time'] = str(c.create_time)
                b['name'] = c.name
                # c['pro_info'] = data.pro_info
                pro_info_show.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = pro_info_show
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    else:
        if not (page_size and page_num):
            page_num = 1
            page_size = 10
            all_data = Pro_info.query.order_by(text("-create_time"))[
                       ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        else:
            all_data = Pro_info.query.order_by(text("-create_time"))[
                       ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        for data in all_data:
            c = {}
            c['id'] = data.id
            c['pro_name'] = data.pro_name
            c['pro_code'] = data.pro_code
            c['create_time'] = str(data.create_time)
            c['name'] = data.name
            # c['pro_info'] = data.pro_info
            pro_info_show.append(c)
        data_total = Pro_info.query.order_by(text("-create_time")).count()
        result = {'status': 0, 'message': '成功', 'total': data_total}
        result['data'] = pro_info_show
        return jsonify(result)


# pc_商品信息详情
@app.route('/pagea/pro_details', methods=['GET', 'POST'])
def pro_details():
    pro_info_show = []
    name = request.form.get('name')
    create_time = request.form.get('create_time')
    id = request.form.get('id')
    pro_info = Pro_info.query.filter(Pro_info.id == id).first()
    db.reflect()
    c = {}
    c['pro_name'] = pro_info.pro_name
    c['pro_code'] = pro_info.pro_code
    c['pro_text'] = pro_info.pro_text
    c['img_url'] = pro_info.img_url
    c['create_time'] = str(pro_info.create_time)
    c['name'] = pro_info.name
    pro_info_show.append(c)
    result = {'status': 0, 'message': '成功'}
    result['data'] = pro_info_show
    return jsonify(result)


# 图片处理
@app.route('/get_picture', methods=['GET', 'POST'])
def get_picture():
    img_file = request.files['img_file'].read()
    try:
        files = {'file': ('image.jpg', img_file)}
        weed_url1 = 'http://192.168.0.60:9333/dir/assign?ttl=3M'  # weed存储地址
        weed_url2 = 'http://192.168.0.60:9081/'
        weed_res1 = requests.post(weed_url1, {}, timeout=10)
        weed_res1 = weed_res1.json()
        weed_res2 = requests.post(weed_url2 + weed_res1['fid'], files=files, timeout=10)
        kt_img_url = weed_res1['publicUrl'] + weed_res1['fid'] + '.jpg'
        result = {'status': 0, 'message': '成功', 'data': {'url': kt_img_url}}
        return jsonify(result)
    except (Exception) as e:
        logging.exception("图片存weed错误:%s", str(e))
        return 'error'
    # img_name = img_file.filename
    # basedir = os.path.abspath(os.path.dirname(__file__))
    # path = basedir + '\imgs\\'
    # splittname = os.path.splitext(img_name)[0]  # # 文件名
    # print(splittname)
    # tsuffix = os.path.splitext(img_name)[1]  # # 后缀
    # splittname = int(time.time()) + random.randint(0, 99999)
    # print(splittname)
    # img_name = str(splittname) + tsuffix
    # img_path = path + img_name
    # img_file.save(img_path)
    # img_url = '\imgs\\' + img_name
    # print(basedir, path, img_url)
    # return "ok"


# pc_商品信息编辑
@app.route('/pagea/pro_edit', methods=['GET', 'POST'])
def pro_edit():
    pro_info_show = []
    # data = request.get_data()
    # data = get_message(data)
    name = request.form.get('name')
    create_time = request.form.get('create_time')
    id = request.form.get('id')
    pro_info = Pro_info.query.filter(Pro_info.id == id).first()
    db.reflect()
    c = {}
    c['pro_name'] = pro_info.pro_name
    c['pro_code'] = pro_info.pro_code
    c['pro_text'] = pro_info.pro_text
    c['img_url'] = pro_info.img_url
    pro_info_show.append(c)
    result = {'status': 0, 'message': '成功'}
    result['data'] = c
    return jsonify(result)


# pc_商品兑换的展示与查询
@app.route('/jf_page/pro_change', methods=['GET', 'POST'])
def pro_change():
    name = request.form.get('name')
    if not name:
        name = None
    pro_name = request.form.get('pro_name')
    if not pro_name:
        pro_name = None
    tra_num = request.form.get('tra_num')
    if not tra_num:
        tra_num = None
    page_num = request.form.get('page_num')
    page_size = request.form.get('page_size')
    db.reflect()
    pro_info_show = []
    if name and pro_name and tra_num:
        info = Pro_change.query.filter(
            and_(Pro_change.like("%{name}%".format(name=name)),
                 Pro_change.pro_name.like("%{pro_name}%".format(pro_name=pro_name)),
                 Pro_change.tra_num.like("%{tra_num}%".format(tra_num=tra_num)))).all()[
               ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        if info:
            total = Pro_change.query.filter(
                and_(Pro_change.like("%{name}%".format(name=name)),
                     Pro_change.pro_name.like("%{pro_name}%".format(pro_name=pro_name)),
                     Pro_change.tra_num.like("%{tra_num}%".format(tra_num=tra_num)))).count()
            for c in info:
                b = {}
                b['id'] = c.id
                b['pro_name'] = c.pro_name
                b['name'] = c.name
                b['add_pho'] = c.add_pho
                b['tra_num'] = c.tra_num
                pro_info_show.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = pro_info_show
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    elif (name and pro_name) or (name and tra_num) or (pro_name and tra_num):
        info = Pro_change.query.filter(or_(and_(Pro_change.name.like("%{name}%".format(name=name)),
                                                Pro_change.pro_name.like("%{pro_name}%".format(pro_name=pro_name))),
                                           and_(Pro_change.name.like("%{name}%".format(name=name)),
                                                Pro_change.tra_num.like("%{tra_num}%".format(tra_num=tra_num))),
                                           and_(Pro_change.pro_name.like("%{pro_name}%".format(pro_name=pro_name)),
                                                Pro_change.tra_num.like("%{tra_num}%".format(tra_num=tra_num))))).all()[
               ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        if info:
            total = Pro_change.query.filter(or_(and_(Pro_change.name.like("%{name}%".format(name=name)),
                                                     Pro_change.pro_name.like(
                                                         "%{pro_name}%".format(pro_name=pro_name))),
                                                and_(Pro_change.name.like("%{name}%".format(name=name)),
                                                     Pro_change.tra_num.like("%{tra_num}%".format(tra_num=tra_num))),
                                                and_(Pro_change.pro_name.like("%{pro_name}%".format(pro_name=pro_name)),
                                                     Pro_change.tra_num.like(
                                                         "%{tra_num}%".format(tra_num=tra_num))))).count()
            for c in info:
                b = {}
                b['id'] = c.id
                b['pro_name'] = c.pro_name
                b['name'] = c.name
                b['add_pho'] = c.add_pho
                b['tra_num'] = c.tra_num
                pro_info_show.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = pro_info_show
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    elif name or pro_name or tra_num:
        info = Pro_change.query.filter(
            or_(Pro_change.name.like(f"%{name}%"),
                Pro_change.pro_name.like(f"%{pro_name}%"),
                Pro_change.tra_num.like(f"%{tra_num}%"))).all()[
               ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        if info:
            total = Pro_change.query.filter(
                or_(Pro_change.name.like(f"%{name}%"),
                    Pro_change.pro_name.like(f"%{pro_name}%"),
                    Pro_change.tra_num.like(f"%{tra_num}%"))).count()
            for c in info:
                b = {}
                b['id'] = c.id
                b['pro_name'] = c.pro_name
                b['name'] = c.name
                b['add_pho'] = c.add_pho
                b['tra_num'] = c.tra_num
                pro_info_show.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = pro_info_show
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    else:
        if not (page_num and page_size):
            page_num = 1
            page_size = 5
            all_data = Pro_change.query.order_by(text("-c_time"))[
                       ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        else:
            all_data = Pro_change.query.order_by(text("-c_time")).all()[
                       ((int(page_num) - 1) * int(page_size)):(int(page_num) * int(page_size))]
        # print(all_data)
        for data in all_data:
            c = {}
            c['id'] = data.id
            c['pro_name'] = data.pro_name
            c['name'] = data.name
            c['c_time'] = str(data.c_time)
            c['add_pho'] = data.add_pho
            c['tra_num'] = data.tra_num
            pro_info_show.append(c)
        data_total = Pro_change.query.order_by(text("-c_time")).count()
        result = {'status': 0, 'message': '成功', 'total': data_total}
        result['data'] = pro_info_show
        return jsonify(result)


# pc_添加快递单号
@app.route('/jf_page/add_tra', methods=['GET', 'POST'])
def add_tra():
    # data = request.get_data()
    # data = get_message(data)
    tra_num = request.form.get('tra_num')
    name = request.form.get('name')
    c_time = request.form.get('c_time')
    id = request.form.get('id')
    order_info = Pro_change.query.filter(Pro_change.id == id).first()
    order_info.tra_num = tra_num
    db.session.commit()
    result = {'status': 0, 'message': '成功'}
    return jsonify(result)


# pc_积分商城的录入
@app.route('/pro_add', methods=["POST"])
def add_pro():
    # data = request.get_data()
    # data = get_message(data)
    pro_name = request.form.get('pro_name')
    pro_code = request.form.get('pro_code')
    pro_text = request.form.get('pro_text')
    name = request.form.get('name')
    p_text = deal_html(pro_text)[-1]
    img_url = '**'.join(p_text)
    id = request.form.get('id')
    create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if id:
        pro_info = Pro_info.query.filter(Pro_info.id == id).first()
        pro_info.pro_name = pro_name
        pro_info.pro_code = pro_code
        pro_info.pro_text = pro_text
        pro_info.img_url = img_url
        db.session.commit()
        result = {'status': 0, 'message': '编辑成功'}
        return jsonify(result)
    else:
        old_pro_name = Pro_info.query.filter(Pro_info.pro_name == pro_name).first()
        if not old_pro_name:
            pro = Pro_info(pro_name=pro_name, pro_code=pro_code, name=name, create_time=create_time, pro_text=pro_text,
                           img_url=img_url)
            db.session.add(pro)
            db.session.commit()
            result = {"status": 0, 'message': '新建成功'}
            return jsonify(result)
        else:
            result = {'status': 1, "error": "该商品已存在", 'data': []}
            return jsonify(result)


# pc_就业信息展示与查询
@app.route('/page4', methods=['GET', 'POST'])
def employ_solution():
    # if request.method == 'GET':
    #     com_info_show = []
    #     db.reflect()
    #     all_data = Com_info.query.order_by(text('-local_time'))
    #     for data in all_data:
    #         c = {}
    #         c['com_name'] = data.com_name  # 企业名称
    #         # c['com_introduce'] = data.com_introduce  # 企业介绍
    #         # c['com_welfare'] = data.com_welfare  # 公司福利
    #         c['com_job'] = data.com_job  # 岗位
    #         # c['com_respon'] = data.com_respon  # 岗位职责
    #         # c['job_require'] = data.job_require  # 任职要求
    #         c['com_pay'] = data.com_pay  # 薪资
    #         c['job_address'] = data.job_address  # 工作地址
    #         # c['com_contact'] = data.com_contact  # 联系人
    #         # c['com_phone'] = data.com_phone  # 联系电话
    #         c['zt'] = data.zt  # 状态
    #         c['name'] = data.name  # 操作人
    #         c['local_time'] = str(data.local_time)  # 最近操作时间
    #         com_info_show.append(c)
    #     result = {'status': 0, 'message': '成功'}
    #     result['data'] = com_info_show
    #     return jsonify(result)
    # else:
    # # data = request.get_data()
    # # data = get_message(data)
    # print(data)
    com_name = request.form.get('com_name')
    if not com_name:
        com_name = None
    com_job = request.form.get('com_job')
    if not com_job:
        com_job = None
    name = request.form.get('name')
    if not name:
        name = None
    start_time = request.form.get('start_time')
    if not start_time:
        start_time = None
    end_time = request.form.get('end_time')
    print(end_time)
    if not end_time:
        end_time = None
    else:
        end_time = time.strptime(end_time, "%Y-%m-%d")
        end_time = int(time.mktime(end_time))
        end_time += 86400
        end_time = time.localtime(end_time)
        end_time = time.strftime("%Y-%m-%d", end_time)
    page_size = request.form.get('page_size')
    page_num = request.form.get('page_num')
    com_info = []
    if com_name and com_job and name and start_time and end_time:
        info = Com_info.query.filter(and_(Com_info.com_name.like("%{com_name}%".format(com_name=com_name)),
                                          Com_info.com_job.like("%{com_job}%".format(com_job=com_job)),
                                          Com_info.name.like("%{name}%".format(name=name)),
                                          Com_info.local_time.between(start_time, end_time))).all()[
               ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        if info:
            total = Com_info.query.filter(and_(Com_info.com_name.like("%{com_name}%".format(com_name=com_name)),
                                               Com_info.com_job.like("%{com_job}%".format(com_job=com_job)),
                                               Com_info.name.like("%{name}%".format(name=name)),
                                               Com_info.local_time.between(start_time, end_time))).count()
            for c in info:
                b = {}
                b['id'] = c.id
                b['com_name'] = c.com_name  # 企业名称
                b['com_job'] = c.com_job  # 岗位
                b['com_pay'] = c.com_pay  # 薪资
                b['job_address'] = c.job_address  # 工作地址
                b['zt'] = c.zt  # 状态
                b['name'] = c.name  # 操作人
                b['local_time'] = str(c.local_time)  # 最近操作时间
                com_info.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = com_info
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    elif (com_name and com_job and start_time and end_time) or (
            com_name and name and start_time and end_time) or (
            com_job and name and start_time and end_time) or (com_name and com_job and name):
        info = Com_info.query.filter(or_(and_(Com_info.com_name.like("%{com_name}%".format(com_name=com_name)),
                                              Com_info.com_job.like("%{com_job}%".format(com_job=com_job)),
                                              Com_info.local_time.between(start_time, end_time)),
                                         and_(Com_info.com_name.like("%{com_name}%".format(com_name=com_name)),
                                              Com_info.name.like("%{name}%".format(name=name)),
                                              Com_info.local_time.between(start_time, end_time)),
                                         and_(Com_info.com_job.like("%{com_job}%".format(com_job=com_job)),
                                              Com_info.name.like("%{name}%".format(name=name)),
                                              Com_info.local_time.between(start_time, end_time)),
                                         and_(Com_info.com_name.like("%{com_name}%".format(com_name=com_name)),
                                              Com_info.com_job.like("%{com_job}%".format(com_job=com_job)),
                                              Com_info.name.like("%{name}%".format(name=name))))).all()[
               ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        if info:
            total = Com_info.query.filter(or_(and_(Com_info.com_name.like("%{com_name}%".format(com_name=com_name)),
                                                   Com_info.com_job.like("%{com_job}%".format(com_job=com_job)),
                                                   Com_info.local_time.between(start_time, end_time)),
                                              and_(Com_info.com_name.like("%{com_name}%".format(com_name=com_name)),
                                                   Com_info.name.like("%{name}%".format(name=name)),
                                                   Com_info.local_time.between(start_time, end_time)),
                                              and_(Com_info.com_job.like("%{com_job}%".format(com_job=com_job)),
                                                   Com_info.name.like("%{name}%".format(name=name)),
                                                   Com_info.local_time.between(start_time, end_time)),
                                              and_(Com_info.com_name.like("%{com_name}%".format(com_name=com_name)),
                                                   Com_info.com_job.like("%{com_job}%".format(com_job=com_job)),
                                                   Com_info.name.like("%{name}%".format(name=name))))).count()
            for c in info:
                b = {}
                b['id'] = c.id
                b['com_name'] = c.com_name  # 企业名称
                b['com_job'] = c.com_job  # 岗位
                b['com_pay'] = c.com_pay  # 薪资
                b['job_address'] = c.job_address  # 工作地址
                b['zt'] = c.zt  # 状态
                b['name'] = c.name  # 操作人
                b['local_time'] = str(c.local_time)  # 最近操作时间
                com_info.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = com_info
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    elif (com_name and start_time and end_time) or (com_job and start_time and end_time) or (
            name and start_time and end_time) or (com_job and com_name) or (com_name and name) or (
            com_job and name):
        info = Com_info.query.filter(
            or_(and_(Com_info.com_name.like(f"%{com_name}%"),
                     Com_info.local_time.between(start_time, end_time)),
                and_(Com_info.com_job.like(f"%{com_job}%"),
                     Com_info.local_time.between(start_time, end_time)),
                and_(Com_info.name.like(f"%{name}%"),
                     Com_info.local_time.between(start_time, end_time)),
                and_(Com_info.name.like(f"%{name}%"),
                     Com_info.com_name.like(f"%{com_name}%")),
                and_(Com_info.com_name.like(f"%{com_name}%"),
                     Com_info.com_job.like(f"%{com_job}%")),
                and_(Com_info.com_job.like(f"%{com_job}%"),
                     Com_info.name.like(f"%{name}%")))).all()[
               ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        if info:
            # print(info)
            total = Com_info.query.filter(
                or_(and_(Com_info.com_name.like(f"%{com_name}%"),
                         Com_info.local_time.between(start_time, end_time)),
                    and_(Com_info.com_job.like(f"%{com_job}%"),
                         Com_info.local_time.between(start_time, end_time)),
                    and_(Com_info.name.like(f"%{name}%"),
                         Com_info.local_time.between(start_time, end_time)),
                    and_(Com_info.name.like(f"%{name}%"),
                         Com_info.com_name.like(f"%{com_name}%")),
                    and_(Com_info.com_name.like(f"%{com_name}%"),
                         Com_info.com_job.like(f"%{com_job}%")),
                    and_(Com_info.com_job.like(f"%{com_job}%"),
                         Com_info.name.like(f"%{name}%")))).count()
            for c in info:
                b = {}
                b['id'] = c.id
                b['com_name'] = c.com_name  # 企业名称
                b['com_job'] = c.com_job  # 岗位
                b['com_pay'] = c.com_pay  # 薪资
                b['job_address'] = c.job_address  # 工作地址
                b['zt'] = c.zt  # 状态
                b['name'] = c.name  # 操作人
                b['local_time'] = str(c.local_time)  # 最近操作时间
                com_info.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = com_info
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    elif (start_time and end_time) or com_job or com_name or name:
        info = Com_info.query.filter(
            or_(Com_info.local_time.between(start_time, end_time),
                Com_info.com_job.like(f"%{com_job}%"),
                Com_info.com_name.like(f"%{com_name}%"),
                Com_info.name.like(f"%{name}%"))).all()[
               ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        if info:
            total = Com_info.query.filter(
                or_(Com_info.local_time.between(start_time, end_time),
                    Com_info.com_job.like(f"%{com_job}%"),
                    Com_info.com_name.like(f"%{com_name}%"),
                    Com_info.name.like(f"%{name}%"))).count()
            for c in info:
                b = {}
                b['id'] = c.id
                b['com_name'] = c.com_name  # 企业名称
                b['com_job'] = c.com_job  # 岗位
                b['com_pay'] = c.com_pay  # 薪资
                b['job_address'] = c.job_address  # 工作地址
                b['zt'] = c.zt  # 状态
                b['name'] = c.name  # 操作人
                b['local_time'] = str(c.local_time)  # 最近操作时间
                com_info.append(b)
            result = {'status': 0, 'message': '成功', 'total': total}
            result['data'] = com_info
            return jsonify(result)
        else:
            result = {'status': 0, 'message': '成功', 'total': 0, 'data': []}
            return jsonify(result)
    else:
        if not (page_num and page_size):
            page_num = 1
            page_size = 10
            all_data = Com_info.query.order_by(text('-local_time'))[
                       ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        else:
            all_data = Com_info.query.order_by(text('-local_time'))[
                       ((int(page_num) - 1) * int(page_size)):int(page_num) * int(page_size)]
        # print(all_data)
        for data in all_data:
            c = {}
            c['id'] = data.id
            c['com_name'] = data.com_name  # 企业名称
            c['com_job'] = data.com_job  # 岗位
            c['com_pay'] = data.com_pay  # 薪资
            c['job_address'] = data.job_address  # 工作地址
            c['zt'] = data.zt  # 状态
            c['name'] = data.name  # 操作人
            c['local_time'] = str(data.local_time)  # 最近操作时间
            com_info.append(c)
        data_total = Com_info.query.order_by(text('-local_time')).count()
        result = {'status': 0, 'message': '成功', 'total': data_total}
        result['data'] = com_info
        return jsonify(result)


# pc_就业信息的发布功能
@app.route('/page4/job_release', methods=['GET', 'POST'])
def job_release():
    # data = request.get_data()
    # data = get_message(data)
    name = request.form.get('name')
    local_time = request.form.get('local_time')
    id = request.form.get('id')
    com_info = Com_info.query.filter(Com_info.id == id).first()
    com_info.zt = '1'
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    com_info.local_time = now_time
    db.session.commit()
    result = {'status': 0, 'message': '成功'}
    return jsonify(result)


# pc_就业信息删除
@app.route('/page4/job_delete', methods=['GET', 'POST'])
def job_delete():
    # data = request.get_data()
    # data = get_message(data)
    name = request.form.get('name')
    local_time = request.form.get('local_time')
    id = request.form.get('id')
    com_info = Com_info.query.filter(Com_info.id == id).first()
    db.session.delete(com_info)
    db.session.commit()
    result = {'status': 0, 'message': '成功'}
    return jsonify(result)


# pc_就业信息编辑
@app.route('/page4/job_edit', methods=['GET', 'POST'])
def job_edit():
    job_info_show = []
    # data = request.get_data()
    # data = get_message(data)
    name = request.form.get('name')
    local_time = request.form.get('local_time')
    id = request.form.get('id')
    com_info = Com_info.query.filter(Com_info.id == id).first()
    # print(com_info)
    c = {}
    c['com_name'] = com_info.com_name  # 企业名称
    c['com_introduce'] = com_info.com_introduce  # 企业介绍
    c['com_welfare'] = com_info.com_welfare  # 公司福利
    c['com_job'] = com_info.com_job  # 岗位
    c['com_respon'] = com_info.com_respon  # 岗位职责
    c['job_require'] = com_info.job_require  # 任职要求
    c['com_pay'] = com_info.com_pay  # 薪资
    c['job_address'] = com_info.job_address  # 工作地址
    c['com_contact'] = com_info.com_contact  # 联系人
    c['com_phone'] = com_info.com_phone  # 联系电话
    job_info_show.append(c)
    result = {'status': 0, 'message': '成功'}
    result['data'] = job_info_show
    return jsonify(result)


# pc_新建招聘
@app.route('/page14', methods=['GET', 'POST'])
def new_recruitment():
    # if request.method == 'GET':
    #     author = request.myuser
    #     print(author.name)
    #     result = {'status': 0, 'message': '成功'}
    #     return jsonify(result)
    # else:
    # data = request.get_data()
    # data = get_message(data)
    # print(data)
    id = request.form.get('id')
    com_name = request.form.get('com_name')
    com_introduce = request.form.get('com_introduce')
    com_welfare = request.form.get('com_welfare')
    com_job = request.form.get('com_job')
    com_respon = request.form.get('com_respon')
    job_require = request.form.get('job_require')
    com_pay = request.form.get('com_pay')
    job_address = request.form.get('job_address')
    com_contact = request.form.get('com_contact')
    com_phone = request.form.get('com_phone')
    name = request.form.get('name')
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db.reflect()
    if not id:
        work = Com_info(com_name=com_name, com_introduce=com_introduce, com_welfare=com_welfare, com_job=com_job,
                        com_respon=com_respon,
                        job_require=job_require, com_pay=com_pay, job_address=job_address, com_contact=com_contact,
                        com_phone=com_phone, zt=0, name=name, local_time=now_time)
        db.session.add(work)
        db.session.commit()
        result = {'status': 0, 'message': '新建成功'}
        return jsonify(result)
    else:
        work_info = Com_info.query.filter(Com_info.id == id).first()
        # print(work_info.com_name)
        work_info.com_name = com_name
        work_info.com_introduce = com_introduce
        work_info.com_welfare = com_welfare
        work_info.com_job = com_job
        work_info.com_respon = com_respon
        work_info.job_require = job_require
        work_info.com_pay = com_pay
        work_info.job_address = job_address
        work_info.com_contact = com_contact
        work_info.com_phone = com_phone
        work_info.local_time = now_time
        db.session.commit()
        result = {'status': 0, 'message': '编辑成功'}
        return jsonify(result)


# token令牌生成
def make_token(name, re_phone, now, expire=600):
    key = '123456'
    now = time.time()
    payload = {'name': name, 're_phone': re_phone, 'now': now, 'exp': now + expire}
    return jwt.encode(payload, key, algorithm='HS256')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
