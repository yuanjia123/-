import rsa
import re
import json
import time
import requests
import base64
import urllib3
import binascii
import xlwt
from lxml import etree
import psycopg2
from multiprocessing.pool import ThreadPool   #线程池

urllib3.disable_warnings()


class Weibo_login():
    def __init__(self, username, password):
        self.user_name = username
        self.pass_word = password
        self.session = requests.session()

    def login(self):
        json_data = self.get_json_data()  # 第一次请求， 获取服务端返回的参数
        if not json_data:
            return False
        pass_word = self.get_password(json_data['servertime'], json_data['nonce'], json_data['pubkey'])

        post_data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            # 'pagerefer': 'https://www.baidu.com/',
            'vsnf': '1',
            'su': self.username,  # 通过bs64加密后的得到的
            'service': 'miniblog',
            'servertime': json_data['servertime'],
            'nonce': json_data['nonce'],
            'pwencode': 'rsa2',
            'rsakv': json_data['rsakv'],
            'sp': pass_word,  # 通过rsa加密过的pass_word
            'sr': '1920*1080',
            'encoding': 'UTF-8',
            'prelt': 28,
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        response_data = self.session.post(login_url, data=post_data, verify=False)

        print(response_data.content.decode('gbk'))  # 先转成二进制， 然后转成dbk

        # 第一次跳转
        url1 = re.findall(r'location.replace\("(.*?)"\)', response_data.content.decode('gbk'))[0]  # 加上[0]就会变的 只剩下想要的数据
        print("要打印的url:", url1)

        # 打印，获取第二次跳转的url
        result = self.session.get(url1).content.decode('gbk')
        print("result", result)

        # 第三次跳转
        url1 = re.findall(r"location.replace\('(.*?)'\)", result)[0]
        print("打印url1******************:", url1)

        # 访问url1
        self.session.get(url1, verify=False)
        # print(self.session.get("https://weibo.com/6779766492", verify=False).content.decode())  # 可以随意访问已经登录的网页
        # print("cookies",self.session.cookies)
        # print("hreader:",self.session.headers)
        return self.session

    #帐号加密
    def get_password(self, servertime, nonce, pubkey):
        s = str(servertime) + '\t' + str(nonce) + '\n' + str(self.pass_word)
        public_key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        password = rsa.encrypt(s.encode(), public_key)
        # print(binascii.b2a_hex(password))
        return binascii.b2a_hex(password).decode()

    #密码加密
    def get_username(self):
        self.username = base64.b64encode(self.user_name.encode())  # 对传进去的进行编码

    def get_json_data(self, ):
        '''
            #这个就是按下tab以后， 产生的get请求
            前面的请求就是为了给后面的post请求铺路
        '''
        params = {
            'entry': 'weibo',
            'callback': 'sinaSSOController.preloginCallBack',
            'su': self.username,
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js(v1.4.19)',
            '_': int(time.time() * 1000),
        }
        response = self.session.get('https://login.sina.com.cn/sso/prelogin.php?', params=params,
                                    verify=False)  # ?号后面的都是一些参数

        try:
            json_loads = json.loads(re.findall(r'preloginCallBack\((.*?)\)', response.text)[0])  # ****重点来了\(的意思是从preloginCallBack(开始  ，到\)结束的所有都要   （.*？）匹配全部
        except:
            json_loads = {}
        # print(json_loads)
        return json_loads


class get_location():

    def __init__(self):
        self.headers = {

            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'SINAGLOBAL=686853348606.9484.1541139120819; SCF=AkhFCrKCUq9wsyl3f_fDwgGgFRpQSCclo3gd_NQHuXjdyEEjbRsY9PC-MgFG6xjCDbPu4IOAIOCXyPLirzjFWdo.; SUHB=00xZwj0czv30Gl; Ugrow-G0=56862bac2f6bf97368b95873bc687eef; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1; YF-Page-G0=86b4280420ced6d22f1c1e4dc25fe846; YF-V5-G0=a9b587b1791ab233f24db4e09dad383c; wb_view_log_6382564064=1920*10801; _s_tentry=-; Apache=2872156489358.7036.1542848804714; ULV=1542848804736:6:6:3:2872156489358.7036.1542848804714:1542706013869; _T_WM=3e8b91cb0fc1afc6f6b197111618f23a; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9Wh3SFjwsRGoBE8ZBHKOX.cV5JpVF02RehnESKe41h24; SUB=_2AkMsqrpQdcPxrAVSkPoQym_iaolH-jyff9OmAn7uJhMyAxgv7nNeqSVutBF-XJVarBSeGUU5IPLleV-08g-rwQpV; login_sid_t=a2b0e92dbac53ded77a3b3a4328efdaa; cross_origin_proto=SSL; WBStorage=f44cc46b96043278|undefined; UOR=,,login.sina.com.cn; wb_view_log=1920*10801',
            'Host': 'weibo.com',
            'Referer': 'https://weibo.com/2889942201/GFo7omJqz?type=comment',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'

        }

        # self.f = xlwt.Workbook(encoding='utf-8')
        # self.sheet1 = self.f.add_sheet(u'sheet1', cell_overwrite_ok=True)

    def get_html(self, url):
        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.text
            else:
                print(response.status_code)
                time.sleep(0.5)
                return self.get_html(url)
        except requests.ConnectionError as e:
            print('Error', e.args)


    def parse(self, html):  # 解析
        #print(type(html))
        id = set(re.findall('usercard="id=(\d{10})"',html.replace('\\','')))
        return id




    def location_parse(self,response,url):  #红点的坐标拼接url.
        #print(response.content.decode())
        res = response.content.decode()

        #//div[@class='pf_username']/h1/text()

        li = []
        selector = etree.HTML(res)
        try:
            name = selector.xpath('//title/text()')[0]
            print("*"*50, name)

            if name:
                li.append(name)
                li.append(url)
        except:
            print("IndexError")

        scripts = selector.xpath('.//script')
        for script in scripts:
            try:
                text = script.xpath('.//text()')
                text = ''.join(text)
                text = text.replace('//', '/')
                text = re.findall(r'<div.*/div>', text)[0]
                text = text.replace(r'\t', '\n').replace(r'\r\n', '\n').replace(r'\"', '"').replace(r'\/', '/')

                se = etree.HTML(text)

                span = se.xpath('.//span[@class = "item_text W_fl"]/text()')
                for s in span:
                    s = s.replace('\n', '').replace(' ', '')
                    if s:
                        #print("*"*50,s)
                        li.append(s)

            except:
                pass

        self.excel_write(li)

    def excel_write(self, li_list):
        conn = psycopg2.connect(database="postgres", user="postgres", password="123456", host="127.0.0.1", port="5432")
        cur = conn.cursor()
        other = None

        print("li_list", li_list)

        try:
            li_list[0] = str(li_list[0])
            if len(li_list) > 3:
                li_list_1 = li_list[:3]  #浅3
                li_list_2 = li_list[3:]  #3个之后
                other = '|'.join(li_list_2)


                #li_list[1] = li_list[1].replace("https://", '')
                print("other{}:::{}".format(other,type(other)))

                cur.execute("INSERT INTO bjzs_big_data.xinlang_spider2(name_1,url,location,other_info) VALUES (%s,%s,%s,%s);", (li_list_1[0], li_list_1[1], li_list_1[2],other))

            elif len(li_list) == 3:
                #li_list[1] = li_list[1].replace("https://", '')
                cur.execute("INSERT INTO bjzs_big_data.xinlang_spider2(name_1,url,location) VALUES (%s,%s,%s);", (li_list[0], li_list[1], li_list[2]))

            else:
                pass

        except  Exception as err:
            print(err)
            print("except: ============li_list",li_list)
            print("索引超出")
        conn.commit()
        cur.close()
        conn.close()


if __name__ == '__main__':
    login = Weibo_login('18082539819', '25257758')  # 先设置账号密码
    login.get_username()  # 给传过去的账号密码进行加密
    session = login.login()

    a = get_location()
    url1 = 'https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id=4298641625417843&max_id=4309096804900746&page={}'
    oneself = 'https://weibo.com/{}'

    pool = ThreadPool(8)  # 实现一个线程池 ，参数是线程的数量, 这里就是两个线程等待调用

    for i in range(849,1314):
        page_url = url1.format(i)
        id_list = a.parse(a.get_html(page_url))
        for id in id_list:
            private_url = oneself.format(id)
            print("详细页面的url", private_url)
            #a.location_parse(session.get(private_url, headers= a.headers, verify=False))

            pool.apply_async(a.location_parse(session.get(private_url, headers= a.headers, verify=False),private_url))  # 这个线程池传参
    pool.close()  # 关闭线程池， 不在提交任务，
    pool.join()  # 等待线程池里面的任务 运行完毕

