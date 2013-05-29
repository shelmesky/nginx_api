# --encoding:utf-8--

import time
import simplejson as json
from common.backend.sender import sender
from common.logger import LOG
from common.utils import timestamp_to_timestr

nodes = dict()


class NodeManager(object):
    def __init__(self):
        pass

    @staticmethod
    def update_node(data):
        '''
        更新节点列表
        '''
        remote_node_id = data['node_id']
        load = data['load']
        time_stamp = data['time_stamp']
        nodes[remote_node_id] = dict(
            node_id = remote_node_id,
            load = load,
            time_stamp = time_stamp,
            time = timestamp_to_timestr(time_stamp)
        )
    
    @staticmethod
    def get_node_len():
        '''
        返回总的节点数
        '''
        return len(nodes)
    
    @staticmethod
    def get_total_load():
        '''
        返回所有节点的负载
        '''
        total_load = 0
        for node_id, node in nodes.items():
            total_load += int(node['load'])
        return total_load

    @staticmethod
    def request(data, callback):
        '''
        根据节点的负载和节点号，判断是否由本节点处理
        '''
        cls = NodeManager
        # 如果没有其他节点，则本节点处理
        if cls.get_node_len() == 0:
            callback(data)
        # 如果有其他节点
        elif cls.get_node_len() > 0:
            
            # 如果所有节点负载大于0
            if cls.get_total_len() > 0:
                # 如果本节点负载最小，则本节点处理
                if get_min_load():
                    callback(data)
                    
            # 如果等于0
            elif cls.get_min_node() == 0:
                # 如果自己的节点号最小，则本节点处理
                if get_min_node():
                    callback(data)
                
    

node_manager = NodeManager()


class ProcessRequest(object):
    def __init__(self):
        self.callback = None

    def process_receive(self, data, node_id):
        try:
            data = eval(data)
        except Exception, e:
            LOG.exception(e)
            raise
        remote_node_id = data['node_id']
        
        # 如果消息不是自己发出的
        if remote_node_id != node_id:
            msg_type = data['msg_type']
            if msg_type == "heartbeat":
                node_manager.update_node(data)
            
            if msg_type == "task":
                node_manager.request(data, self.callback)

process_request = ProcessRequest()


def processor(conn, node_id=None):
    '''
    处理多播连接
    '''
    data, address = conn.recvfrom(2048)
    process_request.process_receive(data, node_id)


def process_send(data):
    data = json.dumps(data)
    sender(data)

