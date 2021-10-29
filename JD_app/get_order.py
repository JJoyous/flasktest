#########################################################################
# File Name: test2.py
# Author: name
# Mail: name@yisa.com
# Created Time: 2021-04-28 21:24:49
# Edit Time: 2021-04-28 21:24:49
# Description: 
#########################################################################
#!/usr/bin/env python


import paramiko

def get_order(num):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('192.168.0.102', username='root', password='yisa123456')

    s_txt='''
import requests
import random
import json
    
def get_order_info(num):
    headers = {
                'Origin': 'https://www.kuaidi100.com',
                'Referer': 'https://www.kuaidi100.com/?from=openv',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
    url = r"https://www.kuaidi100.com/autonumber/autoComNum?"
    form_data = {
        'text': num
    }
    s = requests.session()
    s.keep_alive = False
    ret = s.post(url, headers=headers, data=form_data)
    if ret.status_code == 200:
        find_com = (ret.text.split(",")[2])
        comCode = find_com[find_com.find('comCode') + 10:-1]
        temp = random.random()
        kuaidi_url = 'https://www.kuaidi100.com/query?type={}&postid={}&temp={}&phone='.format(comCode, num, temp)
        ret1 = requests.get(kuaidi_url, headers=headers)
        if ret1.status_code == 200:
            return json.loads(ret1.text)
    return []
    '''+'''
a = get_order_info('{a}')
print(a)'''.format(a=num)
    with open('test_pcap.py','w') as f:
        f.write(s_txt)
    sftp = ssh.open_sftp()

    sftp.put('test_pcap.py','/yisa_oe/test_pcap.py')
    stdin, stdout, stderr= ssh.exec_command('python3 /yisa_oe/test_pcap.py')
    # sftp.close()
    # ssh.close()
    res = stdout.readlines()
    res = eval(res[0][:-1])
    return res
#a = get_order('JDVC09231773044')
#print(a)
