

class Field(object):
    field_type = None

    def __init__(self, verbose_name="", default=None, null=False):
        self.null = null
        self.name = ""
        self.default = default
        self.verbose_name = verbose_name


class StringField(Field):
    field_type = "string"


class IntegerField(Field):
    field_type = "int"


class FloatField(Field):
    field_type = "float"


class BooleanField(Field):
    field_type = "bool"


class ListField(Field):
    field_type = "list"


class DictField(Field):
    field_type = "dict"