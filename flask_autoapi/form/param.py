from flask_autoapi.form.field import Field


class ParamMetaclass(type):
    def __new__(cls, name, bases, attrs):
        fields = dict()
        for k, field in attrs.items():
            if isinstance(field, Field):
                fields[k] = field
                field.name = k
        attrs["fields"] = fields
        return type.__new__(cls, name, bases, attrs)


class Param(metaclass=ParamMetaclass):
    def __init__(self, **kwargs):
        fields = getattr(self, "fields")
        for field in fields.values():
            setattr(self, field.name, kwargs.get(field.name))
    
    def validate(self) -> bool:
        return True

    def json(self):
        return self.__dict__
