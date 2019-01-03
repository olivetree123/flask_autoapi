import types
import werkzeug
from io import BytesIO
from peewee import Model, CharField, ManyToManyField, ForeignKeyField
from playhouse.shortcuts import model_to_dict

from flask_autoapi.storage import Storage
from flask_autoapi.utils.diyutils import field_to_json, content_md5


class ApiModel(Model):

    @classmethod
    def set_meta(cls, **kwargs):
        for key, value in kwargs.items():
            setattr(cls._meta, key, value)
    
    @classmethod
    def get_with_pk(cls, pk_value, without_field_names=None):
        if without_field_names and not isinstance(without_field_names, (list, tuple)):
            return None
        fields = cls.get_fields()
        fields = [field for field in fields if field.name not in without_field_names] \
                    if without_field_names else fields
        return cls.select(*fields).where(cls._meta.primary_key == pk_value).first()
    
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
    def get_display_fields(cls):
        fields = cls.get_fields()
        fields = [field for field in fields if not field._hidden]
        return fields

    @classmethod
    def get_field_by_name(cls, field_name):
        if field_name in cls._meta.fields:
            return cls._meta.fields[field_name]
        return None

    @classmethod
    def in_handlers(cls, **params):
        # 对原始的参数进行处理
        fields = cls.get_fields() + list(cls._meta.manytomany.values())
        for field in fields:
            if not hasattr(field, "in_handler"):
                continue
            handler = getattr(cls, field.in_handler)
            if not (handler and isinstance(handler, types.MethodType)):
                raise Exception("in_handler should be function, but {} found.".format(type(handler)))
            params[field.name] = handler(params.get(field.name))
            if field.name in cls._meta.manytomany:
                params[field.name+"_value"] = params.pop(field.name)
        return params
    
    def mtom(self, **params):
        for field_name, field in self._meta.manytomany.items():
            ins = getattr(self, field_name)
            ins.clear()
            value = params[field_name+"_value"]
            if isinstance(value, (list, tuple)):
                for v in value:
                    ins.add(v)
            else:
                ins.add(value)
    
    @classmethod
    def out_handlers(cls, **data):
        # 对 to_json() 之后的结果进行处理
        fields = cls.get_fields() + list(cls._meta.manytomany.values())
        for field in fields:
            if not (hasattr(field, "out_handler") and getattr(field, "out_handler")):
                continue
            handler = getattr(cls, field.out_handler)
            if not (handler and isinstance(handler, types.MethodType)):
                raise Exception("out_handler should be function, but {} found.".format(type(handler)))
            data[field.name] = handler(data.get(field.name))
        return data

    @classmethod
    def format_params(cls, **params):
        # 格式化参数，主要是将 str 转换成 file 对象
        fields = cls.get_fields()
        for field in fields:
            if isinstance(field, ApiFileIDField):
                if field.source_type == "string":
                    content = params.get(field.source_name)
                    if not content:
                        continue
                    if not isinstance(content, (str, bytes)):
                        raise Exception("{} 应该为 str 或 bytes，而不是 {}".format(field.name, type(content)))
                    if isinstance(content, str):
                        content = content.encode("utf8")
                    f = BytesIO(content)
                    setattr(f, "md5_hash", content_md5(content))
                    setattr(f, "length", len(content))
                    params[field.name] = f
                elif field.source_type == "file":
                    f = params.get(field.source_name)
                    if not isinstance(f, (werkzeug.datastructures.FileStorage, type(None))):
                        raise Exception("类型错误，{} 应该为 werkzeug.datastructures.FileStorage 类型，而不是 {}".format(field.source_name, type(f)))
                    params[field.name] = f
                else:
                    raise Exception("不能识别的类型, 无法转换，source_type = {}".format(field.source_type))
        return params
    
    @classmethod
    def verify_params(cls, **params):
        # 验证 params 中的参数，主要验证非 None 字段是否有值
        fields = cls.get_fields()
        for field in fields:
            if field.auto_increment or field.default or field.null:
                continue
            if params.get(field.name) is None:
                print("{} is None".format(field.name))
                return False
        return True
    
    @classmethod
    def upload_files(cls, **params):
        cls.init_storage()
        fields = cls.get_fields()
        for field in fields:
            if not params.get(field.name):
                continue
            if isinstance(field, ApiFileIDField):
                file_id = cls.storage.write(params[field.name])
                params[field.name] = file_id
        return params
    
    @classmethod
    def verify_list_args(cls, **args):
        # 验证 list 接口的参数
        result = {}
        for key, value in args.items():
            if not key in cls._meta.filter_fields:
                continue
            result[key] = value
        return result
    
    @classmethod
    def get_fileid_field_name(cls, **params):
        fields = cls.get_fields()
        for field in fields:
            if isinstance(field, ApiFileIDField) and not params.get(field.name):
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
    def init_storage(cls):
        storage = Storage(
            kind=cls._meta.store_kind,
            bucket=cls._meta.bucket,
            minio_url=cls._meta.minio_url, 
            minio_secure=cls._meta.minio_secure,
            minio_access_key=cls._meta.minio_access_key, 
            minio_secret_key=cls._meta.minio_secret_key,
            qiniu_url = cls._meta.qiniu_url,
            qiniu_access_key = cls._meta.qiniu_access_key,
            qiniu_secret_key = cls._meta.qiniu_secret_key,
            qiniu_bucket_url = cls._meta.qiniu_bucket_url,
        )
        setattr(cls, "storage", storage)

    @classmethod
    def validate(cls, **params):
        """
        validate 用于验证参数
        返回 True 表示正确；
        返回 False 表示错误，会返回 BadRequest
        """
        return True
    
    @classmethod
    def diy_before_save(cls, **params):
        """
        用于 POST/PUT 方法。
        做一些自定义操作，但是不能修改参数。
        修改参数应该使用各个Field 的 in_handler。
        """
        return True
    
    @classmethod
    def diy_after_get(cls, json_data):
        """
        在 GET 方法中获取到对象并转换为 json 之后，对返回值做一些操作。
        """
        return True

    @classmethod
    def to_json(cls, obj, without_fields=None, datetime_format="%Y-%m-%d %H:%M:%S"):
        fields = cls.get_fields()
        for field in fields:
            # 如果数据源为 string，则返回时也应该返回 string
            if hasattr(field, "source_type") and field.source_type == "string" and getattr(obj, field.name):
                content = cls.storage.read(getattr(obj, field.name))
                setattr(obj, field.name, content)
        # to json
        r = model_to_dict(obj, manytomany=cls._meta.manytomany)
        # 将 many-to-many 的数据取出来
        # for field_name, field in cls._meta.manytomany.items():
        #     r[field_name] = [model_to_dict(x) for x in getattr(obj, field_name)]
        # 过滤掉不需要的字段
        result = {}
        for k, v in r.items():
            if without_fields and k in without_fields:
                continue
            result[k] = field_to_json(v, datetime_format)
        return result
    
    class Meta:
        group = ""
        # verbose_name 指定别名，用于显示在 API 文档上。默认为 Model 的名称
        verbose_name = ""
        # filter_fields 用于指定 list 接口的参数
        filter_fields = ()
        # store_kind 指定文件存储的方式，支持 file/minio/qiniu
        store_kind = "file"
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
        qiniu_bucket_url = ""
        


class ApiFileIDField(CharField):
    # field_type = "FILE_ID"

    def __init__(self, max_length=255, *args, **kwargs):
        self.source_name = kwargs.pop("source_name", "file")
        self.source_type = kwargs.pop("source_type", "file")
        super(ApiFileIDField, self).__init__(max_length=max_length, *args, **kwargs)


class ApiCharField(CharField):

    def __init__(self, max_length=255, *args, **kwargs):
        self.in_handler  = kwargs.pop("in_handler", None)
        self.out_handler = kwargs.pop("out_handler", None)
        # if self.in_handler and not isinstance(self.in_handler, types.FunctionType):
        #     raise Exception("in_handler should be function, but {} found.".format(type(self.in_handler)))
        # if self.out_handler and not isinstance(self.out_handler, types.FunctionType):
        #     raise Exception("out_handler should be function, but {} found.".format(type(self.out_handler)))
        super(ApiCharField, self).__init__(max_length=max_length, *args, **kwargs)


class ApiManyToManyField(ManyToManyField):

    def __init__(self, model, **kwargs):
        self.in_handler  = kwargs.pop("in_handler", None)
        self.out_handler = kwargs.pop("out_handler", None)
        # if self.in_handler and not isinstance(self.in_handler, types.FunctionType):
        #     raise Exception("in_handler should be function, but {} found.".format(type(self.in_handler)))
        # if self.out_handler and not isinstance(self.out_handler, types.FunctionType):
        #     raise Exception("out_handler should be function, but {} found.".format(type(self.out_handler)))
        super(ApiManyToManyField, self).__init__(model, **kwargs)
    
    def get_through_model(self):
        if not self.through_model:
            lhs, rhs = self.get_models()
            tables = [model._meta.table_name for model in (lhs, rhs)]

            class Meta:
                database = self.model._meta.database
                schema = self.model._meta.schema
                table_name = '%s_%s_through' % tuple(tables)
                indexes = (
                    ((lhs._meta.name, rhs._meta.name),
                     True),)

            attrs = {
                lhs._meta.name: ForeignKeyField(lhs, on_delete=self._on_delete,
                                                on_update=self._on_update),
                rhs._meta.name: ForeignKeyField(rhs, on_delete=self._on_delete,
                                                on_update=self._on_update)}
            attrs['Meta'] = Meta

            self.through_model = type(
                '%s%sThrough' % (lhs.__name__, rhs.__name__),
                (ApiModel,),
                attrs)

        return self.through_model
