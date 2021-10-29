from model import *

detection_hair = Blueprint('detection_hair', __name__)


# 毛发检测结果录入
@detection_hair.route('/hair_res', methods=['GET', 'POST'])
def hair_res():
    if request.method == 'GET':
        res = sql_hair()
        return res
    elif request.method == 'POST':
        uid = request.form.get('uid')
        hair_id = request.form.get('id')
        det_department = request.form.get('det_department')
        det_name = request.form.get('det_name')
        id_card = request.form.get('id_card')
        tel_phone = request.form.get('tel_phone')
        det_result = request.form.get('det_result')
        det_object = request.form.get('det_object')
        det_way = request.form.get('det_way')
        res = sql_ins_hair(uid, det_department, det_name, id_card, tel_phone, det_result, det_object, det_way, hair_id)

        return res


# 毛发检测结果查询
@detection_hair.route('/hair_inquire_res', methods=['GET', 'POST'])
def hair_res_list():
    uid = request.form.get('uid')  # 用户id
    hair_id = request.form.get('hair_id')  # 毛发检测结果id
    keywords = request.form.get('keywords')  # 关键字
    start_time = request.form.get('start_time')  # 开始时间
    end_time = request.form.get('end_time')  # 结束时间
    pn = request.form.get('pn')  # 页面
    size = request.form.get('size')  # 条数
    res = sql_hair_res(uid, hair_id, keywords, start_time, end_time, pn, size)
    return res


# 口令
@detection_hair.route('/generate_toke', methods=['GET', 'POST'])
def generate_toke():
    # 获取口令
    if request.method == 'GET':
        res = generate_token()
        return res
    # 验证口令
    elif request.method == 'POST':
        token = request.form.get('token')
        res = generate_token(token)
        return res


# 刷新口令
@detection_hair.route('/refresh', methods=['GET', 'POST'])
def refresh():
    redis_generate_token()
    res = generate_token()
    return res


# 获取H5地址与二维码
@detection_hair .route('/add_code', methods=['GET'])
def add_code():
    add = "http://192.168.0.46:8090/#/login"
    QR_code = "http://192.168.0.46:8089/upload/H5.png"
    return stand([add, QR_code])
