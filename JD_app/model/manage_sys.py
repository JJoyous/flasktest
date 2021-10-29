from model.config import *


# 系统用户查询
def sql_sys_search(name, sys_name, tel_phone, pn, size):
    # 模糊查询人员信息和数量，无条件则查询所有
    sql_data = "SELECT id, name, sys_name, tel_phone, zt FROM zz_operator WHERE id != ''"
    sql_sum = "SELECT count(id) sum FROM zz_operator WHERE id != ''"
    if name:
        sql_data += " AND name like '%{0}%'".format(name)
        sql_sum += " AND name like '%{0}%'".format(name)
    if sys_name:
        sql_data += " AND sys_name like '%{0}%'".format(sys_name)
        sql_sum += " AND sys_name like '%{0}%'".format(sys_name)
    if tel_phone:
        sql_data += " AND tel_phone like '%{0}%'".format(tel_phone)
        sql_sum += " AND tel_phone like '%{0}%'".format(tel_phone)
    sql_data += "ORDER BY reg_time DESC LIMIT {0},{1} ".format(int(size) * (int(pn) - 1), int(size))
    sys_data = execute_sql(sql_data)
    sys_sum = execute_sql(sql_sum)
    return stand(sys_data, '成功', sys_sum[0]["sum"], 0)


# 新建、编辑保存用户
def sql_sys_update(name_id, name, sys_name, password, tel_phone):
    # 当id存在时为更新用户
    if name_id:
        sql = "select password from zz_operator where id = {0}".format(name_id)
        pass_old = execute_sql(sql)[0]["password"]
        if password == pass_old:
            sql = "UPDATE zz_operator SET name = '{0}',sys_name = '{1}',password = '{2}',tel_phone = '{3}' WHERE id = {4} ".format(
                name, sys_name, password, tel_phone, name_id)
            execute_sql(sql, 'update')
        else:
            sql = "UPDATE zz_operator SET name = '{0}',sys_name = '{1}',password = '{2}',tel_phone = '{3}' WHERE id = {4} ".format(
                name, sys_name, str_md5(password), tel_phone, name_id)
            execute_sql(sql, 'update')
        return stand([])
    # 当id不存在时为新建用户
    else:
        sql = "SELECT sys_name FROM zz_operator WHERE sys_name = '{0}'".format(sys_name)
        sys_data = execute_sql(sql)
        # 判断是否存在同名的用户
        if sys_data:
            return stand([], "存在同名用户", 0, 1)
        else:
            sql = "INSERT INTO zz_user_info(name, username, password, re_phone, local_time, register_time, login_time) VALUES ('{0}','{1}','{2}','{3}',Now(),Now(),0)".format(
                name, sys_name, str_md5(password), tel_phone)
            uid = execute_sql(sql, 'insert')
            sql = "INSERT INTO zz_operator(name, sys_name, password, tel_phone, uid) VALUES ('{0}','{1}','{2}','{3}','{4}')".format(
                name, sys_name, str_md5(password), tel_phone, uid)
            execute_sql(sql, 'insert')
            return stand([])


# 删除用户
def sql_sys_delete(name_id):
    sql = "select uid from zz_operator where id = {0}".format(name_id)
    uid = execute_sql(sql)
    sql = "delete from zz_operator where id = {0} ".format(name_id)
    execute_sql(sql)
    sql = "delete from zz_user_info where id = {0} ".format(uid[0]['uid'])
    execute_sql(sql)
    return stand([])


# 根据id查出id、用户名、姓名、密码
def sql_sys_find(name_id):
    sql = "select name,sys_name,password,tel_phone from zz_operator where id = {0}".format(name_id)
    sys_data = execute_sql(sql)
    return stand(sys_data[0])


# 修改状态
def sql_sys_status(name_id, zt):
    sql = "UPDATE zz_operator SET zt = '{0}' WHERE id = '{1}'".format(zt, name_id)
    execute_sql(sql)
    return stand([])
