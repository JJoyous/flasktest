
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
    
a = get_order_info('123456789')
print(a)