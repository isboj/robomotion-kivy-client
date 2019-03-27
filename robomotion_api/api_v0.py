import requests
import json


class ApiV0:

    def __init__(self):
        self._robot_name = False
        self._robot_id = False
        self._motion_name = False
        self._motion_id = False

        self._token = False
        self._headers = ""
        self.base_url = "http://133.37.61.82:3000/api_v0/"

    def set_token(self, token):
        # TODO: 関数にしているのは、tokenの正確性を確認する処理を入れたいから
        self._token = token
        self.set_headers()

    def set_headers(self):
        self._headers = {
            'Authorization': 'JWT {}'.format(self._token)
        }

    def set_robot_name(self, robot_name):
        """
        ロボット名から、ロボット名とidのパラメータを設定
        :param robot_name:
        :return: 正常終了でTrue、それ以外はAPIのエラーメッセージ
        """

        get_robot_id_url = "robots/get_robot_id/?robot_name={}"
        request_url = self.base_url + get_robot_id_url.format(robot_name)
        response = requests.get(request_url, headers=self._headers)

        response = json.loads(response.text)

        if response["status"]:
            self._robot_name = response["robot_name"]
            self._robot_id = response["robot_id"]
            return True
        else:
            return response["message"]

    def set_motion_name(self, motion_name):
        """
        モーション名から、モーション名とidのパラメータを設定
        :param motion_name:
        :return: 正常終了でTrue、それ以外はAPIのエラーメッセージ
        """
        # set_robot_nameをあらかじめ実行する必要あり
        if (self._robot_name or self._robot_id) is False:
            return "You Need Set Robot Name First"

        get_motion_id_url = "robots/{}/get_motion/?motion_name={}"

        request_url = self.base_url + get_motion_id_url.format(self._robot_id, motion_name)
        response = requests.get(request_url, headers=self._headers)

        response = json.loads(response.text)

        if response["status"]:
            self._motion_name = response["motion_name"]
            self._motion_id = response["motion_id"]
            return True
        else:
            return response["message"]

    def set_parameters(self, token, robot_name, motion_name):
        """
        まとめて、パラメータを設定できる関数
        この関数は、エラーメッセージが簡略化されているため、デバッグには利用しないこと。
        :param token:
        :param robot_name:
        :param motion_name:
        :return: エラーメッセージは、リクエストURLに間違いがないことが前提。
        """
        # Set Token
        self.set_token(token)
        # Set Robot Name
        srn = ""
        srn = self.set_robot_name(robot_name)
        if srn is not True:
            return "Robot Name does not Exit"
        # Set Motion Name
        smn = self.set_motion_name(motion_name)
        if smn is not True:
            return "Motion Name does not Exit"
        return True

    def get_motion_id(self):
        return self._motion_id


def save_motionvalue(token, motion_id, vnect_joints):
    """
    モーションのデータを保存するための暫定的な関数
    # TODO: apiv0クラスと一体的に運用したい
    :param token:
    :param motion:
    :param data:
    :return:
    """

    url = "http://133.37.61.82:3000/api_v0/values/"
    headers = {
            'Authorization': 'JWT {}'.format(token)
        }
    data = {}
    data["motion"] = motion_id
    data["data"] = json.dumps(vnect_joints)
    #data["value_num"] = -1
    r = requests.post(url, headers=headers, data=data)
    print(r.text)


def test_get_with_token(url, token):

    headers = {
        'Authorization': 'JWT {}'.format(token)
    }

    response = requests.get(url, headers=headers)

    #print(response.text)


if __name__ == "__main__":

    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6InRlc3QiLCJleHAiOjE1NDE0ODM1OTAsImVtYWlsIjoiYzIwMDd0aEBnbWFpbC5jb20ifQ.D__vfHKsukCLsPUGhGmJpsQ-_4Vyi1-APtNQifyDBxg"
    apiv0 = ApiV0()
    sp = apiv0.set_parameters(token, "Pepper", "pepper 02")
    print(sp)
    print(apiv0.get_motion_id())

    #test_get_with_token("http://133.37.61.82:3000/api_v0/robots/1/get_motion/?motion_name=pepper 02", token)
