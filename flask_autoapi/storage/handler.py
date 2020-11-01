import os
import requests

from flask_autoapi.utils.diyutils import content_md5


class StorageHandler(object):
    def __init__(self, client, bucket):
        self.client = client
        self.bucket = bucket


class FileHandler(StorageHandler):
    def write(self, file_obj):
        content = str(file_obj.read(), encoding="latin-1")
        md5_hash = content_md5(content.encode("latin-1"))
        file_path = os.path.join(self.bucket, md5_hash)
        with open(file_path, "wb") as f:
            f.write(bytes(content, encoding="latin-1"))
        return md5_hash

    def read(self, md5_hash):
        file_path = os.path.join(self.bucket, md5_hash)
        with open(file_path, "rb") as f:
            content = f.read()
        return content


class MinioHandler(StorageHandler):
    def write(self, file_obj):
        etag = None
        try:
            etag = self.client.put_object(
                bucket_name=self.bucket,
                object_name=file_obj.md5_hash,
                data=file_obj,
                length=file_obj.length,
            )
        except Exception as e:
            print("上传文件到 minio 失败，{}".format(e))
        return etag

    def read(self, md5_hash):
        r = self.client.get_object(
            bucket_name=self.bucket,
            object_name=md5_hash,
        )
        return r.read()


class QiniuHandler(StorageHandler):
    def write(self, file_obj):
        content = file_obj.read()
        token = self.client.upload_token(
            bucket=self.bucket,
            key=file_obj.md5_hash,
            expires=10,
        )
        r, info = self.client.put_data(
            token=token,
            key=file_obj.md5_hash,
            data=content,
        )
        return r["key"]

    def read(self, md5_hash):
        base_url = "http://{BUCKET_URL}/{KEY}".format(
            BUCKET_URL=self.bucket,
            KEY=md5_hash,
        )
        private_url = self.client.private_download_url(
            base_url,
            expires=10,
        )
        r = requests.get(private_url)
        if r.status_code != 200:
            raise Exception("获取七牛文件失败, status_code = {}".format(r.status_code))
        return r.content


class TencentHandler(StorageHandler):
    """腾讯云对象存储"""
    def write(self, file_obj):
        self.client.put_object(
            Bucket=self.bucket,
            Body=file_obj,
            Key=file_obj.md5_hash,
        )

    def read(self, md5_hash):
        r = self.client.get_object(
            Bucket=self.bucket,
            Key=md5_hash,
        )
        return r["Body"].get_stream_to_file(md5_hash)