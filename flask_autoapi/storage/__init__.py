import os

from flask_autoapi.utils.diyutils import content_md5
from flask_autoapi.storage.handler import (FileHandler, MinioHandler,
                                           QiniuHandler, TencentHandler)
from flask_autoapi.storage.client import Client, MinioClient, QiniuClient, TencentClient


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

    def write(self, file_obj):
        if not file_obj:
            return
        self._file_attrs(file_obj)
        return self.handler.write(file_obj)

    def read(self, md5_hash):
        if not md5_hash:
            return
        return self.handler.read(md5_hash)

    def _file_attrs(self, file_obj):
        if not hasattr(file_obj, "md5_hash"):
            content = file_obj.read()
            setattr(file_obj, "md5_hash", content_md5(content))
            setattr(file_obj, "length", len(content))
            file_obj.seek(0, os.SEEK_SET)
