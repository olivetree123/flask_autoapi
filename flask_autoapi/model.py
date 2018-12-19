from peewee import Model, CharField
from playhouse.shortcuts import model_to_dict

from flask_autoapi.utils.diyutils import field_to_json


class ApiModel(Model):
    
    @classmethod
    def get_with_pk(cls, pk_value):
        if not id:
            return None
        return cls.get_or_none(cls._meta.primary_key == pk_value)
    
    @classmethod
    def get_field_names(cls):
        return cls._meta.sorted_field_names

    @classmethod
    def get_fields(cls):
        fields = []
        for field_name in cls.get_field_names():
            field = cls._meta.fields[field_name]
            fields.append(field)
        return fields
    
    @classmethod
    def get_field_by_name(cls, field_name):
        if field_name in cls._meta.fields:
            return cls._meta.fields[field_name]
        return None
    
    @classmethod
    def verify_params(cls, **params):
        # 验证 params 中的参数
        fields = cls.get_fields()
        for field in fields:
            if field.auto_increment or field.default or field.null:
                continue
            if params.get(field.name) is None:
                print("{} is None".format(field.name))
                return False
        return True
    
    @classmethod
    def verify_list_args(cls, **args):
        # 验证 list 接口的参数
        result = {}
        for key, value in args.items():
            if not key in cls.Model._meta.list_fields:
                continue
            result[key] = value
        return result
    
    @classmethod
    def get_fileid_field_name(cls):
        fields = cls.get_fields()
        for field in fields:
            print(field)
            if isinstance(field, FileIDField):
                return field.name
        return None
    
    @classmethod
    def update_by_pk(cls, pk_value, **params):
        status = cls.verify_params(**params)
        if not status:
            return
        field_names = cls.get_field_names()
        r = cls.get_with_pk(pk_value)
        for key, value in params.items():
            if not key in field_names or cls.get_field_by_name(key).primary_key:
                continue
            setattr(r, key, value)
        r.save()
        return r
    
    def to_json(self, datetime_format="%Y-%m-%d %H:%M:%S"):
        r = model_to_dict(self)
        for k, v in r.items():
            r[k] = field_to_json(v, datetime_format)
        return r
    
    class Meta:
        group = ""
        # 指定别名，用于显示在 API 文档上。默认为 Model 的名称
        verbose_name = ""
        # list_fields 用于指定 list 接口的参数
        list_fields = ()


class FileIDField(CharField):
    # field_kind = "FILE_ID"
    pass