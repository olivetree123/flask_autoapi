import os
from jinja2 import Template
from flask_script import Command

from flask_autoapi.utils.filter import standard_type, str_align, get_example
from flask_autoapi.utils.cmd import sys_apidoc
from flask_autoapi.endpoint import BaseEndpoint, BaseListEndpoint

class GenerateDoc(Command):
    def __init__(self, model_list, static_folder="static"):
        self.static_folder = static_folder
        self.model_list = model_list
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
        f = open(os.path.join(self.static_folder, "doc.py"), "w+")
        for model in self.model_list:
            fields = model.get_display_fields()
            for doc in docs:
                if not doc:
                    print("No doc")
                    continue
                template = Template(doc)
                content = template.render(
                    Fields=fields,
                    ModelName=model.__name__, 
                    Title=model._meta.verbose_name, 
                    Group=model._meta.group or model.__name__,
                    str_align=str_align,
                    standard_type=standard_type,
                    get_example=get_example,
                    project_name=project_name,
                )
                f.write('"""'+content+'\n"""\n')
        f.close()
        sys_apidoc("-i", self.static_folder, "-o", self.docs_folder)
        