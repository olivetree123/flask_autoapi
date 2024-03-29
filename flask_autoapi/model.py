import uuid
import werkzeug
from io import BytesIO
from datetime import datetime
from playhouse.shortcuts import model_to_dict
from peewee import (
    Model,
    CharField,
    ManyToManyField,
    ForeignKeyField,
    Field,
    FieldAccessor,
    MetaField,
    Metadata,
    AutoField,
    DateTimeField,
    IntegerField,
    MySQLDatabase,
)

from flask_autoapi.storage import FileObject
from flask_autoapi.utils.diyutils import (
    field_to_json,
    content_md5,
    get_uuid,
)

MySQLDatabase.field_types["OBJECT"] = "VARCHAR"


def api_model_to_dict(obj, **kwargs):
    data = model_to_dict(obj, **kwargs)
    method_fields = list(obj._meta.method_fields.values())
    for field in method_fields:
        data[field.name] = getattr(obj, field.name)
    return data


class MethodClass(object):

    def get(self, obj):
        raise NotImplementedError("get function should be implemented.")

    def get_example(self):
        raise NotImplementedError(
            "get_example function should be implemented.")


class ApiMethodField(MetaField):
    """
    A readonly field, get value by object method.
    """
    field_type = "METHOD"

    def __init__(self, method_class, verbose_name=None):
        self.choices = None
        self.read_only = True
        self.method_class = method_class
        self.verbose_name = verbose_name
        if not self.method_class:
            raise Exception("method_class should not be None.")
        if not issubclass(self.method_class, MethodClass):
            raise Exception(
                "method_class should not be subclass of MethodClass.")


class ApiMetadata(Metadata):

    def __init__(self, model, **kwargs):
        self.method_fields = {}
        self.display_id = None
        super(ApiMetadata, self).__init__(model, **kwargs)

    def add_field(self, field_name, field, set_attribute=True):
        super(ApiMetadata, self).add_field(field_name, field, set_attribute)
        if isinstance(field, ApiMethodField) and field.name:
            self.add_method_field(field)
        if self.display_id and field.display_id:
            raise AttributeError("duplicate display_id setting")
        if hasattr(field, "display_id") and field.display_id:
            self.display_id = field

    def add_method_field(self, field):
        self.method_fields[field.name] = field


class ApiModel(Model):

    @classmethod
    def set_meta(cls, **kwargs):
        for key, value in kwargs.items():
            setattr(cls._meta, key, value)

    @classmethod
    def get_with_pk(cls, pk_value, without_field_names=None):
        if without_field_names and not isinstance(without_field_names,
                                                  (list, tuple)):
            return None
        fields = cls.get_fields()
        fields = [field for field in fields if field.name not in without_field_names] \
                    if without_field_names else fields
        pk = cls._meta.primary_key if not cls._meta.display_id else cls._meta.display_id
        return cls.select(*fields).where(pk == pk_value).first()

    @classmethod
    def get_field_names(cls):
        return cls._meta.sorted_field_names

    @classmethod
    def get_all_field_names(cls):
        all_fields = cls.get_fields() + list(cls._meta.manytomany.values())
        return [field.name for field in all_fields]

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
    def get_post_fields(cls):
        fields = cls.get_fields()
        fields = [
            field for field in fields if not getattr(field, "read_only", False)
        ]
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
            if not (hasattr(field, "in_handler") and field.in_handler):
                continue
            handler = field.in_handler
            # handler = getattr(cls, field.in_handler)
            # if not (handler and isinstance(handler, types.MethodType)):
            #     raise Exception(
            #         "in_handler should be function, but {} found.".format(
            #             type(handler)))
            params[field.name] = handler(params.get(field.name))
            if field.name in cls._meta.manytomany:
                params[field.name + "_value"] = params.pop(field.name)
        return params

    def mtom(self, **params):
        for field_name, field in self._meta.manytomany.items():
            ins = getattr(self, field_name)
            ins.clear()
            value = params[field_name + "_value"]
            if isinstance(value, (list, tuple)):
                for v in value:
                    ins.add(v)
            else:
                ins.add(value)

    @classmethod
    def out_handlers(cls, **data):
        # 对 json() 之后的结果进行处理
        fields = cls.get_fields() + list(cls._meta.manytomany.values())
        for field in fields:
            if not (hasattr(field, "out_handler")
                    and getattr(field, "out_handler")):
                continue
            # handler = getattr(cls, field.out_handler)
            # if not (handler and isinstance(handler, types.MethodType)):
            #     raise Exception(
            #         "out_handler should be MethodType, but {} found.".format(
            #             type(handler)))
            handler = field.out_handler
            data[field.name] = handler(data.get(field.name))
        return data

    @classmethod
    def format_params(cls, **params):
        # all_field_names = cls.get_all_field_names()
        # for key in list(params.keys()):
        #     if key in all_field_names:
        #         continue
        #     params.pop(key)
        # 格式化参数，主要是将 str 转换成 file 对象
        fields = cls.get_fields()
        for field in fields:
            if isinstance(field, ApiFileField):
                if field.source_type == "string":
                    content = params.get(field.name)
                    if not content:
                        continue
                    if not isinstance(content, (str, bytes)):
                        raise Exception("{} 应该为 str 或 bytes，而不是 {}".format(
                            field.name, type(content)))
                    if isinstance(content, str):
                        content = content.encode("utf8")
                    f = BytesIO(content)
                    setattr(f, "hash_value", content_md5(content))
                    setattr(f, "length", len(content))
                    params[field.name] = FileObject(f)
                elif field.source_type == "file":
                    f = params.get(field.name)
                    if not isinstance(
                            f,
                        (werkzeug.datastructures.FileStorage, type(None))):
                        raise Exception(
                            "类型错误，{} 应该为 werkzeug.datastructures.FileStorage 类型，而不是 {}"
                            .format(field.name, type(f)))
                    params[field.name] = FileObject(f)
                else:
                    raise Exception("不能识别的类型, 无法转换，source_type = {}".format(
                        field.source_type))
        return params

    def get_method_fields(self):
        fields = list(self._meta.method_fields.values())
        for field in fields:
            r = field.method_class.get(self)
            setattr(self, field.name, r)
        return self

    @classmethod
    def verify_params(cls, **params):
        # 验证 params 中的参数，主要验证非 None 字段是否有值
        fields = cls.get_fields()
        for field in fields:
            if field.auto_increment or field.default is not None or field.null:
                continue
            if params.get(field.name) is None:
                raise ValueError("{} should not be None".format(field.name))
        return True

    @classmethod
    def upload_files(cls, **params):
        # cls.init_storage()
        fields = cls.get_fields()
        for field in fields:
            if not params.get(field.name):
                continue
            if isinstance(field, ApiFileField):
                file_id = cls._meta.storage.write(params[field.name])
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
            if isinstance(field, ApiFileField) and not params.get(field.name):
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
            if not key in field_names or cls.get_field_by_name(
                    key).primary_key:
                continue
            setattr(r, key, value)
        r.save()
        return r

    @classmethod
    def diy_before_save(cls, request, **params) -> bool:
        """
        用于 POST/PUT 方法。
        做一些自定义操作，但是不能修改参数。
        修改参数应该使用各个Field 的 in_handler。                        
        """
        return True

    @classmethod
    def diy_after_save(cls, obj) -> bool:
        """
        用于 POST/PUT 方法。
        create/save/update 之后，自定义操作。
        """
        return True

    @classmethod
    def validate_for_get(cls, request, pk_value) -> bool:
        """
        用于 GET 方法
        """
        return True

    @classmethod
    def validate_for_put(cls, request, pk_value, **params) -> bool:
        """
        用于 PUT 方法
        """
        return True

    @classmethod
    def validate_for_post(cls, request, **params) -> bool:
        """
        用于 POST 方法
        """
        return True

    @classmethod
    def validate_for_delete(cls, request, pk_value) -> bool:
        """
        用于 DELETE 方法
        """
        return True

    @classmethod
    def diy_after_get(cls, **json_data):
        """
        在 GET 方法中获取到对象并转换为 json 之后，对返回值做一些操作。
        """
        return json_data

    @classmethod
    def json(cls,
             obj,
             without_fields=None,
             datetime_format="%Y-%m-%d %H:%M:%S"):
        fields = cls.get_fields()
        # for field in fields:
        #     # 如果数据源为 string，则返回时也应该返回 string
        #     if hasattr(field, "source_type") and field.source_type == "string" and getattr(obj, field.name):
        #         content = cls._meta.storage.read(getattr(obj, field.name))
        #         setattr(obj, field.name, content)
        # to json
        r = api_model_to_dict(obj, manytomany=cls._meta.manytomany)
        # 将 many-to-many 的数据取出来
        # for field_name, field in cls._meta.manytomany.items():
        #     r[field_name] = [model_to_dict(x) for x in getattr(obj, field_name)]
        # 过滤掉不需要的字段
        result = {}
        for name, value in r.items():
            field = cls.get_field_by_name(name)
            if field._hidden:
                continue
            if without_fields and name in without_fields:
                continue
            result[name] = field_to_json(value, datetime_format)
        return result

    class Meta:
        model_metadata_class = ApiMetadata
        group = ""
        # verbose_name 指定别名，用于显示在 API 文档上。默认为 Model 的名称
        verbose_name = ""
        # filter_fields 用于指定 list 接口的参数
        filter_fields = ()
        api_methods = ("GET", "POST", "PUT", "DELETE", "LIST")
        # api_methods = ()
        api_decorator_list = ()
        api_method_decorators = None
        list_api_decorator_list = ()
        list_api_method_decorators = None
        # storage 是 Storage 的对象
        storage = None


class ApiField(object):

    def custom_fields(self, kwargs):
        self.read_only = kwargs.pop("read_only", False)
        self.display_id = kwargs.pop("display_id", False)
        self.in_handler = kwargs.pop("in_handler", False)
        self.out_handler = kwargs.pop("out_handler", False)


class ApiFileField(CharField):
    field_type = "OBJECT"

    def __init__(self, max_length=255, *args, **kwargs):
        self.source_name = kwargs.pop("source_name", "file")
        self.source_type = kwargs.pop("source_type", "file")
        super(ApiFileField, self).__init__(max_length=max_length,
                                           *args,
                                           **kwargs)

    def db_value(self, file_obj: FileObject) -> str:
        if not isinstance(file_obj, FileObject):
            raise TypeError("file_obj should be type of FileObject")
        # 写数据库时会使用该函数返回的值，但是并不会修改参数的值
        r = self.model._meta.storage.write(file_obj)
        return r

    def python_value(self, value) -> FileObject:
        # just for select sql
        # content = self.model._miuyeta.storage.read(value)
        # return content
        return FileObject(hash_value=value, storage=self.model._meta.storage)


class ApiCharField(CharField, ApiField):

    def __init__(self, max_length=255, *args, **kwargs):
        self.custom_fields(kwargs)
        super(ApiCharField, self).__init__(max_length=max_length,
                                           *args,
                                           **kwargs)


class ApiManyToManyField(ManyToManyField):

    def __init__(self, model, **kwargs):
        self.in_handler = kwargs.pop("in_handler", None)
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
                indexes = (((lhs._meta.name, rhs._meta.name), True), )

            attrs = {
                lhs._meta.name:
                ForeignKeyField(lhs,
                                on_delete=self._on_delete,
                                on_update=self._on_update),
                rhs._meta.name:
                ForeignKeyField(rhs,
                                on_delete=self._on_delete,
                                on_update=self._on_update)
            }
            attrs['Meta'] = Meta

            self.through_model = type(
                '%s%sThrough' % (lhs.__name__, rhs.__name__), (ApiModel, ),
                attrs)

        return self.through_model


class ApiUUIDField(ApiField, Field):
    field_type = "char(32)"

    def __init__(self, **kwargs):
        self.custom_fields(kwargs)
        super(ApiUUIDField, self).__init__(**kwargs)

    def db_value(self, value):
        if not isinstance(value, (str, uuid.UUID)):
            return value
        if isinstance(value, str):
            # value = uuid.UUID(value)
            try:
                value = uuid.UUID(value)  # convert hex string to UUID
            except Exception as e:
                print("Failed to convert value {} to uuid".format(value))
        value = value.hex if isinstance(value, uuid.UUID) else str(
            value)  # convert UUID to hex string.
        return value

    def python_value(self, value):
        value = uuid.UUID(value).hex
        return value


class ApiAutoField(ApiField, AutoField):

    def __init__(self, *args, **kwargs):
        self.custom_fields(kwargs)
        super(ApiAutoField, self).__init__(*args, **kwargs)


class ApiDateTimeField(DateTimeField, ApiField):

    def __init__(self, *args, **kwargs):
        self.custom_fields(kwargs)
        super(ApiDateTimeField, self).__init__(*args, **kwargs)


class ApiIntegerField(IntegerField, ApiField):

    def __init__(self, *args, **kwargs):
        self.custom_fields(kwargs)
        super(ApiIntegerField, self).__init__(*args, **kwargs)


class ApiBaseModel(ApiModel):
    id = ApiAutoField(verbose_name="id",
                      read_only=True,
                      _hidden=True,
                      primary_key=True)
    uid = ApiUUIDField(verbose_name="uid",
                       default=get_uuid,
                       unique=True,
                       read_only=True,
                       display_id=True)
    created = ApiDateTimeField(default=datetime.now,
                               verbose_name="Create Time",
                               read_only=True)
    updated = ApiDateTimeField(default=datetime.now,
                               verbose_name="Update Time",
                               read_only=True)
