import os
from tornado import template
import settings

TCP_LOADBALANCE_CONF = settings.tcp_template

class TemplateManage(object):
    """
    template manager, render template with variables.
    """
    
    def __init__(self, path):
        self.path = path
    
    @property
    def get_lbconf_path(self):
        """
        get the template dir.
        """
        return os.path.join(settings.project_path, self.path)

    def get_template(self, template_name):
        """
        load the template with name.
        """
        loader = template.Loader(self.get_lbconf_path)
        t = loader.load(template_name)
        return t
    
    def render_http_lb(self,**kwargs):
        """
        render the http load balance template
        """
        server_name = kwargs.get('server_name', None)
        upstream_server = kwargs.get('upstream_server', None)
        distrubute = kwargs.get('distrubute', None)
        t = self.get_template(HTTP_LOADBALANCE_CONF)
        if server_name and upstream_server:
            return t.generate(server_name=server_name,
                              upstream_server=upstream_server, distrubute=distrubute)
        else:
            return False
    
    def render_tcp_lb(self, **kwargs):
        """
        render the tcp load balance template.
        """
        server_port = kwargs.get('server_port', None)
        upstream_server = kwargs.get('upstream_server', None)
        distrubute = kwargs.get('distrubute', None)
        t = self.get_template(TCP_LOADBALANCE_CONF)
        if server_port and upstream_server:
            return t.generate(server_port=server_port,
                              upstream_server=upstream_server, distrubute=distrubute)
        else:
            return False