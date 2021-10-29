"""
统计zz_hot_spot热点分析表中的数据
"""

import logging
import sys

import pymysql


def execute_sql(sql, action='select'):
    try:
        db = pymysql.connect(host='192.168.0.46', user='yisa_oe', passwd='yisa_oe', db='yisa_oe', charset="utf8")
        mysql = db.cursor(pymysql.cursors.DictCursor)
        r = mysql.execute(sql)
        if action == 'select':
            r = mysql.fetchall()
        elif action == 'update':
            pass
        elif action == 'insert':
            r = db.insert_id()
        mysql.close()
        return r
    except Exception as e:
        logging.exception('连接数据库时错误: %s', str(e))
        r = None
        if action == 'select':
            r = []
        elif action == 'update':
            pass
        elif action == 'insert':
            r = 0
        return r


# 统计总数（表名）或 日量（表名，时间)
def sql_sum(table, field=None):
    if field:
        sql = "SELECT COUNT(*) sum FROM {0} WHERE date({1}) = CURDATE()".format(table, field)
        data_sum = execute_sql(sql)
    else:
        sql = "SELECT COUNT(*) sum FROM {0}".format(table)
        data_sum = execute_sql(sql)
    if data_sum[0]['sum']:
        return data_sum[0]['sum']
    else:
        return 0


# 周同比(同比增长率=（本周注册总量－上周注册总量）÷上周注册总量×100%)
def sql_week_rate(field):
    # 查询上上周末到上周末的数据
    sql = "SELECT {} sum,time FROM zz_hot_spot WHERE YEARWEEK(date_format(time,'%Y-%m-%d'), 1) = YEARWEEK(now(), 1)-1 or YEARWEEK(date_format(time,'%Y-%m-%d')) = YEARWEEK(now())-1 order by time".format(field)
    data_last = execute_sql(sql)
    # 查询这周一到今天的数据
    sql = "SELECT {} sum,time FROM zz_hot_spot WHERE YEARWEEK(date_format(time,'%Y-%m-%d'), 1) = YEARWEEK(now(), 1) order by time".format(field)
    data_today = execute_sql(sql)
    if data_last and data_today:
        # 上周注册数
        reg_last = data_last[-1]['sum'] - data_last[0]['sum']
        # 这周注册数
        reg_today = data_today[-1]['sum'] - data_last[-1]['sum']
        # 当上周有增长时
        if reg_last != 0:
            week_rate = (reg_today - reg_last) / reg_last * 100
        # 当上周无增长时
        else:
            week_rate = reg_today * 100
    # 当无上周数据时
    elif data_today:
        week_rate = data_today[-1]['sum'] * 100
    # 当这周无数据时
    elif data_last:
        week_rate = (0 - (data_last[-1]['sum'] - data_last[0]['sum'])) * 100
    # 当这周上周都没数据
    else:
        week_rate = 0
    return round(week_rate)


# 日环比(环比增长率=(昨天注册量-前天注册量)÷前天注册量×100%)
def sql_day_rate(field):
    sql = "SELECT {} sum FROM zz_hot_spot WHERE TO_DAYS( NOW( ) ) - TO_DAYS(time) <= 2 and TO_DAYS( NOW( ) ) - TO_DAYS(time) > 0".format(field)
    data = execute_sql(sql)
    if data and data[0]['sum'] != 0:
        day_rate = (data[-1]['sum'] - data[0]['sum']) / data[0]['sum'] * 100
    elif data and data[0]['sum'] == 0:
        day_rate = data[-1]['sum'] * 100
    else:
        day_rate = 0
    return round(day_rate)


# 总登录数
def sql_sum_login():
    sql = "SELECT SUM(login_time) sum FROM zz_user_info"
    sum_login = execute_sql(sql)
    if sum_login[0]['sum']:
        return sum_login[0]['sum']
    else:
        return 0


# 任务完成率
def sql_task_rate():
    # 每日应完成任务总数
    task_sum = sql_sum('zz_man_task')
    user_num = sql_sum('zz_user_info')
    task_num = sql_sum('zz_com_task', 'com_time')
    if task_sum == 0 or user_num == 0:
        task_rate = 0
    else:
        task_rate = round(task_num / (task_sum * user_num) * 100)
    return task_rate


# 插入所有数据
def sql_hot_all():
    data_list = dict()
    # 总注册数
    data_list['reg_sum'] = sql_sum('zz_user_info')
    # 日注册数
    data_list['reg_num'] = sql_sum('zz_user_info', 'register_time')
    # 注册周同比
    data_list['reg_week_grow'] = sql_week_rate('reg_sum')
    # 注册日环比
    data_list['reg_day_grow'] = sql_day_rate('reg_num')
    # 总登录数
    data_list['login_sum'] = sql_sum_login()
    # 日登录数
    data_list['login_num'] = sql_sum('zz_user_info', 'local_time')
    # 总兑换数
    data_list['pro_sum'] = sql_sum('zz_pro_change')
    # 日兑换数
    data_list['pro_num'] = sql_sum('zz_pro_change', 'c_time')
    # 总任务数
    data_list['task_sum'] = sql_sum('zz_com_task')
    # 日任务数
    data_list['task_num'] = sql_sum('zz_com_task', 'com_time')
    # 日任务完成率
    data_list['task_rate'] = sql_task_rate()
    # 任务周同比
    data_list['task_week_grow'] = sql_week_rate('task_sum')
    # 任务日环比
    data_list['task_day_grow'] = sql_day_rate('task_num')
    # 总阅读数
    data_list['read_sum'] = sql_sum('zz_user_read')
    # 日阅读数
    data_list['read_num'] = sql_sum('zz_user_read', 'read_time')
    # 总收藏数
    data_list['col_sum'] = sql_sum('zz_user_col')
    # 日收藏数
    data_list['col_num'] = sql_sum('zz_user_col', 'col_time')
    # 总搜索数
    data_list['sear_sum'] = sql_sum('zz_user_sear')
    # 日搜索数
    data_list['sear_num'] = sql_sum('zz_user_sear', 'sear_time')

    insert_data_list = []
    for k, v in data_list.items():
        t = k + " = '" + str(v) + "'"
        insert_data_list.append(t)

    insert_data_str = ", ".join(insert_data_list)
    # 判断库里是否存在
    sql = "SELECT time FROM zz_hot_spot WHERE date(time) = CURDATE()"
    data = execute_sql(sql)
    if data:
        sql = "UPDATE zz_hot_spot SET {data} WHERE date(time) = CURDATE()".format(data=insert_data_str)
        execute_sql(sql, 'insert')
    else:
        sql = "INSERT INTO zz_hot_spot SET {data}".format(data=insert_data_str)
        execute_sql(sql, 'insert')


sql_hot_all()
