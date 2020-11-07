import os

from flask_autoapi.utils.diyutils import content_md5
from flask_autoapi.storage.handler import (FileHandler, MinioHandler,
                                           QiniuHandler, TencentHandler)
from flask_autoapi.storage.client import Client, MinioClient, QiniuClient, TencentClient


class FileObject(object):
    def __init__(self, obj=None, hash_value=None, storage=None):
        if not (obj or hash_value):
            raise ValueError("obj and hash_value both are None")
        self.obj = obj
        self.length = 0
        self.hash_value = hash_value
        self.storage = storage
        if not self.hash_value and self.obj:
            content = self.obj.read()
            self.length = len(content)
            self.hash_value = content_md5(content)
            self.obj.seek(0, os.SEEK_SET)

    def __str__(self):
        return self.hash_value

    def content(self):
        if self.obj:
            return self.obj.read()
        if self.storage:
            return self.storage.read(self)
        raise Exception("can not find content")


class Storage(object):
    def __init__(self, client: Client, bucket):
        if not isinstance(client, Client):
            raise TypeError("client should be type of Client")
        self.client = client
        self.bucket = bucket
        self.handler = self.client.handler_class(
            client=self.client,
            bucket=self.bucket,
        )

    def write(self, file_obj: FileObject):
        if not file_obj:
            return
        if not isinstance(file_obj, FileObject):
            raise TypeError("file_obj should be type of FileObject")
        # self._file_attrs(file_obj)
        return self.handler.write(file_obj)

    def read(self, file_obj):
        if not file_obj:
            return
        return self.handler.read(file_obj.hash_value)

    # def _file_attrs(self, file_obj):
    #     if not hasattr(file_obj, "hash_value"):
    #         content = file_obj.read()
    #         setattr(file_obj, "hash_value", content_md5(content))
    #         setattr(file_obj, "length", len(content))
    #         file_obj.seek(0, os.SEEK_SET)
