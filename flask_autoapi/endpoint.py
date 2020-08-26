import math
from flask import request
from flask_restful import Resource, marshal_with

from flask_autoapi.utils.response import JsonResponse, resource_fields
from flask_autoapi.utils.message import BAD_REQUEST, OBJECT_SAVE_FAILED

class BaseEndpoint(Resource):

    Model = None
    Type = None
    # 由于 method_decorators 是内层装饰器，比 decorators 先起作用，所以一律使用 method_decorators
    decorators = []
    method_decorators = {
        "get":      [marshal_with(resource_fields)], 
        "put":      [marshal_with(resource_fields)],
        "post":     [marshal_with(resource_fields)],
        "delete":   [marshal_with(resource_fields)],
        "options":  [marshal_with(resource_fields)],
    }

    @classmethod
    def add_decorators(cls, decorator_list):
        if not decorator_list:
            return
        if not isinstance(decorator_list, (list, tuple)):
            raise Exception("TypeError, decorator_list should be list or tuple, but {} found".format(type(decorator_list)))
        cls.decorators += decorator_list
    
    @classmethod
    def add_method_decorators(cls, method_decorators):
        if not method_decorators:
            return
        if not isinstance(method_decorators, dict):
            raise Exception("TypeError, method_decorators should be dict, but {} found, endpoint = {}".format(type(method_decorators), cls))
        for key, value in method_decorators.items():
            cls.method_decorators[key] += value

    def get(self, id):
        """
        @api {GET} /{{project_name}}/{{ModelName.lower()}}/:id 获取{{Title}}详情
        @apiName Get{{ModelName}}
        @apiGroup {{Group}}

        @apiExample 返回值
{{ DATA}}

        """
        without_fields = request.args.get("without_fields")
        without_fields = without_fields.split(",") if without_fields else None
        r = self.Model.get_with_pk(id, without_fields)
        if not r:
            return JsonResponse()
        r.get_method_fields()
        r = self.Model.to_json(r, without_fields) if r else None
        r = self.Model.out_handlers(**r)
        r = self.Model.diy_after_get(**r)
        return JsonResponse(data=r)
    
    def post(self):
        """
        @api {POST} /{{project_name}}/{{ModelName.lower()}} 创建{{Title}}
        @apiName Create{{ModelName}}
        @apiGroup {{Group}}

        @apiExample 参数
        {%- for field in Fields %}
        {{ str_align(standard_type(field.field_type))}} \t {{ str_align(field.name, 15) }}  # {% if field.null is sameas true %} 非必填项 {% else %} 必填项 {% endif %} {% if field.verbose_name %}, {{field.verbose_name}} {% endif %}{% endfor %}
        

        @apiExample 返回值
{{ DATA}}

        """
        params = request.get_json() if request.content_type == "application/json" else request.form.to_dict()
        params.update(request.files.to_dict())
        params = self.Model.in_handlers(**params)
        params = self.Model.format_params(**params)
        status = self.Model.verify_params(**params)
        if not status:
            return JsonResponse(BAD_REQUEST)
        params = self.Model.upload_files(**params)
        if not self.Model.validate(**params):
            return JsonResponse(BAD_REQUEST)
        self.Model.diy_before_save(**params)
        r = self.Model.create(**params)
        self.Model.diy_after_save(r)
        r.mtom(**params)
        r.get_method_fields()
        r = self.Model.to_json(r) if r else None
        r = self.Model.out_handlers(**r)
        r = self.Model.diy_after_get(**r)
        return JsonResponse(data=r)
    
    def put(self, id):
        """
        @api {PUT} /{{project_name}}/{{ModelName.lower()}}/:id 更新{{Title}}
        @apiName Update{{ModelName}}
        @apiGroup {{Group}}

        @apiExample 参数
        {%- for field in Fields %}
        {{ str_align(standard_type(field.field_type))}} \t {{ str_align(field.name, 15) }}  # {% if field.null is sameas true %} 非必填项 {% else %} 必填项 {% endif %} {% if field.verbose_name %}, {{field.verbose_name}} {% endif %}{% endfor %}

        @apiExample 返回值
{{ DATA}}
        
        """
        params = request.get_json() if request.content_type == "application/json" else request.form.to_dict()
        params.update(request.files.to_dict())
        params = self.Model.in_handlers(**params)
        params = self.Model.format_params(**params)
        status = self.Model.verify_params(**params)
        if not status:
            return JsonResponse(BAD_REQUEST)
        params = self.Model.upload_files(**params)
        if not self.Model.validate(**params):
            return JsonResponse(BAD_REQUEST)
        self.Model.diy_before_save(**params)
        r = self.Model.update_by_pk(id, **params)
        self.Model.diy_after_save(r)
        r.mtom(**params)
        r.get_method_fields()
        r = self.Model.to_json(r) if r else None
        r = self.Model.out_handlers(**r)
        r = self.Model.diy_after_get(**r)
        return JsonResponse(data=r)
    
    def delete(self, id):
        """
        @api {DELETE} /{{project_name}}/{{ModelName.lower()}}/:id 删除{{Title}}
        @apiName Delete{{ModelName}}
        @apiGroup {{Group}}

        @apiExample 返回值
        {
            "code": 0,
            "message": "",
            "data": None,
        }
        
        """
        self.Model.delete().where(self.Model._meta.primary_key == id).execute()
        return JsonResponse()


class BaseListEndpoint(Resource):

    Model = None
    Type = "List"
    decorators = []
    method_decorators = {
        "get":      [marshal_with(resource_fields)], 
        "put":      [marshal_with(resource_fields)],
        "post":     [marshal_with(resource_fields)],
        "delete":   [marshal_with(resource_fields)],
        "options":  [marshal_with(resource_fields)],
    }

    @classmethod
    def add_decorators(cls, decorator_list):
        if not decorator_list:
            return
        if not isinstance(decorator_list, (list, tuple)):
            raise Exception("格式错误")
        cls.decorators += decorator_list
    
    @classmethod
    def add_method_decorators(cls, method_decorators):
        if not method_decorators:
            return
        if not isinstance(method_decorators, dict):
            raise Exception("TypeError, method_decorators should be dict, but {} found".format(type(method_decorators)))
        for key, value in method_decorators.items():
            cls.method_decorators[key] += value

    def get(self):
        """
        @api {GET} /{{project_name}}/{{ModelName.lower()}}/list?page=2&page_size=10&order=0 获取{{Title}}列表
        @apiName Get{{ModelName}}List
        @apiGroup {{Group}}

        @apiExample 参数
        int    page    # 页码。非必填，默认1。
        int    page_size     # 每页数量。非必填，默认10。
        int    order   # 排序方法。非必填，默认0。0表示按时间倒序，1表示按时间顺序。

        @apiExample 返回值
{{LIST_DATA}}
        """
        args = request.args.to_dict()
        try:
            page  = int(args.get("page", 1))
            page_size   = int(args.get("page_size", 10))
            order = int(args.get("order", 0))
        except:
            return JsonResponse(BAD_REQUEST)
        if not order in (0, 1):
            return JsonResponse(BAD_REQUEST)
        args = self.Model.verify_list_args(**args)
        without_fields = request.args.get("without_fields")
        without_fields = without_fields.split(",") if without_fields else None
        fields = self.Model.get_fields()
        fields = [field for field in fields if field.name not in without_fields] \
                    if without_fields else fields
        result = self.Model.select(*fields)
        for key, value in args.items():
            if value.find("~") >= 0:
                a, b = value.split("~")
                a = a.strip()
                b = b.strip()
                if a:
                    result = result.where(getattr(self.Model, key) >= a)
                if b:
                    result = result.where(getattr(self.Model, key) <= b)
            else:
                result = result.where(getattr(self.Model, key) == value)
        result = result.order_by(self.Model.create_time.desc()) if order == 0 else result.order_by(self.Model.create_time.asc())
        total_count = result.count()
        result = result.offset((page-1)*page_size).limit(page_size)
        result = [self.Model.to_json(r.get_method_fields(), without_fields) for r in result] if result else None
        result = [self.Model.out_handlers(**r) for r in result] if result else None
        result = [self.Model.diy_after_get(**r) for r in result] if result else None
        result = {
            "page_size":page_size,
            "total": total_count,
            "page": page,
            "result":result
        }
        return JsonResponse(data=result)
        