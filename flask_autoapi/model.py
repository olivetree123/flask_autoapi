from peewee import Model, CharField
from playhouse.shortcuts import model_to_dict

from flask_autoapi.utils.file import StoreConfig
from flask_autoapi.utils.diyutils import field_to_json


class ApiModel(Model):

    @classmethod
    def set_meta(cls, **kwargs):
        for key, value in kwargs.items():
            setattr(cls._meta, key, value)
    
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
            if not key in cls._meta.list_fields:
                continue
            result[key] = value
        return result
    
    @classmethod
    def get_fileid_field_name(cls):
        fields = cls.get_fields()
        for field in fields:
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
    
    @classmethod
    def store_config(cls):
        return StoreConfig(
            kind=cls._meta.file_store,
            bucket=cls._meta.bucket,
            minio_url=cls._meta.minio_url, 
            minio_secure=cls._meta.minio_secure,
            minio_access_key=cls._meta.minio_access_key, 
            minio_secret_key=cls._meta.minio_secret_key,
            qiniu_url = cls._meta.qiniu_url,
            qiniu_access_key = cls._meta.qiniu_access_key,
            qiniu_secret_key = cls._meta.qiniu_secret_key,
        )

    
    def to_json(self, datetime_format="%Y-%m-%d %H:%M:%S"):
        r = model_to_dict(self)
        for k, v in r.items():
            r[k] = field_to_json(v, datetime_format)
        return r
    
    class Meta:
        group = ""
        # verbose_name 指定别名，用于显示在 API 文档上。默认为 Model 的名称
        verbose_name = ""
        # list_fields 用于指定 list 接口的参数
        list_fields = ()
        # file_store 指定文件存储的方式，支持 file/minio
        file_store = "file"
        # bucket 指定文件存储文件夹，或云存储的 bucket
        bucket = ""
        # minio 配置
        minio_url = ""
        minio_secure = False
        minio_access_key = ""
        minio_secret_key = ""
        # qiniu 配置
        qiniu_url = ""
        qiniu_access_key = ""
        qiniu_secret_key = ""
        


class FileIDField(CharField):
    # field_kind = "FILE_ID"
    pass