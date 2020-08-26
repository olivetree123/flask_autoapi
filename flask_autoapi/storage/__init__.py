import os
from minio import Minio

from flask_autoapi.utils.diyutils import content_md5
from flask_autoapi.storage.handler import FileHandler, MinioHandler, QiniuHandler


class Storage(object):
    def __init__(self, 
                kind="", 
                bucket="", 
                minio_url="", 
                minio_secure=False,
                minio_access_key="", 
                minio_secret_key="",
                qiniu_url = "",
                qiniu_access_key = "",
                qiniu_secret_key = "",
                qiniu_bucket_url = ""):
        if not kind in ("file", "minio", "qiniu"):
            raise Exception("存储方式只能是 file/minio/qiniu，暂不支持 {}".format(kind))
        self.kind=kind
        self.bucket = bucket
        self.minio_url = minio_url
        self.minio_secure = minio_secure
        self.minio_access_key = minio_access_key
        self.minio_secret_key = minio_secret_key
        self.qiniu_url = qiniu_url
        self.qiniu_access_key = qiniu_access_key
        self.qiniu_secret_key = qiniu_secret_key
        self.qiniu_bucket_url = qiniu_bucket_url
        self.client = None
        self.handler_class = None
        self._is_valid()
        self._connect()
        
    
    def _is_valid(self):
        # 验证配置的完整性
        if self.kind == "file" and self.bucket:
            return True
        elif self.kind == "minio" and \
            self.minio_url and \
            self.bucket and \
            self.minio_access_key and \
            self.minio_secret_key:
            return True
        elif self.kind == "qiniu" and \
            self.qiniu_url and \
            self.bucket and \
            self.qiniu_access_key and \
            self.qiniu_secret_key and \
            self.qiniu_bucket_url:
            return True
        raise Exception("配置错误")
    
    def _connect(self):
        if self.kind == "minio":
            self.handler_class = MinioHandler
            self.client = Minio(self.minio_url,
                                access_key=self.minio_access_key,
                                secret_key=self.minio_secret_key,
                                secure=self.minio_secure
                )
        elif self.kind == "qiniu":
            self.handler_class = QiniuHandler
            self.client = Auth(self.qiniu_access_key, self.qiniu_secret_key)
        elif self.kind == "file":
            self.handler_class = FileHandler
        self.handler = self.handler_class(
            client=self.client, 
            bucket=self.bucket, 
            qiniu_bucket_url=self.qiniu_bucket_url
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

