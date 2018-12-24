import os
from minio import Minio
from minio.error import ResponseError

from flask_autoapi.entity.store_config import StoreConfig


def put_object(file_obj, store_config):
    if not isinstance(store_config, StoreConfig):
        raise Exception("store_config 应该是 StoreConfig 类型，而不是 {}".format(type(store_config)))
    etag = None
    try:
        client = Minio(store_config.minio_url,
                        access_key=store_config.minio_access_key,
                        secret_key=store_config.minio_secret_key,
                        secure=store_config.minio_secure
        )
        file_obj.seek(0, os.SEEK_END)
        length = file_obj.tell()
        file_obj.seek(0, os.SEEK_SET)
        etag = client.put_object(store_config.bucket, file_obj.name, file_obj, length)
    except Exception as e:
        print("上传文件到minio 失败，{}".format(e))
    return etag
        
    