import os
import json
import peewee
import inspect
from jinja2 import Template
from flask_script import Command

from flask_autoapi.utils.filter import standard_type, str_align, get_example, is_mtom, mtom_fields, method_field_example, is_foreign
from flask_autoapi.utils.cmd import sys_apidoc
from flask_autoapi.endpoint import BaseEndpoint, BaseListEndpoint

# doc_tmpl = """
#         @api {{Method}} {{Url}} {{Title}}
#         @apiGroup {{Group}}

#         @apiExample 参数
#         {%- for field in Fields %}
#         {{ str_align(standard_type(field.field_type))}} \t {{ str_align(field.name, 15) }}  # {% if field.null is sameas true %} 非必填项 {% else %} 必填项 {% endif %} {% if field.verbose_name %}, {{field.verbose_name}} {% endif %}{% endfor %}

#         @apiExample 返回值
# {{DATA}}
# """


class GenerateDoc(Command):
    def __init__(self, api, diy_endpoint_list=None, static_folder="static"):
        self.api = api
        self.static_folder = static_folder
        self.doc_model_list = api.model_list
        self.diy_endpoint_list = diy_endpoint_list if diy_endpoint_list else []
        self.docs_folder = os.path.join(self.static_folder, "docs")

    def run(self):
        if not os.path.exists(self.static_folder):
            os.makedirs(self.static_folder)
        docs = [
            {
                "method": "get",
                "content": BaseEndpoint.get.__doc__,
            },
            {
                "method": "post",
                "content": BaseEndpoint.post.__doc__,
            },
            {
                "method": "put",
                "content": BaseEndpoint.put.__doc__,
            },
            {
                "method": "delete",
                "content": BaseEndpoint.delete.__doc__,
            },
            {
                "method": "list",
                "content": BaseListEndpoint.get.__doc__,
            },
        ]

        f = open(os.path.join(self.static_folder, "doc.py"), "w+")
        # template = Template(doc_tmpl)
        # for endpoint in self.diy_endpoint_list:
        #     titles = getattr(endpoint, "api_title")
        #     if not titles:
        #         continue
        #     for method in ["get", "post", "put", "delete"]:
        #         if not hasattr(endpoint, method):
        #             continue
        #         handler = getattr(endpoint, method)
        #         param_class = inspect.getclosurevars(handler).nonlocals.get(
        #             "param_class")
        #         if not param_class:
        #             continue
        #         content = template.render(
        #             Url=self.api._custom_resources.get(endpoint.__name__),
        #             Method="{"+method.upper()+"}",
        #             Title=titles.get(method),
        #             Group=getattr(endpoint, "api_group", "Default"),
        #             Fields=param_class.fields.values(),
        #             str_align=str_align,
        #             standard_type=standard_type,
        #         )
        #         f.write('"""' + content + '\n"""\n')

        for endpoint in self.diy_endpoint_list:
            for method in ["get", "post", "put", "delete"]:
                if not hasattr(endpoint, method):
                    continue
                content = getattr(getattr(endpoint, method), "__doc__")
                if not content:
                    continue
                f.write('"""' + content + '\n"""\n')

        for model in self.doc_model_list:
            fields = model.get_display_fields()
            all_fields = model.get_fields() + list(
                model._meta.manytomany.values()) + list(
                    model._meta.method_fields.values())
            r = get_model_example(model)
            data = {"code": 0, "message": "", "data": r}
            list_data = {"code": 0, "message": "", "data": [r]}
            model._meta.api_methods = [
                method.upper() for method in model._meta.api_methods
            ]
            for doc in docs:
                if not (doc.get("content")
                        and doc["method"].upper() in model._meta.api_methods):
                    continue
                template = Template(doc.get("content"))
                content = template.render(
                    Fields=model.get_post_fields()
                    if doc["method"] in ("post", "put") else fields,
                    # AllFields=all_fields,
                    ModelName=model.__name__,
                    Title=model._meta.verbose_name,
                    Group=model._meta.group or model.__name__,
                    str_align=str_align,
                    standard_type=standard_type,
                    # get_example=get_example,
                    project_name=self.api.project_name,
                    # is_mtom=is_mtom,
                    # mtom_fields=mtom_fields,
                    # method_field_example=method_field_example,
                    DATA=json.dumps(data, indent=4, sort_keys=True),
                    LIST_DATA=json.dumps(list_data, indent=4, sort_keys=True),
                )
                f.write('"""' + content + '\n"""\n')
        f.close()
        sys_apidoc("-i", self.static_folder, "-o", self.docs_folder)


def get_model_example(model):
    data = {}
    all_fields = model.get_fields() + list(
        model._meta.manytomany.values()) + list(
            model._meta.method_fields.values())
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
            data[field.name] = get_example(standard_type(field.field_type),
                                           field.choices)
    return data