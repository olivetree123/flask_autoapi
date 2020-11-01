from flask_autoapi.storage.handler import (FileHandler, MinioHandler,
                                           QiniuHandler, TencentHandler)


class Client(object):
    def __init__(self):
        self.conn = None
        self.kind = None
        self.handler_class = None

    def __getattribute__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        return getattr(self.conn, name)


class FileClient(Client):
    pass


class MinioClient(Client):
    def __init__(self, url, access_key, secret_key, secure):
        from minio import Minio
        self.kind = "minio"
        self.conn = Minio(
            url,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.handler_class = MinioHandler


class QiniuClient(Client):
    """七牛对象存储"""
    def __init__(self, url, access_key, secret_key):
        from qiniu import Auth, put_data
        self.kind = "qiniu"
        self.conn = Auth(access_key, secret_key)
        self.qiniu_url = url
        self.put_data = put_data
        self.handler_class = QiniuHandler


class TencentClient(Client):
    """腾讯云对象存储"""
    def __init__(self, secret_id, secret_key, region):
        from qcloud_cos import CosConfig
        from qcloud_cos import CosS3Client
        self.kind = "tencent"
        config = CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key,
        )
        self.conn = CosS3Client(config)
        self.handler_class = TencentHandler
