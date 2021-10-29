from model.config import *
import datetime

TODAY = datetime.date.today()


# 曲线图（一个月以天为单位，这个月有多少天提交多少条，无数据提交0）
def sql_line_day(field):
    list_day = []
    # 这个月有多少天
    month_num = calendar.monthrange(TODAY.year, TODAY.month)[1]
    # 这个月从那一天开始
    month_start = datetime.date(TODAY.year, TODAY.month, 1)
    sql = "SELECT DATE_FORMAT(time, '%Y-%m-%d') as time, {0} as num FROM zz_hot_spot WHERE time >= '{1}' ORDER BY time".format(
        field, month_start)
    line_day = execute_sql(sql)
    for i in line_day:
        list_day.append(i['time'])
    for i in range(0, month_num):
        t = month_start + timedelta(days=i)
        t = str(t)
        if t not in list_day:
            day = {"time": t, "num": 0}
            line_day.append(day)
    return line_day


# 曲线图（取最近7天，无数据提交0）
def sql_line_7(time_t, table):
    list_7 = []
    for i in range(6, -1, -1):
        t = TODAY - timedelta(days=i)
        sql = "select DATE_FORMAT({0}, '%Y-%m-%d') time, count(id) count from {1} where DATE_FORMAT({0}, '%Y-%m-%d') = '{2}' group by date({0})".format(time_t, table, t)
        r = execute_sql(sql)
        if r == ():
            t = str(t)
            r = {"time": t, "count": 0}
            list_7.append(r)
        else:
            list_7.append(r[0])
    return list_7


# 曲线图(从周一开始一周)
def sql_line_week():
    sql = "SELECT DATE_FORMAT(sear_time, '%Y-%m-%d') time, count(id) count FROM zz_user_sear WHERE YEARWEEK(date_format(sear_time,'%Y-%m-%d'), 1) = YEARWEEK(now(), 1) group by time"
    line_week = execute_sql(sql)
    this_week_start = TODAY - timedelta(days=TODAY.weekday())
    line_week_list = []
    for i in range(0, 7):
        time_n = str(this_week_start + timedelta(days=i))
        data = {"time": time_n, "count": 0}
        line_week_list.append(data)
    for i in line_week_list:
        for j in line_week:
            if i['time'] == j['time']:
                i['count'] = j['count']
    return line_week_list


# 曲线图(一天24小时，以4小时为一段时间)
def sql_line_hour(time_t, table):
    # 只显示有的
    sql = "SELECT DATE_FORMAT({0}, '%k') time, count(id) count, hour(sear_time) div 4 FROM {1} WHERE date({0})= CURDATE() group by hour(sear_time) div 4".format(time_t, table)
    line_hour = execute_sql(sql)
    return line_hour


# 热点分析第1块，包括注册、登录、兑换、任务4个模块
def sql_hot_spot_1():
    # 获取所有数据
    sql = "SELECT * FROM zz_hot_spot WHERE date(time) = CURDATE()"
    sql_data = execute_sql(sql)[0]

    reg_data = {
        "reg_sum": sql_data["reg_sum"],  # 注册总数
        "reg_num": sql_data["reg_num"],  # 今天注册量n
        "reg_week_grow": sql_data["reg_week_grow"],  # 注册周同比
        "reg_day_grow": sql_data["reg_day_grow"]  # 注册日环比
    }
    login_data = {
        "login_sum": sql_data["login_sum"],  # 登陆总数
        "login_zxt": sql_line_day("login_num"),  # 登录月折线图
        "login_num": sql_data["login_num"]  # 日登录数
    }
    pro_data = {
        "pro_sum": sql_data["pro_sum"],  # 商品兑换总数
        "pro_zxt": sql_line_day("pro_num"),  # 兑换月折线图
        "pro_num": sql_data["pro_num"]  # 日兑换量
    }
    task_data = {
        "task_rate": sql_data["task_rate"],  # 任务完成率
        "task_week_grow": sql_data["task_week_grow"],  # 任务周同比
        "task_day_grow": sql_data["task_day_grow"]  # 任务日环比
    }
    return stand({"reg_info": reg_data, "login_info": login_data, "pro_info": pro_data, "task_info": task_data})


# 热点分析第2块，阅读量和收藏量折线图
def sql_hot_spot_2(types):
    if types == 'read':
        line = sql_line_7('read_time', 'zz_user_read')
    else:
        line = sql_line_7('col_time', 'zz_user_col')
    return stand(line)


# 热点分析第3块，线上热门搜索
def sql_hot_spot_3():
    sql = "SELECT sear_num, login_num FROM zz_hot_spot WHERE date(time) = CURDATE()"
    sear_data = execute_sql(sql)
    # 今日搜索用户数
    if sear_data:
        sear_num = sear_data[0]['sear_num']
    else:
        sear_num = 0
    # 人均搜索次数
    if sear_data and sear_data[0]['login_num'] == 0:
        sear_rate = sear_data[0]['sear_num']
    elif sear_data and sear_data[0]['login_num'] != 0:
        sear_rate = round(sear_data[0]['sear_num'] / sear_data[0]['login_num'], 1)
    else:
        sear_rate = 0
    # 本周搜索用户折线图
    sear_line_week = sql_line_week()
    # 本天搜索次数折线图
    sear_line_day = sql_line_hour('sear_time', 'zz_user_sear')
    return stand({"ssyhs": sear_num, "ssyh_zxt": sear_line_week, "rjss": sear_rate, "rjss_zxt": sear_line_day})


# 热点分析第4块，搜索排名
def sql_hot_spot_4(pn, size):
    sql = "select sear_key, count(sear_key) sum from zz_user_sear group by sear_key order by sum desc limit {0},{1}".format(
        (int(size) * (int(pn) - 1)), int(size))
    sear_now = execute_sql(sql)
    sql = "select sear_key, count(sear_key) sum from zz_user_sear where sear_time <= '{0}' group by sear_key order by sum desc".format(
        TODAY - timedelta(days=7))
    sear_last = execute_sql(sql)
    for i in sear_now:
        if sear_last:
            for j in sear_last:
                if i['sear_key'] == j['sear_key']:
                    rate = round((i['sum'] - j['sum']) / j['sum'] * 100)
                    i['rate'] = rate
                    break
                elif i['sear_key'] not in j:
                    i['rate'] = i['sum'] * 100
        else:
            i['rate'] = 0
    sql = "select sear_key, count(sear_key) sum from zz_user_sear group by sear_key"
    sear_len = execute_sql(sql)
    return stand(sear_now, "成功", len(sear_len))


# 热点分析第5块，文章阅读排名和文章收藏排名
def sql_hot_spot_5(types):
    if types == 'read':
        sql = "SELECT art_title, art_read FROM zz_art_info ORDER BY art_read DESC limit 7"
        rank = execute_sql(sql)
    else:
        sql = "SELECT art_title, art_col FROM zz_art_info ORDER BY art_col DESC limit 7"
        rank = execute_sql(sql)
    return stand(rank)


# 热点分析第6块，阅读资讯占比(这里有点问题)
def sql_hot_spot_6():
    sql = "select sum(art_read) sum from zz_art_info"
    data = execute_sql(sql)
    if data is not None:
        read_sum = int(data[0]['sum'])
    else:
        read_sum = 0
    sql = "select art_type, sum(art_read) num from zz_art_info group by art_type"
    read_num = execute_sql(sql)
    if read_num:
        for i in read_num:
            i['num'] = int(i['num'])
            if read_sum != 0:
                rate = round(i['num'] / read_sum * 100)
            else:
                rate = round(i['num']*100)
            i['rate'] = rate

    data = {"ydzl": read_sum, "bfb": read_num}
    return stand(data)
