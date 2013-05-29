import sys
import os
import subprocess

import settings

class NginxDriver(object):
    """
    encapsulation to nginx
    """
    
    def __init__(self,bin_path=None,logger=None):
        if not bin_path:
            self.bin_path = settings.nginx_bin_path
            self.logger = logger
    
    def _add_host(self,server,server_path):
        if not os.path.exists(server_path):
            try:
                fd = open(server_path,'w')
                fd.write(str(server))
                fd.close()
                self.perform_conf()
            except IOError,e:
                self.logger.exception(e)
                if e.errno == 2:
                    why = False,'open_no_file'
                elif e.errno == 13:
                    why = False,'open_permission_denied'
                else:
                    why = False,'unknown_ioerror'
                return why
            except Exception,e:
                self.logger.exception(e)
                return False,'addhost_failed'
            else:
                return True,'addhost_done'
        else:
            return False,'server_exists'
    
    def _add_http_host(self, server, server_name):
        server_path = os.path.join(settings.http_conf_path,
                                   server_name + settings.conf_suffix)
        ret = self._add_host(server,server_path)
        return ret
    
    def _add_tcp_host(self, server, server_port):
        server_path = os.path.join(settings.tcp_conf_path,
                                   str(server_port) + settings.conf_suffix)
        ret = self._add_host(server,server_path)
        return ret
    
    def add_host(self, message):
        """
        add the configuration file of load balance host.
        then restart nginx process to let the configuration take effect.
        """
        host_type = message['content'].get('host_type',None)
        
        # http loadbalance
        if host_type == 'http':
            if self.ensure_conf(settings.http_conf_path):
                content = message.get('content',None)
                server = content.get('server',None)
                server_name = content.get('server_name',None)
                if server and server_name:
                    ret,why = self._add_http_host(server, server_name)
                    if ret:
                        return True,why
                    else:
                        return False,why
                else:
                    why = 'error_args'
                    return False,why
            else:
                why = 'conf_not_exists'
                return False,why
        
        # tcp loadbalance
        elif host_type == 'tcp':
            if self.ensure_conf(settings.tcp_conf_path):
                content = message.get('content',None)
                server = content.get('server',None)
                server_port = content.get('server_port',None)
                if server and server_port:
                    ret,why = self._add_tcp_host(server,server_port)
                    if ret:
                        return True,why
                    else:
                        return False,why
                else:
                    why = 'conf_not_exists'
                    return False,why
            else:
                why = 'conf_not_exists'
                return False,why
    
    def _delete_host(self,server_path):
        try:
            if not os.path.exists(server_path):
                raise PathNotExists(exc=server_path)
        except PathNotExists,e:
            self.logger.exception(e)
            return False,'file_not_exists'
        try:
            os.remove(server_path)
            self.perform_conf()
        except IOError,e:
            self.logger.exception(e)
            if e.errno == 2:
                return False,'file_not_exists'
            if e.errno == 13:
                return False,'remove_permission_denied'
            else:
                return False,'unknown_ioerror'
        except NginxPerformError,e:
            self.logger.exception(e)
            return False,'nginx_failed'
        except Exception,e:
            self.logger.exception(e)
            return False,'remove_host_failed'
        else:
            return True,'remove_host_done'
    
    def _delete_http_host(self, server):
        server_path = os.path.join(settings.http_conf_path,
                                   server + settings.conf_suffix)
        ret = self._delete_host(server_path)
        return ret
    
    def _delete_tcp_host(self, server):
        server_path = os.path.join(settings.tcp_conf_path,
                                   str(server) + settings.conf_suffix)
        ret = self._delete_host(server_path)
        return ret
    
    def delete_host(self, message):
        """
        delete the configuration file of load balanace host.
        """
        host_type = message['content'].get('host_type',None)
        server = message['content'].get('server',None)
        
        if host_type == 'http':
            ret,why = self._delete_http_host(server)
        if host_type == 'tcp':
            ret,why = self._delete_tcp_host(server)
        if ret:
            return True,why
        else:
            return False,why
    
    def delete_server_path(self,path):
        """
        function delete file
        """
        try:
            os.remove(path)
        except Exception,e:
            self.logger.exception(e)
    
    def restart_node(self):
        """
        the convenience function of self.perform_conf
        """
        ret = self.perform_conf()
        if ret != True:
            return False,'nginx_faild'
        else:
            return True,'perform_done'
    
    def perform_conf(self):
        """
        restart nginx process to let the configuration take effect.
        """
        #TODO: if nginx process is not running, just try to run it.
        self.logger.info('reload nginx now...')
        action = ' -s reload'
        args = settings.nginx_bin_path + action 
        process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True)
        process.wait()
        returncode = process.returncode
        if returncode == 1:
            output = process.stderr.readlines()
            return output
        elif returncode == 0:
            return True
    
    def ensure_conf(self,conf_path):
        """
        make sure the configuration path
        and the executeable file of nginx are exists. 
        """
        try:
            if os.path.exists(conf_path) and os.path.exists(self.bin_path):
                return True
            else:
                return False
        except Exception,e:
            self.logger.exception(e)
            return False
