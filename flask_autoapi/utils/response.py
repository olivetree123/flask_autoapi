from flask_restful import fields
from flask_autoapi.utils.message import MESSAGE


resource_fields = {
    "code" : fields.Integer,
    "message" : fields.String,
    "data" : fields.Raw(default=None)
}

class JsonResponse(object):

    msg = MESSAGE

    def __init__(self, code=0, message="", data=None):
        if not message:
            message = self.msg.get(code)
        self.code = code
        self.data = data
        self.message = message
    
    @classmethod
    def set_msg(cls, msg):
        cls.msg = msg

