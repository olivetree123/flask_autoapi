from peewee import CharField, BooleanField, IntegerField
from flask_autoapi.model import FileIDField
from models import BaseModel


class Audio(BaseModel):
    # file_id 为云存储中文件的 id
    # 你应该总是使用云存储来存储文件
    # 任何模型，需要存储文件 id 时，总是应该使用 file_id 字段
    file_id = FileIDField(null=True)
    duration = IntegerField(null=True)

    class Meta:
        group = "Audio"
        # 指定别名，用于显示在 API 文档上。默认为 Model 的名称
        # verbose_name = "音频"
