# 客户端发送伪代码：

sender_list = list()

class Sender(object):
    def __init__(self, msg_id, data):
        self.msg_id = msg_id
        self.data = data
    
    def send(self):
        send_data(self.data)


data = 123
msg_id = gen_msg_id()

sender = Sender(msg_id)
sender.send(data)

sender_list.append(sender)


