import time
from model.config import *


# 毛发检查
def sql_hair():
    sql = "SELECT * FROM zz_hair"
    r = execute_sql(sql)
    res_list = []
    for i in r:
        res_dict = dict()
        res_dict['code'] = i['id']
        res_dict['name'] = i['name']
        res_dict['pCode'] = i['classify_id']
        res_list.append(res_dict)
    return stand(res_list)


# 插入结果
def sql_ins_hair(uid, det_department, det_name, id_card, tel_phone, det_result, det_object, det_way, hair_id):
    if hair_id:
        sql = "update zz_hair_res set det_department = '{0}', det_name = '{1}', id_card = '{2}', tel_phone = '{3}', det_result = '{4}', det_object = '{5}', det_way = '{6}' where id = '{7}'".format(det_department, det_name, id_card, tel_phone, det_result, det_object, det_way, hair_id)
        execute_sql(sql, 'update')
    else:
        sql = "select name,re_phone from zz_user_info where id = '{0}'".format(uid)
        name = execute_sql(sql)[0]['name']
        re_phone = execute_sql(sql)[0]['re_phone']
        sql = "INSERT INTO zz_hair_res (det_department,ent_id,ent_name,ent_tel,det_name,id_card,tel_phone,det_result,det_object,det_way) value ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')".\
            format(det_department, uid, name, re_phone, det_name, id_card, tel_phone, det_result, det_object, det_way)
        execute_sql(sql, 'insert')
    return stand([])


# 毛发检测结果查询
# *args = (uid, hair_id, keywords, start_time, end_time, pn, size)
def sql_hair_res(*args):
    # 查询单个结果
    if args[1]:
        sql = "SELECT * FROM zz_hair_res WHERE id = {hair_id}".format(hair_id=args[1])
        hair_data = execute_sql(sql)
        hair_data[0]["det_time"] = hair_data[0]["det_time"].strftime('%Y-%m-%d %H:%M:%S')
        return stand(hair_data)
    # 查询所有结果
    else:
        sql_data = "SELECT * FROM zz_hair_res WHERE id != ''"
        sql_sum = "SELECT count(id) sum FROM zz_hair_res WHERE id != ''"
        if args[2]:
            keyword = args[2].split("&", 1)
            if keyword[1] != "":
                sql_data += " AND {0} like '%{1}%'".format(hair_dict[keyword[0]], keyword[1])
                sql_sum += " AND {0} like '%{1}%'".format(hair_dict[keyword[0]], keyword[1])
        if args[3]:
            sql_data += " AND det_time >= '{0}'".format(args[3])
            sql_sum += " AND det_time >= '{0}'".format(args[3])
        if args[4]:
            time_rel = (datetime.strptime(args[4], '%Y-%m-%d')).strftime(
                "%Y-%m-%d")
            sql_data += " AND det_time <= '{0} 23:59:59'".format(time_rel)
            sql_sum += " AND det_time <= '{0} 23:59:59'".format(time_rel)
        if args[5]:
            sql_data += " ORDER BY det_time DESC LIMIT {0},{1}".format(
                (int(args[6]) * (int(args[5]) - 1)), int(args[6]))
        info_data = execute_sql(sql_data)
        info_sum = execute_sql(sql_sum)

        sql_name = "SELECT name FROM zz_operator WHERE id = '{0}'".format(args[0])
        sys_name = execute_sql(sql_name)

        if info_data and sys_name:
            for i in info_data:
                i["det_time"] = i["det_time"].strftime('%Y-%m-%d %H:%M:%S')
                if i["ent_name"] == sys_name[0]['name']:
                    i["col"] = "1"
                else:
                    i["col"] = "0"
        if info_sum:
            return stand(info_data, "成功", info_sum[0]["sum"], 0)
        else:
            return stand([], "成功", 0, 0)


# 生成口令写入redis
def redis_generate_token():
    list1 = list(random.sample(string.digits + string.ascii_letters, 19))
    list1.insert(3, '_')
    new_token = ''.join(list1)
    redis_token.set('token', new_token)


def generate_token(token="default"):
    # 查询口令
    if token == "default":
        return stand(redis_token['token'])
    # 验证口令
    else:
        if token == redis_token['token']:
            return stand([])
        else:
            return stand([], "失败", 0, 1)
