import requests
import json


class AuthApi:

    def __init__(self, ip="133.37.61.82", port="3000"):

        self.ip = ip
        self.port = port

        self.user_name = ""
        self.user_password = ""

    def login(self, login_url="auth_api/login"):

        request_url = "http://{0}:{1}/{2}".format(self.ip, self.port, login_url)
        headers = {
            'Content-Type': 'application/json',
        }
        data = {}
        data['username'] = self.user_name
        data['password'] = self.user_password

        r = requests.post(request_url, headers=headers, data=json.dumps(data))
        r = r.text
        r = json.loads(r)

        if "token" in r:
            return r["token"]  # ログイン成功時はtokenを返す
        else:
            return False  # ログイン失敗時はflaseを返す


if __name__ == "__main__":
    aa = AuthApi()
    aa.user_name = "test"
    aa.user_password = "CSgroup29"

    print(aa.login())



