# jinja2 filters
import uuid
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
        return '"'+choices[0][0]+'"'
    if tp == "uuid":
        return '"'+str(uuid.uuid4())+'"'
    if tp == "string":
        return '"123456"'
    if tp == "datetime":
        t = datetime.now()
        return '"'+datetime_to_str(t)+'"'
    if tp in ("int", "float", "double", "decimal"):
        return 12
    if tp == "bool":
        return 1