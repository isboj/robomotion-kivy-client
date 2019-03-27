from .api_v0_status import ApiV0Status
from .vnect_status import VnectStatus


class StatusManager:

    def __init__(self):
        self.api_v0 = ApiV0Status()
        self.vnect = VnectStatus()

        # スタートボタンを押せるかを返す
        self.can_push_start_button = False

    def manage_can_start(self):

        self.api_v0.judge_can_start()
        self.vnect.judge_can_start()

        if self.vnect.can_start is False:
            # api_v0はvnectが使える場合のみ可能
            self.api_v0.can_start = False

        if self.vnect.can_start and self.api_v0.can_start:
            return True
        else:
            return False
