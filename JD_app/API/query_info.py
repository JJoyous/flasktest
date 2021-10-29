from model import *

query_info = Blueprint('query_info', __name__)


# 查询小铃铛
@query_info.route('/info_xld', methods=['POST'])
def info_xld():
    uid = request.form.get('uid')  # 用户id
    res = sql_xld(uid)
    return res


# 通知详情
@query_info.route('/info_xld_xx', methods=['POST'])
def info_xld_xx():
    info_id = request.form.get('info_id')  # 通知信息id
    res = sql_xld_xx(info_id)
    return res


# 搜索框
@query_info.route('/info_sear', methods=['POST'])
def info_sear():
    sear_key = request.form.get('sear_key')
    uid = request.form.get('uid')
    pn = request.form.get('pn')
    size = request.form.get('size')
    res = sql_sear(sear_key, uid, pn, size)
    return res


# 文章详细页面
@query_info.route('/info_sear_id', methods=['POST'])
def info_sear_id():
    art_id = request.form.get('id')
    uid = request.form.get('uid')
    res = sql_sear_art(art_id, uid)
    return res


# 1点赞、2评论、3分享、4收藏
@query_info.route('/info_com_type', methods=['POST'])
def info_com_type():
    art_id = request.form.get('id')
    uid = request.form.get('uid')
    art_tit = request.form.get('art_tit')
    op_type = request.form.get('type')
    if op_type == "1":
        col = request.form.get('col')
        sql_like(col, art_id, uid, art_tit)
    elif op_type == "2":
        art = request.form.get('art')
        res = sql_com_ins(art_id, uid, art)
        return res
    elif op_type == "3":
        sql_add("share", art_id)
    elif op_type == "4":
        col = request.form.get('col')
        sql_col(col, art_id, uid)
    return stand([])


# 切换标题类型
@query_info.route('/info_type', methods=['POST'])
def info_type():
    # data = request.get_data()
    # data = get_message(data)
    art_type = request.form.get('art_type')
    uid = request.form.get('uid')
    pn = request.form.get('pn')
    size = request.form.get('size')
    res = sql_info_type(art_type, uid, pn, size)
    return res


# 轮播图
@query_info.route('/type_img', methods=['POST'])
def type_img():
    art_type = request.form.get('art_type')
    res = info_type_img(art_type)
    return res


# 就业信息列表
@query_info.route('/info_com', methods=['POST'])
def info_com_list():
    pn = request.form.get('pn')
    size = request.form.get('size')
    res = sql_com_info(pn, size)
    return res


# 就业信息详情
@query_info.route('/info_com_id', methods=['POST'])
def info_com_id():
    # data = request.get_data()
    # data = get_message(data)
    job_id = request.form.get('id')
    res = sql_com_id(job_id)
    return res
