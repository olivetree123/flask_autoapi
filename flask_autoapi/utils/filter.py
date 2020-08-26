# jinja2 filters
import uuid
import json
import peewee
from datetime import datetime

from flask_autoapi.utils.diyutils import datetime_to_str


def standard_type(t):
    if not (t and isinstance(t, str)):
        return t
    t = t.upper()
    if t == "CHAR(32)":
        return "uuid"
    if t == "VARCHAR" or t.find("CHAR")>=0:
        return "string"
    return t.lower()

def str_align(word, length=10):
    return word.ljust(length," ")

def get_example(tp, choices=None):
    if choices:
        return choices[0][0]
    if tp == "uuid":
        return str(uuid.uuid4())
    if tp == "string":
        return "123456"
    if tp == "datetime":
        t = datetime.now()
        return datetime_to_str(t)
    if tp in ("int", "float", "double", "decimal"):
        return 12
    if tp == "bool":
        return 1
    return tp

def is_mtom(field):
    return isinstance(field, peewee.ManyToManyField)

def is_foreign(field):
    return isinstance(field, peewee.ForeignKeyField)

def mtom_fields(field):
    model = field.rel_model
    fields = model.get_fields()
    # fields = model.get_fields() + list(model._meta.manytomany.values())
    return fields

def foreign_fields(field):
    model = field.rel_model
    fields = model.get_fields()
    return fields

def method_field_example(field):
    if not field.field_type == "METHOD":
        return None
    r = field.method_class.get_example()
    # if not isinstance(r, (list, tuple, dict)):
    #     return r
    # r = json.dumps(r, sort_keys=True, indent=4)
    # result = ""
    # for line in r.split("\n"):
    #     result += "\n                " + line
    # return result
    return r