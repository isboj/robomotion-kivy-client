from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.base import EventLoop
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty, DictProperty
from kivy.uix.screenmanager import ScreenManager, Screen

from websocket_connection.connection import Connection
from robomotion_api.auth_api import AuthApi
from robomotion_api.api_v0 import ApiV0
from kivycamera import KivyCamera
from connection_status.status_manager import StatusManager

import base64
import cv2
import numpy as np

sm = ScreenManager()


class CameraWeb(Screen):
    """
    カメラを表示するスクリーン
    OpenCVを用いた表示処理自体は,KivyCameraにて定義
    """
    vnect_server_config = DictProperty(None)
    robomotion_config = DictProperty(None)
    status_manager = DictProperty(None)

    def __init__(self, **kwargs):
        super(CameraWeb, self).__init__(**kwargs)
        self.cam = None

    def cam_start(self):
        self.cam = cv2.VideoCapture(0)
        self.ids.kvcam.start(self.cam)

    def cam_start_websocket(self):
        self.cam = cv2.VideoCapture(0)
        connection = self.vnect_server_config["server_object"]
        _status_manager = self.status_manager["status_manager"]

        _status_manager.api_v0.judge_final_use()
        if _status_manager.api_v0.final_use:
            self.ids.kvcam.start_websocket(self.cam, connection, self.robomotion_config)
        else:
            self.ids.kvcam.start_websocket(self.cam, connection)

    def cam_stop(self):
        if self.cam is not None:
            self.cam.release()
            self.cam = None

        EventLoop.close()

    def back_setting(self):
        if self.cam is not None:
            self.cam.release()
            self.cam = None
        EventLoop.close()
        sm.current = 'setting_screen'

    def run_initial(self):
        """
        画面遷移後最初に実行すべき関数
        :return:
        """
        _status_manager = self.status_manager["status_manager"]
        _status_manager.vnect.judge_final_use()
        _status_manager.api_v0.judge_final_use()

        self.ids["cam_start_vnect"].disabled = not _status_manager.vnect.final_use

        self.ids["cameraweb_message"].text = str(_status_manager.api_v0) + "\n" + str(_status_manager.vnect)


class ConnectionSetting(Screen):
    """
    カメラを開始する前に各種設定を行うクラス
    """
    login_status = DictProperty(None)  # ログイン状況・情報を格納する辞書

    def __init__(self, **kwargs):
        super(ConnectionSetting, self).__init__(**kwargs)
        self.status_manager = StatusManager()

    def startButtonClicked(self):
        """
        画面遷移し、カメラの開始
        :return:
        """
        self.manager.get_screen('camera_screen').status_manager["status_manager"] = self.status_manager
        self.manager.get_screen("camera_screen").run_initial()
        sm.current = 'camera_screen'

    def manage_can_start(self):
        """
        正常に、設定が完了し、開始できるか判断する
        :return:
        """
        self.ids["start_button"].disabled = not self.status_manager.manage_can_start()

    # VNect Settingに関して

    def VNectSwitchOn(self, value):
        if value is True:
            self.status_manager.vnect.will_use = True
        else:
            self.status_manager.vnect.will_use = False
        self.manage_can_start()

    def VNectConnectButtonClicked(self):
        """
        VNectサーバへ接続
        :return:
        """
        vnect_server_ip = self.ids["vnect_server_ip"].text
        vnect_server_port = self.ids["vnect_server_port"].text

        # Websocket Connection作成
        vnect_connection = Connection(vnect_server_ip, vnect_server_port)
        _vnect_connection = vnect_connection.create_short_connection()

        if _vnect_connection is True:
            # 接続成功時
            self.ids["vnect_message"].color = [0, 1, 0, 1]
            self.ids["vnect_message"].text = "Connected"
            self.manager.get_screen('camera_screen').vnect_server_config["server_object"] = vnect_connection
            self.status_manager.vnect.can_use = True
        else:
            # 接続失敗時
            self.ids["vnect_message"].color = [1, 0, 0, 1]
            self.ids["vnect_message"].text = _vnect_connection
            self.status_manager.vnect.can_use = False
        self.manage_can_start()

    # Robomotion Settingに関して
    def RobomotionSwitchOn(self, value):
        if value is True:
            self.status_manager.api_v0.will_use = True
        else:
            self.status_manager.api_v0.will_use = False
        self.manage_can_start()

    def RobomotionConnectButtonClicked(self):
        """
        roboモーションapiサーバへ接続
        :return:
        """
        robot_name = self.ids["robot_name"].text
        motion_name = self.ids["motion_name"].text

        # ロボットの存在を確認
        token = self.login_status["token"]
        apiv0 = ApiV0()
        api_status = apiv0.set_parameters(token, robot_name, motion_name)

        robomotion_config = self.manager.get_screen('camera_screen').robomotion_config

        if api_status is True:
            # 接続成功時
            self.ids["robomotion_message"].color = [0, 1, 0, 1]
            self.ids["robomotion_message"].text = "Connected"
            robomotion_config["token"] = token
            robomotion_config["motion_id"] = apiv0.get_motion_id()
            self.status_manager.api_v0.can_use = True

        else:
            # 接続失敗時
            self.ids["robomotion_message"].color = [1, 0, 0, 1]
            self.ids["robomotion_message"].text = api_status
            self.status_manager.api_v0.can_use = False
        self.manage_can_start()


class Login(Screen):
    """
    ログイン処理を行うクラス
    """

    def __init__(self, **kwargs):
        super(Login, self).__init__(**kwargs)

    def LoginButtonClicked(self):
        """
        ログイン
        :return:
        """
        user_id = self.ids["user_id"].text
        user_password = self.ids['user_password'].text

        auth_api = AuthApi()
        auth_api.user_name = user_id
        auth_api.user_password = user_password
        login = auth_api.login()
        if login is not False:
            self.set_login_status(name=user_id, token=login)
            sm.current = 'setting_screen'
        else:
            self.ids["message"].text = "Login Failed!"

    def set_login_status(self, name, token):
        login_status = self.manager.get_screen('setting_screen').login_status
        login_status["name"] = name
        login_status["token"] = token


class CamerawebApp(App):
    """
    Appクラス
    """
    def __init__(self, **kwargs):
        super(CamerawebApp, self).__init__(**kwargs)

    def build(self):

        sm.add_widget(Login(name="login_screen"))
        sm.add_widget(ConnectionSetting(name="setting_screen"))
        sm.add_widget(CameraWeb(name="camera_screen"))
        return sm

    def on_stop(self):
        pass


if __name__ == '__main__':
    CamerawebApp().run()
