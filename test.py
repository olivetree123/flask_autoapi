from flask import Flask
from flask_script import Manager
from peewee import MySQLDatabase
from peewee import CharField, BooleanField, IntegerField

from flask_autoapi import AutoAPI
from flask_autoapi.model import ApiModel, FileIDField
from flask_autoapi.command import GenerateDoc


db = MySQLDatabase(
    "test", 
    host="localhost", 
    port=3306, 
    user="root", 
    password="gaojian"
)

class Album(ApiModel):
    name      = CharField(null=False, index=True, verbose_name="相册名称")
    desc      = CharField(null=True, verbose_name="说明")
    cover     = CharField(null=True, verbose_name="封面")
    dirname   = CharField(null=True, verbose_name="存储目录")
    file_id   = FileIDField(null=True)

    class Meta:
        database = db
        group = "Album"
        # 指定别名，用于显示在 API 文档上。默认为 Model 的名称
        verbose_name = "相册"
        # filter_fields 用于指定 list 接口的参数
        filter_fields = ("dirname", "name", )

        # 文件存储配置
        file_store = "qiniu"
        bucket = "gaojian"

        # minio 配置
        # file_store = "minio"
        # minio_url = ""
        # minio_bucket = ""
        # minio_access_key = ""
        # minio_secret_key = ""

        # qiniu 配置
        qiniu_url = ""
        qiniu_access_key = ""
        qiniu_secret_key = ""


MODEL_LIST = [Album, ]
db.create_tables(MODEL_LIST)

if __name__ == "__main__":
    app = Flask(__name__)
    api = AutoAPI()
    api.init_app(app, MODEL_LIST)

    manager = Manager(app)
    manager.add_command("doc", GenerateDoc(MODEL_LIST))
    manager.run()