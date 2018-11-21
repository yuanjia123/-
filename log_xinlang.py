import requests
from lxml import etree


class Login(object):
    def __init__(self):
        self.headers = {
            'Referer': 'https://github.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Host': 'github.com'
        }
        self.login_url = 'https://github.com/login'
        self.post_url = 'https://github.com/session'
        self.logined_url = 'https://github.com/settings/profile'
        self.session = requests.Session()

    def token(self):
        response = self.session.get(self.login_url, headers=self.headers)
        selector = etree.HTML(response.text)
        token = selector.xpath('//div//input[2]/@value')
        return token

    def login(self, email, password):
        post_data = {                        #在form data  下面的数据中找到
            'commit': 'Sign in',
            'utf8': '✓',
            'authenticity_token': self.token()[0],    #直接调用， 上面获取到的token  参数
            'login': email,
            'password': password
        }
        response = self.session.post(self.post_url, data=post_data, headers=self.headers)   #放入 post请求的header里面。
        if response.status_code == 200:
            self.dynamics(response.text)    #登录成功以后跳转到首页， 首页有所有人的动态。 拿到以后，打印所有人，

        response = self.session.get(self.logined_url, headers=self.headers)
        if response.status_code == 200:
            self.profile(response.text)   #在用到这个方法， 处理详细页面的个人信息。

    def dynamics(self, html):
        selector = etree.HTML(html)
        dynamics = selector.xpath('//div[contains(@class, "news")]//div[contains(@class, "alert")]')
        for item in dynamics:
            dynamic = ' '.join(item.xpath('.//div[@class="title"]//text()')).strip()
            print(dynamic)

    def profile(self, html):
        print(html)
        selector = etree.HTML(html)
        name = selector.xpath('//input[@id="user_profile_name"]/@value')[0]                       # 哪个人的name
        email = selector.xpath('//select[@id="user_profile_email"]/option[@value!=""]/text()')   #哪个人的email
        print(name, email)                                                                       #将他们打印出来


if __name__ == "__main__":
    login = Login()
    login.login(email='帐号', password='密码')
