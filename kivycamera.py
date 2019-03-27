from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image

from robomotion_api.api_v0 import save_motionvalue

import base64
import numpy as np
import json


class KivyCamera(Image):
    """
    OpenCVを用いてカメラを作成するクラス
    """

    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.cam = None
        self.connection = None  # websocket connection保持用
        self.robomotion_status = None  # robomotion情報保持用

    def start(self, cam, fps=30):
        """
        カメラ起動
        :param cam:
        :param fps:
        :return:
        """
        self.cam = cam
        Clock.schedule_interval(self.update, 1.0/fps)

    def start_websocket(self, cam, connection, robomotion_status=None, fps=30):
        """
        カメラ起動(websocket送信も開始)
        :param cam:
        :param fps:
        :param connection: websocket connection オブジェクト
        :return:
        """
        self.cam = cam
        self.connection = connection
        self.robomotion_status = robomotion_status

        Clock.schedule_interval(self.update_with_socket, 1.0/fps)

    def stop(self):
        Clock.unscedule_interval(self.update)
        self.cam = None

    def update(self, dt):
        """
        フレームごとにOpenCVより得られたカメラ画像を
        kivyのtextureに変換し表示をする
        :param dt:
        :return:
        """
        return_value, frame = self.cam.read()
        if return_value:
            texture = self.texture
            w, h = frame.shape[1], frame.shape[0]
            if not texture or texture.width != w or texture.height != h:
                self.texture = texture = Texture.create(size=(w, h))
                texture.flip_vertical()
            texture.blit_buffer(frame.tobytes(), colorfmt='bgr')
            self.canvas.ask_update()

    def update_with_socket(self, dt):
        """
        フレームごとにOpenCVより得られたカメラ画像を
        kivyのtextureに変換し表示をする

        フレームを更新する際にデータを送信する
        :param dt:
        :return:
        """
        return_value, frame = self.cam.read()

        # 送信処理
        send_data = {}
        frame_ = frame.tostring()  # バイト列にframeを変換
        frame_ = base64.b64encode(frame_).decode('utf-8')  # base64エンコード
        send_data["frame"] = frame_
        send_data = json.dumps(send_data)  # 送信はjsonで行う
        self.connection.send_str(send_data)  # 送信

        # 受信後
        recv = self.connection.receive_str()  # 受信
        recv = json.loads(recv)
        vnect_joints = recv["vnect_joints"]
        #print(recv["vnect_joints"])
        vnect_frame = recv["vnect_frame"]

        vnect_frame = vnect_frame.encode('utf-8')
        vnect_frame = base64.b64decode(vnect_frame)  # base64デコード
        vnect_frame = np.frombuffer(vnect_frame, dtype=np.uint8)  # バイト列に変換したものを戻す
        frame = np.reshape(vnect_frame, (368, 736, 3))  # numpy配列に戻す

        #  kivyでの描画処理
        if return_value:
            texture = self.texture
            w, h = frame.shape[1], frame.shape[0]
            if not texture or texture.width != w or texture.height != h:
                self.texture = texture = Texture.create(size=(w, h))
                texture.flip_vertical()
            texture.blit_buffer(frame.tobytes(), colorfmt='bgr')
            self.canvas.ask_update()

        # robomotion apiへの保存
        if self.robomotion_status is not None:
           save_motionvalue(self.robomotion_status["token"],
                            self.robomotion_status["motion_id"],
                            vnect_joints)
