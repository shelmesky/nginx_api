import os
import sys

# config for server
project_path = os.path.dirname(os.path.realpath(__file__))
server_node_id = 1
time_format = "%Y-%m-%d %H:%M:%S"
port_count_file = os.path.join(project_path, "port_count.dat")
port_start_count = 11001
load_balancer_host = "lb.cloud-open.cn"

# config for nginx api server
multicast_addr = "224.0.0.180"
multicast_port = 3000
multicast_bind_addr = "0.0.0.0"

# config for template and nginx configuration file
template_path = "common/templates"
nginx_path = "/usr/local/nginx"
tcp_template = "tcp.conf"
main_conf_path = os.path.join(nginx_path, 'conf')
http_conf_path = os.path.join(main_conf_path,'http.conf.d')
tcp_conf_path = os.path.join(main_conf_path,'tcp.conf.d')
nginx_bin_path = os.path.join(nginx_path, 'sbin/nginx')
conf_suffix = '.conf'