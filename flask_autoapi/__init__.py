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
        self._lazy_resources = []
    
    def init_app(self, app, model_list, decorator_list=None, project_name=""):
        if not isinstance(model_list, (list, tuple)):
            raise Exception("model_list 应该是一个列表，不是{}".format(type(model_list)))
        for model in model_list:
            if not issubclass(model, ApiModel):
                raise Exception("model 应该继承自 ApiModel")
        self.app = app
        self.model_list = model_list
        self.project_name = project_name if project_name else os.getcwd().split("/")[-1]
        if not self.project_name:
            raise Exception("project_name 不能为空，需要使用 project_name 作为 URL 前缀")
        self.app.add_url_rule("/docs/", "docs", self._static_file, strict_slashes=False)
        self.app.add_url_rule("/docs/<path:path>", "docs", self._static_file, strict_slashes=False)
        self._add_decorators(decorator_list)
        self._auto_urls()
        self.api.init_app(self.app)
        for data in self._lazy_resources:
            self.update_resource(data[0], *data[1:])
    
    def update_resource(self, resource, *urls):
        if self.app:
            endpoint = resource.__name__.lower()
            func = self.api.output(resource.as_view(endpoint))
            self._del_exists_endpoint(endpoint)
            for url in urls:
                self.app.add_url_rule(url, endpoint, func, strict_slashes=False)
        else:
            self._lazy_resources.append((resource, *urls))
    
    def _del_exists_endpoint(self, endpoint):
        if self.app.view_functions.get(endpoint):
            del self.app.view_functions[endpoint]
            for i in range(len(self.app.url_map._rules)):
                if self.app.url_map._rules[i].endpoint == endpoint:
                    del self.app.url_map._rules[i]
                    break
    
    def _static_file(self, path=None):
        if not path:
            path = "index.html"
        path = os.path.join(self.doc_folder, path)
        return self.app.send_static_file(path)
    
    def _add_decorators(self, decorator_list):
        if decorator_list:
            BaseEndpoint.add_decorators(decorator_list)
            BaseListEndpoint.add_decorators(decorator_list)

    def _auto_urls(self):
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
            if endpoint.Type:
                url = "/".join(["", self.project_name.lower(), endpoint.Model.__name__.lower(), endpoint.Type.lower(), ""])
                self.api.add_resource(endpoint, url, endpoint=endpoint.__name__.lower(), strict_slashes=False)
            else:
                url1 = "/".join(["", self.project_name.lower(), endpoint.Model.__name__.lower(), ""])
                url2 = url1 + "<id>/"
                self.api.add_resource(endpoint, url1, url2, endpoint=endpoint.__name__.lower(), strict_slashes=False)

        