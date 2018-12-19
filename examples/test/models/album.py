#coding:utf-8
from peewee import CharField, BooleanField, IntegerField
from models import BaseModel


class Album(BaseModel):
    name      = CharField(null=False, index=True, verbose_name="相册名称")
    desc      = CharField(null=True, verbose_name="说明")
    cover     = CharField(null=True, verbose_name="封面")
    dirname   = CharField(null=True, verbose_name="存储目录")

    class Meta:
        group = "Album"
        # 指定别名，用于显示在 API 文档上。默认为 Model 的名称
        verbose_name = "相册"
        # list_fields 用于指定 list 接口的参数
        list_fields = ("dirname", )
