import csv
import hashlib
import logging
import pymysql
import requests
import os
import stat
import re
import time
import json
import redis
import random
import string
# import yaml
from bs4 import BeautifulSoup
from datetime import timedelta
import calendar
from flask import Flask, render_template, request, jsonify, Blueprint
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta

redis_token = redis.Redis('192.168.0.46', '6379', 0, 'yisa123456q', decode_responses=True)


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
        db.commit()
        mysql.close()
        db.close()
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


# 以固定格式返回前端
def stand(data, message="成功", total=0, status=0):
    res = {
        "data": data,
        "message": message,
        "total": total,
        "status": status
    }
    return jsonify(res)


# 字符转md5
def str_md5(str5):
    str5 = str5.encode("utf-8")
    m = hashlib.md5()
    m.update(str5)
    return m.hexdigest()


# 毛发检测对应字典
hair_dict = {
    "序号": "id",
    "检测部门": "det_department",
    "录入人": "ent_name",
    "录入人手机号码": "ent_tel",
    "检测人姓名": "det_name",
    "身份证号码": "id_card",
    "手机号码": "tel_phone",
    "检测结果": "det_result",
    "检测对象": "det_object",
    "现场检测方式": "det_way",
    "提交时间": "det_time"
    }
