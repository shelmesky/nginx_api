#!/usr/bin/python
# --encoding:utf-8--
import os
import sys
import functools
import threading
import time

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

from tornado import ioloop
from common.logger import LOG
from common.backend.receiver import add_callback
from common import processor
from common.templates.manager import TemplateManage
from common.utils import get_tcp_port
from common.driver.nginx import NginxDriver
import settings

server_node_id = 1
callback = functools.partial(processor.processor, node_id=server_node_id)


class HeartBeat(threading.Thread):
    def __init__(self):
        super(HeartBeat, self).__init__()

    def run(self):
        while 1:
            amount, _ = self._get_host_amount(settings.tcp_conf_path)
            msg = dict(
                msg_type = "heartbeat",
                node_id = server_node_id,
                load = amount,
                time_stamp = time.time()
            )
            processor.process_send(msg)
            time.sleep(1)
    
    def _get_host_amount(self, conf_path):
        # on error callback function, just raise the error
        def listdir_onerror(error):
            raise error
        host_amount = 0
        host_list = []
        # the dirs will be an empty list, because the depth is 1
        try:
            for root, dirs, files in os.walk(conf_path, onerror=listdir_onerror):
                for file in files:
                    if os.path.isfile(os.path.join(root, file)):
                        host_amount += 1
                        host_list.append(file.split(settings.conf_suffix)[0])
        except Exception, e:
            LOG.exception(e)
            return None
        else:
            return host_amount, host_list


def request_handler(data):
    dst_host = data['dst_host']
    dst_port = data['dst_port']
    msg_id = data['msg_id']
    src_port = get_tcp_port()
    src_host = settings.load_balancer_host
    
    server_port = src_port
    upstream_server = [{dst_host: dst_port}]
    distrubute = "ip_hash"
    kwargs = {
        "server_port": server_port,
        "upstream_server": upstream_server,
        "distrubute": distrubute
    }
    
    templater = TemplateManage(settings.template_path)
    
    message = {
        "server": templater.render_tcp_lb(**kwargs),
        "server_port": server_port,
        "host_type": "tcp",
        "original": kwargs
    }
    
    message_final = {
        "message_id": msg_id,
        "message_type": "task",
        "command": "addhost",
        "content": message
    }
    
    driver = NginxDriver(logger=LOG)
    ret, why = driver.add_host(message_final)
    if ret == True:
        data = dict(
            msg_id = msg_id,
            msg_type = "result",
            node_id = server_node_id,
            target_host = src_host,
            target_port = src_port
        )
        processor.process_send(data)


if __name__ == '__main__':
    processor.process_request.callback = request_handler
    
    heartbeat = HeartBeat()
    heartbeat.start()
    
    add_callback(callback)
    ioloop.IOLoop.instance().start()

