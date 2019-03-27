from websocket import create_connection
from websocket import _exceptions


class Connection:

    def __init__(self, ip="127.0.0.1", port="3000"):

        self.ip = ip
        self.port = port

        self.ws = None  # websocket connection

    def create_short_connection(self):

        # websocket接続時のチェック
        try:
            self.ws = create_connection("ws://"+self.ip+":"+self.port)
        except _exceptions.WebSocketAddressException:
            return "invalid IP address"
        except ValueError:
            return "invalid PORT"
        except ConnectionRefusedError:
            return "Connection Refused!"
        except TimeoutError:
            return "Connection Time out"
        except _exceptions.WebSocketBadStatusException:
            return "Responsed Status is bad"
        else:
            # tryで例外が発生しなかったとき
            return True

    def send_str(self, message=None):

        if type(message) is bytes or str:
            self.ws.send(message)
            return True
        else:
            return False

    def receive_str(self):
        return self.ws.recv()

    def close_connection(self):
        self.ws.close()


if __name__ == "__main__":

    connection = Connection("133.37.61.82", "3000")
    connection.create_short_connection()
    print(connection.send_str("こんにちは"))
    print(connection.receive_str())
