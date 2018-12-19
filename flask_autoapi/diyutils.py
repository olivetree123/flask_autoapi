import uuid
from decimal import Decimal
from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def datetime_to_str(_datetime, _format=DATETIME_FORMAT):
    return _datetime.strftime(_format)

def field_to_json(value, datetime_format=DATETIME_FORMAT):
    ret = value
    if isinstance(value, datetime):
        ret = datetime_to_str(value, datetime_format)
    elif isinstance(value, list):
        ret = [field_to_json(_) for _ in value]
    elif isinstance(value, dict):
        ret = {k: field_to_json(v) for k, v in value.items()}
    elif isinstance(value, bytes):
        ret = value.decode("utf-8")
    elif isinstance(value, bool):
        ret = int(ret)
    elif isinstance(value, uuid.UUID):
        ret = str(value)
    elif isinstance(value, Decimal):
        ret = float(ret)
    return ret