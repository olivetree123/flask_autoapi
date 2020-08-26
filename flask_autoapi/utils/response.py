from flask_restful import fields
from flask_autoapi.utils.message import MESSAGE


resource_fields = {
    "code" : fields.Integer,
    "message" : fields.String,
    "data" : fields.Raw(default=None)
}

class JsonResponse(object):

    def __init__(self, code=0, message="", data=None):
        if not message:
            message = MESSAGE.get(code)
        self.code = code
        self.message = message
        self.data = data

