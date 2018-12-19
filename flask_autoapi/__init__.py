# 获取所有的 docstring，生成 doc
import os
from flask_restful import Api

from flask_autoapi.model import ApiModel
from flask_autoapi.endpoint import BaseEndpoint, BaseListEndpoint


class AutoAPI(object):
    def __init__(self):
        self.api = Api()
        self.app = None
        self.model_list = None
        # doc_folder 位于 static 目录下
        self.doc_folder = "docs"
    
    def init_app(self, app, model_list):
        if not isinstance(model_list, (list, tuple)):
            raise Exception("model_list 应该是一个列表，不是{}".format(type(model_list)))
        for model in model_list:
            if not issubclass(model, ApiModel):
                raise Exception("model 应该继承自 ApiModel")
        self.app = app
        self.model_list = model_list
        self.app.add_url_rule("/docs/", "docs", self._static_file, strict_slashes=True)
        self.app.add_url_rule("/docs/<path:path>", "docs", self._static_file, strict_slashes=True)
        self.auto_urls()
        self.api.init_app(self.app)
    
    def _static_file(self, path=None):
        if not path:
            path = "index.html"
        path = os.path.join(self.doc_folder, path)
        return self.app.send_static_file(path)
    
    def auto_urls(self):
        endpoints = []
        for model in self.model_list:
            class_name = model.__name__ + "Endpoint"
            endpoint = type(class_name, (BaseEndpoint, ), {})
            endpoint.Model = model
            endpoints.append(endpoint)

            class_name = model.__name__ + "ListEndpoint"
            endpoint = type(class_name, (BaseListEndpoint, ), {})
            endpoint.Model = model
            endpoints.append(endpoint)
        
        for endpoint in endpoints:
            if endpoint.Type.upper() == "LIST":
                url = "/api/"+endpoint.Model.__name__.lower()+"/"+endpoint.Type.lower()+"/"
                self.api.add_resource(endpoint, url, strict_slashes=False)
            else:
                url1 = "/api/"+endpoint.Model.__name__.lower()+"/"
                url2 = url1 + "<id>/"
                self.api.add_resource(endpoint, url1, url2, strict_slashes=False)



        