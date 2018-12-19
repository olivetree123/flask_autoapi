from jinja2 import Template
from flask_script import Command

from flask_autoapi.cmd import sys_apidoc
from flask_autoapi.endpoint import BaseEndpoint, BaseListEndpoint

class GenerateDoc(Command):
    def __init__(self, model_list):
        self.model_list = model_list

    def run(self):
        f = open("static/doc.py", "w+")
        for model in self.model_list:
            fields = model.get_fields()
            template = Template(BaseEndpoint.get.__doc__)
            doc = template.render(
                Fields=fields,
                ModelName=model.__name__, 
                Title=model._meta.verbose_name, 
                Group=model._meta.group,
            )
            f.write('"""'+doc+'\n"""\n')
        f.close()
        sys_apidoc("-i", "static/", "-o", "static/doc/")
        