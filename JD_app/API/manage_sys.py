from model import *

manage_sys = Blueprint('manage_sys', __name__)


# 系统用户查询
@manage_sys.route('/sys', methods=['POST'])
def sys():
    name = request.form.get('name')
    sys_name = request.form.get('sys_name')
    tel_phone = request.form.get('tel_phone')
    pn = request.form.get('pn')
    size = request.form.get('size')
    res = sql_sys_search(name, sys_name, tel_phone, pn, size)
    return res


# 新建、编辑保存用户
@manage_sys.route('/sys_update', methods=['POST'])
def sys_update():
    name_id = request.form.get('id')
    name = request.form.get('name')
    sys_name = request.form.get('sys_name')
    password = request.form.get('password')
    tel_phone = request.form.get('tel_phone')
    res = sql_sys_update(name_id, name, sys_name, password, tel_phone)
    return res


# 删除用户
@manage_sys.route('/sys_delete', methods=['POST'])
def sys_delete():
    name_id = request.form.get('id')
    res = sql_sys_delete(name_id)
    return res


# 点击编辑
@manage_sys.route('/sys_edit', methods=['POST'])
def sys_edit():
    name_id = request.form.get("id")
    res = sql_sys_find(name_id)
    return res


# 启用，停用
@manage_sys.route('/zt', methods=['POST'])
def sys_zt():
    name_id = request.form.get("id")
    zt = request.form.get("zt")
    res = sql_sys_status(name_id, zt)
    return res

