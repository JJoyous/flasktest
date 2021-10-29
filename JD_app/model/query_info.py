from model.config import *


# 小铃铛查找被通知用户所有通知信息
def sql_xld(uid):
    sql = "select id, info_type, art_id, info_tit, name, DATE_FORMAT(info_time,'%Y-%m-%d %H:%i:%s') time ,type from zz_info where bname = '{0}' order by info_time desc".format(uid)
    data = execute_sql(sql)
    if data:
        for i in data:
            i["info_tit"] = dis_html_word(i["info_tit"])
    return stand(data)


# 查看通知详细信息
def sql_xld_xx(info_id):
    sql = "select id, info_type, art_id, info_tit, name, DATE_FORMAT(info_time,'%Y-%m-%d %H:%i:%s') time ,type from zz_info where id = {0} order by info_time desc".format(info_id)
    data = execute_sql(sql)
    sql = "update zz_info set type= '1' where id = {0}".format(info_id)
    execute_sql(sql, 'update')
    # 插入阅读表
    sql_add("art_read", data[0]['art_id'])
    sql = "insert into zz_user_read(art_id)value('{0}')".format(data[0]['art_id'])
    execute_sql(sql, 'insert')
    return stand(data)


# 确实用户是否点赞或者收藏该文章
def like_col(data, uid):
    sql = "select art_id from zz_user_col where uid = '{0}'".format(uid)
    col = execute_sql(sql)
    sql = "select art_id from zz_user_like where uid = '{0}' and col = '1'".format(uid)
    like = execute_sql(sql)
    for i in data:
        if col:
            for j in col:
                if i["id"] == j["art_id"]:
                    i['col'] = "1"
                    break
                else:
                    i["col"] = "0"
        else:
            i["col"] = "0"
        if like:
            for x in like:
                if i["id"] == x["art_id"]:
                    i['like'] = "1"
                    break
            else:
                i["like"] = "0"
        else:
            i["like"] = "0"


# 搜索关键字
def sql_sear(sear_key, uid, pn, size):
    # 查询文章信息
    sql = "select id, art_title, art_img, vid_info, art_cont, DATE_FORMAT(local_time,'%Y-%m-%d %H:%i:%s') time from zz_art_info where art_title like '%{0}%' order by local_time desc limit {1},{2}".format(sear_key, int(size) * (int(pn) - 1), int(size))
    data = execute_sql(sql)
    for i in data:
        i["art_cont"] = dis_html_word(i["art_cont"])
        if i["art_img"] == "":
            i["art_img"] = []
        else:
            i["art_img"] = i["art_img"].split('&&')
        if i["vid_info"] == "":
            i["vid_info"] = []
        else:
            i["vid_info"] = i["vid_info"].split('&&')
    # 插入搜索表
    sql = "insert into zz_user_sear (uid, sear_key) value ('{0}','{1}')".format(uid, sear_key)
    execute_sql(sql, 'insert')
    like_col(data, uid)
    return stand(data)


# 点击文章详情，根据id来搜索文章详细信息
def sql_sear_art(art_id, uid):
    #  查询文章信息
    sql = "select * from zz_art_info where id = '{0}'".format(art_id)
    data = execute_sql(sql)

    if data:
        #  插入阅读表，阅读次数+1
        sql_add("art_read", art_id)
        sql = "insert into zz_user_read(art_id)value('{0}')".format(art_id)
        execute_sql(sql, 'insert')

        # 格式化文章内容
        data[0]['local_time'] = data[0]['local_time'].strftime('%Y-%m-%d')
        if data[0]["art_img"] == "":
            data[0]["art_img"] = []
        else:
            data[0]["art_img"] = data[0]["art_img"].split('&&')
        if data[0]["vid_info"] == "":
            data[0]["vid_info"] = []
        else:
            data[0]["vid_info"] = data[0]["vid_info"].split('&&')
        data[0]['art_cont_old'] = data[0]['art_cont']
        data[0]['art_cont'] = dis_html_word(data[0]['art_cont'])
        like_col(data, uid)

        # 查看文章是否有评论
        sql = "select name, art, DATE_FORMAT(art_time,'%Y-%m-%d %H:%i:%s') time from zz_user_comm where art_id = '{0}' order by art_time desc".format(art_id)
        comm = execute_sql(sql)
        if comm:
            art_data = [{"nr": data[0], "pl": comm}]
        else:
            art_data = [{"nr": data[0], "pl": []}]
        return stand(art_data)

    # 文章不存在
    else:
        return stand([], "文章不存在")


# 点赞
def sql_like(col, art_id, uid, art_tit):
    sql = "select id from zz_user_like where art_id = '{0}' and uid = '{1}'".format(art_id, uid)
    like = execute_sql(sql)
    if like:
        if col == "1":
            sql = "update zz_user_like set col = '1' where id = '{0}'".format(like[0]['id'])
            execute_sql(sql, "update")
            sql_add("art_like", art_id)
        elif col == "0":
            sql = "update zz_user_like set col = '0' where id = '{0}'".format(like[0]['id'])
            execute_sql(sql, "update")
            sql_dec("art_like", art_id)
    else:
        # 搜索uid对应的用户名
        sql = "select username from zz_user_info where id = '{0}'".format(uid)
        username = execute_sql(sql)[0]['username']
        # # 搜索点赞过这篇文章的人
        # sql = "select uid from zz_user_like where art_id = '{0}'".format(art_id)
        # user = execute_sql(sql)
        # # 给点赞同一篇文章的人发通知
        # for i in user:
        #     info = username + ' 点赞了 ' + art_tit
        #     sql = "insert into zz_info (info_type, art_id, info_tit, name, bname) value ('点赞','{0}','{1}','{2}','{3}')".format(
        #         art_id, info, username, i['uid'])
        #     execute_sql(sql, "insert")
        # 插入点赞表
        sql = "insert into zz_user_like (art_id, uid, name, art_tit) value ('{0}','{1}','{2}','{3}')".format(art_id, uid, username, art_tit)
        execute_sql(sql, 'insert')
        sql_add("art_like", art_id)


# 写评论
def sql_com_ins(art_id, uid, art):
    sql = "SELECT sensitive_word FROM zz_sensitive_word WHERE '{comment}' REGEXP sensitive_word".format(comment=art)
    res = execute_sql(sql)
    if res:
        return stand([], '内容涉及敏感词，评论失败', 0, 1)
    else:
        # 搜索uid对应的用户名
        sql = "select username from zz_user_info where id = '{0}'".format(uid)
        username = execute_sql(sql)[0]['username']
        # # 搜索评论过这篇文章的人
        # sql = "select uid from zz_user_comm where art_id = '{0}'".format(art_id)
        # user = execute_sql(sql)
        # # 给评论同一篇文章的人发通知
        # for i in user:
        #     if i['uid'] != int(uid):
        #         info = username + '在"' + art_tit + '"文章中评论了：' + art
        #         sql = "insert into zz_info (info_type, art_id, info_tit, name, bname)value('评论','{0}','{1}','{2}','{3}')".format(art_id, info, username, i['uid'])
        #         execute_sql(sql, "insert")
        # 插入评论表
        sql = "insert into zz_user_comm (art_id, uid, name, art) value ('{0}','{1}','{2}','{3}')".format(art_id, uid, username, art)
        execute_sql(sql, "insert")
        sql_add("comments", art_id)
        return stand([], '评论成功')


# 收藏
def sql_col(col, art_id, uid):
    # 搜索uid对应的姓名，电话
    sql = "select name,re_phone from zz_user_info where id = '{0}'".format(uid)
    user = execute_sql(sql)[0]
    if col == "1":
        sql = "insert into zz_user_col(art_id, uid, name, re_phone)value('{0}','{1}','{2}','{3}')".format(art_id, uid, user['name'], user['re_phone'])
        execute_sql(sql, "insert")
        sql_add('art_col', art_id)
    elif col == "0":
        sql = "delete from zz_user_col where uid = '{0}' and art_id = {1}".format(uid, art_id)
        execute_sql(sql, "update")
        sql_dec('art_col', art_id)


# 分享，点赞，评论，阅读, 收藏+1
# 表名，类型，文章id
def sql_add(func, art_id):
    sql = "update zz_art_info set {0} = {0} + 1 where id = {1}".format(func, art_id)
    execute_sql(sql, "update")


# 点赞、收藏-1
def sql_dec(func, art_id):
    sql = "update zz_art_info set {0} = {0} - 1 where id = {1}".format(func, art_id)
    execute_sql(sql, "update")


# 轮播图
def info_type_img(art_type):
    filepath = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '/upload/'
    if art_type == "1":
        name = os.listdir(filepath + 'JDFP')
        for i in range(len(name)):
            name[i] = 'http://192.168.0.46:8089/upload/JDFP/' + name[i]
    elif art_type == "2":
        name = os.listdir(filepath + 'JYZD')
        for i in range(len(name)):
            name[i] = 'http://192.168.0.46:8089/upload/JYZD/' + name[i]
    elif art_type == "3":
        name = os.listdir(filepath + 'KFZD')
        for i in range(len(name)):
            name[i] = 'http://192.168.0.46:8089/upload/KFZD/' + name[i]
    else:
        return stand([], '切换失败', 0, 1)
    return stand(name)


# 点击禁毒扶贫、就业指导、康复指导
def sql_info_type(art_type, uid, pn, size):
    if art_type == "1":
        art_type = "禁毒扶贫"
    elif art_type == "2":
        art_type = "就业指导"
    elif art_type == "3":
        art_type = "康复指导"
    sql = "select id, art_title, art_img, vid_info, art_cont, DATE_FORMAT(local_time,'%Y-%m-%d %H:%i:%s') time from zz_art_info where art_type ='{0}' and zt = '1' order by local_time desc limit {1},{2}".format(art_type, int(size) * (int(pn) - 1), int(size))
    data = execute_sql(sql)
    sql = "select count(id) sum from zz_art_info where art_type ='{0}' and zt = '1'"
    data_len = execute_sql(sql)[0]['sum']
    if data:
        for i in data:
            i["art_cont"] = dis_html_word(i["art_cont"])
            if i["art_img"] == "":
                i["art_img"] = []
            else:
                i["art_img"] = i["art_img"].split('&&')
            if i["vid_info"] == "":
                i["vid_info"] = []
            else:
                i["vid_info"] = i["vid_info"].split('&&')
        like_col(data, uid)
        return stand(data, "成功", data_len)
    else:
        return stand([], '没有该类型文章', 0, 1)


# 就业信息
def sql_com_info(pn, size):
    sql = "select id, com_name, com_pay, com_job, com_respon, DATE_FORMAT(local_time,'%Y-%m-%d %H:%i:%s') time from zz_com_info where zt = 1 order by local_time desc limit {0},{1}".format(int(size) * (int(pn) - 1), int(size))
    data = execute_sql(sql)
    sql = "select count(id) sum from zz_com_info where zt = 1 "
    data_len = execute_sql(sql)[0]['sum']
    return stand(data, "成功", data_len)


# 招聘详情
def sql_com_id(job_id):
    sql = "select * from zz_com_info where id = {0}".format(job_id)
    data = execute_sql(sql)
    data[0]['local_time'] = data[0]['local_time'].strftime('%Y-%m-%d')
    return stand(data)


# 处理前端标签,不全，未使用
def dis_html(hstr):
    res = re.findall(r'<p>(.*?)</p>', hstr)
    num = 0
    for i in res:
        # 处理图片
        if "<img" in i:
            r = re.findall(r'<(.*?)/>', i)
            for j in range(len(r)-1, -1, -1):
                if r[j] == 'br':
                    r.pop(j)
            # 处理单图片
            if len(r) == 1:
                r = re.findall(r'src="(.*?)"', i)
                res[num] = r
            else:
                src_list = []
                for j in range(len(r)):
                    r[j] = re.findall(r'src="(.*?)"', r[j])
                    src_list.append(r[j][0])
                res[num] = src_list
        # 处理视频
        elif "<video" in i:
            r = re.findall(r'src="(.*?)"', i)
            res[num] = r
        # 处理标签
        elif "</b>" in i or "</font>" in i or "</i>" in i or "</u>" in i or "</strike>" in i or "</span>" in i or "</strong>" in i:
            r = re.findall(r'>(.*?)<', i)
            for j in range(len(r)-1, -1, -1):
                if r[j] == "":
                    r.pop(j)
            res[num] = r
        elif "br" in i:
            r = re.findall(r'(.*?)<br/>', i)
            res[num] = r
        # 处理文本
        else:
            res[num] = [i]
        num += 1
    return res


# 提取文字
def dis_html_word(hstr):
    html_list = []
    soup = BeautifulSoup(hstr, 'html.parser')
    for i in soup.stripped_strings:
        html_list.append(i)
    return html_list
