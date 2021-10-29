from model.config import *
from model.query_info import dis_html


# 查询资讯信息
def sql_info_sear(art_title, name, art_type, time_s, time_e, pn, size):
    sql_data = "SELECT id, art_title, art_type, zt, cname, DATE_FORMAT(local_time, '%Y-%m-%d %H:%i:%s') time FROM zz_art_info WHERE id != ''"
    sql_sum = "SELECT count(id) sum FROM zz_art_info WHERE id != ''"
    if art_title != "":
        sql_data += " AND art_title like '%{0}%'".format(art_title)
        sql_sum += " AND art_title like '%{0}%'".format(art_title)
    if name != "":
        sql_data += " AND cname like '%{0}%'".format(name)
        sql_sum += " AND cname like '%{0}%'".format(name)
    if art_type != "":
        sql_data += " AND art_type like '%{0}%'".format(art_type)
        sql_sum += " AND art_type like '%{0}%'".format(art_type)
    if time_s != "":
        sql_data += " AND local_time >= '{0}'".format(time_s)
        sql_sum += " AND local_time >= '{0}'".format(time_s)
    if time_e != "":
        time_rel = (datetime.strptime(time_e, '%Y-%m-%d')).strftime("%Y-%m-%d")
        sql_data += " AND local_time <= '{0} 23:59:59'".format(time_rel)
        sql_sum += " AND local_time <= '{0} 23:59:59'".format(time_rel)
    sql_data += " ORDER BY local_time DESC LIMIT {0},{1}".format((int(size) * (int(pn) - 1)), int(size))
    info_data = execute_sql(sql_data)
    info_sum = execute_sql(sql_sum)
    return stand(info_data, "成功", info_sum[0]["sum"], 0)


# 编辑、根据id查询单一资讯
def sql_info_id(info_id):
    sql = "select id, art_title, art_type, art_cont from zz_art_info where id = {0}".format(info_id)
    info_data = execute_sql(sql)
    return stand(info_data)


# 编辑、新建保存文章
def sql_info_update(info_id, name, art_title, art_type, art_cont):
    img = re.findall(r'<img src="(.*?)"', str(art_cont))
    if img:
        art_img = '&&'.join(img)
    else:
        art_img = ""

    vid = re.findall(r'<video src="(.*?)"', str(art_cont))
    if vid:
        vid_info = '&&'.join(vid)
    else:
        vid_info = ""

    # 传id为更新
    if info_id:
        sql = "UPDATE zz_art_info SET art_title = '{0}', cname = '{1}', art_type = '{2}', art_cont = '{3}', art_img = '{4}',vid_info = '{5}',local_time = Now(2) WHERE id = {6}".format(
            art_title, name, art_type, art_cont, art_img, vid_info, info_id)
        execute_sql(sql, 'update')
        return stand([])
    # 不传id传其他信息为新建
    else:
        sql = "INSERT INTO zz_art_info (art_title, cname, art_type, art_img, vid_info, art_cont, local_time) VALUES ('{0}', '{1}', '{2}', '{3}','{4}','{5}',Now())".format(
            art_title, name, art_type, art_img, vid_info, art_cont)
        execute_sql(sql, 'insert')
        return stand([])


# 发布文章
def sql_info_status(info_id, name, col):
    if col == "0":
        execute_sql("update zz_art_info set zt = '1' WHERE id = {0} ".format(info_id), 'update')
        sql = "SELECT art_title, art_cont FROM zz_art_info WHERE id = {0} AND art_type = '通知信息' ".format(info_id)
        res = execute_sql(sql)
        if res:
            # 搜索所有的用户
            user_info = execute_sql("SELECT id FROM zz_user_info")
            # 给每个人发通知(改批量插入)
            for i in user_info:
                sql = "insert into zz_info (info_type, art_id, info_tit, name, bname)value('{0}','{1}','{2}','{3}','{4}')".format(res[0]['art_title'], info_id, res[0]['art_cont'], name, i['id'])
                execute_sql(sql, "insert")
    else:
        execute_sql("update zz_art_info set zt = '0' WHERE id = {0} ".format(info_id), 'update')

    return stand([])


# 删除文章 (资讯表，点赞表，收藏表，评论表，阅读表，通知表)
def sql_info_del(info_id):
    sql = "delete from zz_art_info where id = {0}".format(info_id)
    execute_sql(sql)
    lists = ['zz_user_like', 'zz_user_col', 'zz_art_com', 'zz_user_read', 'zz_info']
    for i in lists:
        sql = "delete from {0} where art_id = {1}".format(i, info_id)
        execute_sql(sql)
    return stand([])



