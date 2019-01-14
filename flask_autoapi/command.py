import os
import json
import peewee
from jinja2 import Template
from flask_script import Command

from flask_autoapi.utils.filter import standard_type, str_align, get_example, is_mtom, mtom_fields, method_field_example, is_foreign
from flask_autoapi.utils.cmd import sys_apidoc
from flask_autoapi.endpoint import BaseEndpoint, BaseListEndpoint

class GenerateDoc(Command):
    def __init__(self, model_list, diy_endpoint_list=None, static_folder="static"):
        self.static_folder = static_folder
        self.model_list = model_list
        self.diy_endpoint_list = diy_endpoint_list
        self.docs_folder = os.path.join(self.static_folder, "docs")

    def run(self, project_name=""):
        project_name = project_name if project_name else os.getcwd().split("/")[-1].lower()
        if not os.path.exists(self.static_folder):
            os.makedirs(self.static_folder)
        docs = [
            BaseEndpoint.get.__doc__, 
            BaseEndpoint.post.__doc__, 
            BaseEndpoint.put.__doc__, 
            BaseEndpoint.delete.__doc__,
            BaseListEndpoint.get.__doc__,
        ]
        for endpoint in self.diy_endpoint_list:
            if hasattr(endpoint, "get"):
                docs.append(endpoint.get.__doc__, )
            if hasattr(endpoint, "post"):
                docs.append(endpoint.post.__doc__, )
            if hasattr(endpoint, "put"):
                docs.append(endpoint.put.__doc__, )
            if hasattr(endpoint, "delete"):
                docs.append(endpoint.delete.__doc__, )
        f = open(os.path.join(self.static_folder, "doc.py"), "w+")
        for model in self.model_list:
            mtm = list(model._meta.manytomany.values())
            for m in mtm:
                print(m, m.name, type(m), isinstance(m, peewee.ManyToManyField), m.rel_model)
            fields = model.get_display_fields()
            all_fields = model.get_fields() + list(model._meta.manytomany.values()) + list(model._meta.method_fields.values())
            r = get_model_example(model)
            data = {
                "code": 0,
                "message":"",
                "data": r
            }
            list_data = {
                "code": 0,
                "message":"",
                "data": [r]
            }
            for doc in docs:
                if not doc:
                    continue
                template = Template(doc)
                content = template.render(
                    Fields=fields,
                    # AllFields=all_fields,
                    ModelName=model.__name__, 
                    Title=model._meta.verbose_name, 
                    Group=model._meta.group or model.__name__,
                    str_align=str_align,
                    standard_type=standard_type,
                    # get_example=get_example,
                    project_name=project_name,
                    # is_mtom=is_mtom,
                    # mtom_fields=mtom_fields,
                    # method_field_example=method_field_example,
                    DATA=json.dumps(data, indent=4, sort_keys=True),
                    LIST_DATA=json.dumps(list_data, indent=4, sort_keys=True),
                )
                f.write('"""'+content+'\n"""\n')
        f.close()
        sys_apidoc("-i", self.static_folder, "-o", self.docs_folder)


def get_model_example(model):
    data = {}
    all_fields = model.get_fields() + list(model._meta.manytomany.values()) + list(model._meta.method_fields.values())
    for field in all_fields:
        if is_foreign(field):
            data[field.name] = get_model_example(field.rel_model)
        elif is_mtom(field) and not field._is_backref:
            data[field.name] = [get_model_example(field.rel_model)]
        elif is_mtom(field):
            data[field.name] = get_example(standard_type(field.field_type))
        elif field.field_type == "METHOD":
            data[field.name] = method_field_example(field)
        else:
            data[field.name] = get_example(standard_type(field.field_type), field.choices)
    return data