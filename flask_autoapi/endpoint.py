from flask import request
from flask_restful import Resource, marshal_with
from flask_autoapi.utils.response import APIResponse, resource_fields

class BaseEndpoint(Resource):

    Model = None
    Type = "Single"
    decorators = [marshal_with(resource_fields)]

    @classmethod
    def add_decorators(cls, decorator_list):
        if not isinstance(decorator_list, (list, tuple)):
            raise Exception("格式错误")
        cls.decorators += decorator_list

    def get(self, id):
        """
        @api {GET} /api/{{ModelName.lower()}}/:id 获取{{Title}}详情
        @apiName Get{{ModelName}}
        @apiGroup {{Group}}

        @apiExample DATA
        {% for field in Fields %}
        {{ field.name }} {{field.field_type}} {% if field.verbose_name %} # {{field.verbose_name}} {% endif %}{% endfor %}

        @apiExample 返回值
        code    int
        message string
        data    DATA

        """
        r = self.Model.get_with_pk(id)
        r = r.to_json() if r else None
        return APIResponse(data=r)
    
    def post(self):
        """
        @api {POST} /api/{{ModelName.lower()}} 创建{{Title}}详情
        @apiName Create{{ModelName}}
        @apiGroup {{Group}}

        @apiExample DATA
        {% for field in Fields %}
        {{ field.name }} {{field.field_type}} {% if field.verbose_name %} # {{field.verbose_name}} {% endif %}{% endfor %}

        @apiExample 返回值
        code    int
        message string
        data    DATA
        """
        params = request.get_json() if request.content_type == "application/json" else request.form.to_dict()
        file_obj = request.files.get("file")
        fileid_field_name = self.Model.get_fileid_field_name()
        if file_obj and fileid_field_name:
            file_id, _ = save_file(file_obj)
            params[fileid_field_name] = file_id
        status = self.Model.verify_params(**params)
        if not status:
            return APIResponse(BAD_REQUEST)
        r = self.Model.create(**params)
        r.save()
        r = r.to_json() if r else None
        return APIResponse(data=r)
    
    def put(self, id):
        """
        @api {PUT} /api/{{ModelName.lower()}}/:id 更新{{Title}}
        @apiName Update{{ModelName}}
        @apiGroup {{Group}}

        @apiExample 参数
        {% for field in Fields %}
        {{ field.name }} {{field.field_type}} {% if field.verbose_name %} # {{field.verbose_name}} {% endif %}{% endfor %}

        @apiExample DATA
        {% for field in Fields %}
        {{ field.name }} {{field.field_type}} {% if field.verbose_name %} # {{field.verbose_name}} {% endif %}{% endfor %}

        @apiExample 返回值
        code    int
        message string
        data    DATA

        """
        params = request.get_json() if request.content_type == "application/json" else request.form.to_dict()
        if not params:
            return APIResponse(BAD_REQUEST)
        status = self.Model.verify_params(**params)
        if not status:
            return APIResponse(BAD_REQUEST)
        r = self.Model.update_by_pk(id, **params)
        r = r.to_json() if r else None
        return APIResponse(data=r)
    
    def delete(self, id):
        # self.Model.remove(id)
        self.Model.delete().where(self.Model._meta.primary_key == id).execute()
        return APIResponse()


class BaseListEndpoint(Resource):

    Model = None
    Type = "List"
    decorators = []

    @classmethod
    def add_decorators(cls, decorator_list):
        if not isinstance(decorator_list, (list, tuple)):
            raise Exception("格式错误")
        cls.decorators += decorator_list

    def get(self):
        """
        @apiName 获取{{Title}}列表
        @apiGroup {{Group}}

        @apiExample 返回值
        {
            "code": 0,
            "message": null,
            "data": [{{Data}}]
        }
        """
        args = request.args.to_dict()
        args = self.Model.verify_list_args(**args)
        if not args:
            return APIResponse(BAD_REQUEST)
        result = self.Model.list()
        for key, value in args.items():
            result = result.where(getattr(self.Model, key) == value)
        result = [r.to_json() for r in result] if result else None
        return APIResponse(data=result)