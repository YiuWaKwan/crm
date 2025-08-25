import threading
import socket,time,json
import mySqlUtil

# 客户端处理线程
class websocket_thread(threading.Thread):
    def __init__(self, connection, username):
        super(websocket_thread, self).__init__()
        self.connection = connection
        self.username = username

    def run(self):
        print('new websocket client joined!')

        while True:
            try:
                sql = "select wx_main_id,wx_id,(select groupId from wx_account_info c where c.wx_id=t.wx_main_id) from wx_chat_info t"
                chatList = mySqlUtil.getData(sql)
                group = {}
                wxMain = {}
                wxId = {}
                for chat in chatList:
                    if chat[0] in wxMain:
                        wxMain[chat[0]] = wxMain[chat[0]] + 1
                    else:
                        wxMain[chat[0]] = 1
                    if chat[0] in wxId:
                        if chat[1] in wxId[chat[0]]:
                            wxId[chat[0]][chat[1]] = wxId[chat[0]][chat[1]] + 1
                        else:
                            wxId[chat[0]][chat[1]] = 1
                    else:
                        wxId[chat[0]] = {chat[1]: 1}

                    if chat[2] != None:
                        if chat[2] in group:
                            group[chat[2]] = group[chat[2]] + 1
                        else:
                            group[chat[2]] = 1
                message = {}
                message["groupNotice"] = group
                message["wxMainNotice"] = wxMain
                message["wxNotice"] = wxId
                message["heartbeat"] = {"heart": ""}
                print(json.dumps(wxId))

                if len(group) > 0 or len(wxMain)>0 or len(wxId)>0:
                    #通知客户端
                    self.connection.send(json.dumps(message).encode())
                time.sleep(2)
            except(socket.error) :
                print("socket error")
                break

# 服务端
class websocket_server(threading.Thread):
    def __init__(self, port):
        super(websocket_server, self).__init__()
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', self.port))
        sock.listen(5)
        print('websocket server started!')
        while True:
            connection, address = sock.accept()
            try:
                username = "ID" + str(address[1])
                thread = websocket_thread(connection, username)
                thread.start()
            except socket.timeout:
                print('websocket connection timeout!')


if __name__ == '__main__':
    server = websocket_server(8001)
    server.start()