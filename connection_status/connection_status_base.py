
class ConnectionStatusBase:

    def __init__(self):

        self.will_use = True  # 利用する意思があるかどうか
        self.can_use = False  # 設定が正常かどうか
        self.final_use = False  # 最終的に利用する設定であるかどうか
        self.can_start = False  # スタートボタンを押してもいいかどうか

    def __str__(self):

        res = self.__class__.__name__
        res += "("
        res += "will_use: {}, ".format(repr(self.will_use))
        res += "can_use: {}, ".format(repr(self.can_use))
        res += "final_use: {}, ".format(repr(self.final_use))
        res += "can_start: {}, ".format(repr(self.final_use))
        res += "), "
        return res

    def print_status(self):

        print("will_use:{}, can_use:{}".format(self.will_use, self.can_use))

    def judge_final_use(self):
        """
        最終状況を判断する際に実行
        画面遷移直前に実行すること
        :return:
        """

        if self.will_use and self.can_use:
            self.final_use = True
        else:
            self.final_use = False

    def judge_can_start(self):
        """
        スタートボタンを押してもいいかどうか決める
        :return:
        """
        if self.will_use is True and self.can_use is False:
            self.can_start = False
        else:
            self.can_start = True
