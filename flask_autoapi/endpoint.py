
from flask import request
from flask_restful import Resource

class BaseEndpoint(Resource):

    Model = None
    Type = "Single"
    decorators = []

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
        {{ field.name }} {{field.field_type}} {% if field.help_text %} # {{field.help_text}} {% endif %}{% endfor %}

        @apiExample 返回值
        code    int
        message string
        data    DATA

        """
        r = self.Model.get_with_uid(id)
        r = r.to_json() if r else None
        return APIResponse(data=r)
    
    def post(self):
        """
        @apiName 创建{{Title}}
        @apiGroup {{Group}}

        @apiExample 返回值
        {
            "code": 0,
            "message": null,
            "data": {{Data}}
        }
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
        params = request.get_json() if request.content_type == "application/json" else request.form.to_dict()
        if not params:
            return APIResponse(BAD_REQUEST)
        status = self.Model.verify_params(**params)
        if not status:
            return APIResponse(BAD_REQUEST)
        r = self.Model.update_by_uid(id, **params)
        r = r.to_json() if r else None
        return APIResponse(data=r)
    
    def delete(self, id):
        self.Model.remove(id)
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