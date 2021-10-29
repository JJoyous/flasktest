#########################################################################
# File Name: deal_html.py
# Author: name
# Mail: name@yisa.com
# Created Time: 2021-05-01 14:50:21
# Edit Time: 2021-05-01 14:50:21
# Description: 
#########################################################################
# !/usr/bin/env python

import nltk
import re, json


def deal_html(b):
    img_url = re.findall('src="(.*?)"', b, re.S)
    content = b.split('</p>')
    contentList = []
    c = 1
    for i in content:
        a = []
        b = 0
        for k in i:
            b += 1
            if k == '<' and "{}.{}".format(i[b], i[b + 1]) != 'br' and (
                    "</{}".format(i[b]) in i or i[b] == "/" or i[b] == "p" or i[b] == "s" or i[
                b] == 'i' or '<{}r/>'.format(i[b] == '<br/>') or '<b{}/>'.format(i[b] == '<br/>')):
                c = 0
                continue
            if k == '"' and c == 0 and '{}{}{}'.format(i[b - 5], i[b - 4], i[b - 3]) == 'src':
                c = 1
                a.append('-*slide*-')
                continue
            if k == '"' and c == 1:
                c = 0
                a.append('-*slide*-')
                continue
            if k == '>' and c == 0:
                c = 1
                continue
            if c == 1:
                a.append(k)
        contentList.append(''.join(a))
    result = []
    for info in contentList:
        src = info.split('-*slide*-')
        for i in src:
            if i == '':
                src.remove(i)
            if '&nbsp;' in i:
                a = i.replace('&nbsp;', ' ')
                src.remove(i)
                src.append(a)
        result.append(src)
    result[-1] = img_url
    return result



