import os
import requests
from minio import Minio
from minio.error import ResponseError
from qiniu import Auth, put_data

from flask_autoapi.utils.diyutils import content_md5


class StorageHandler(object):
    def __init__(self, **kwargs):
        self.client = kwargs.get("client")
        self.bucket = kwargs.get("bucket")
        self.qiniu_bucket_url = kwargs.get("qiniu_bucket_url")
        if not self.bucket:
            raise Exception("bucket 不能为空")


class FileHandler(StorageHandler):
    
    def write(self, file_obj):
        content   = str(file_obj.read(), encoding="latin-1")
        md5_hash  = content_md5(content.encode("latin-1"))
        file_path = os.path.join(self.bucket, md5_hash)
        with open(file_path, "wb") as f:
            f.write(bytes(content, encoding="latin-1"))
        return md5_hash
    
    def read(self, md5_hash):
        file_path = os.path.join(self.bucket, md5_hash)
        content = b""
        with open(file_path, "rb") as f:
            content = f.read()
        return content


class MinioHandler(StorageHandler):

    def write(self, file_obj):
        etag = None
        try:
            etag = self.client.put_object(self.bucket, file_obj.md5_hash, file_obj, file_obj.length)
        except Exception as e:
            print("上传文件到 minio 失败，{}".format(e))
        return etag

    def read(self, md5_hash):
        r = self.client.get_object(self.bucket, md5_hash)
        return r.read()


class QiniuHandler(StorageHandler):

    def write(self, file_obj):
        content = file_obj.read()
        token = self.client.upload_token(self.bucket, file_obj.md5_hash, 10)
        r, info = put_data(token, file_obj.md5_hash, content)
        return r["key"]

    def read(self, md5_hash):
        base_url = "http://{BUCKET_URL}/{KEY}".format(BUCKET_URL=self.qiniu_bucket_url, KEY=md5_hash)
        private_url = self.client.private_download_url(base_url, expires=10)
        r = requests.get(private_url)
        if r.status_code != 200:
            raise Exception("获取七牛文件失败, status_code = {}".format(r.status_code))
        return r.content
