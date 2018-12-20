import os
from flask_autoapi.utils.diyutils import content_md5

from flask_autoapi.utils.minio import put_object
from flask_autoapi.utils.qiniu import qiniu_put_object
from flask_autoapi.entity.store_config import StoreConfig


def save_file(file_obj, store_config):
    if not isinstance(store_config, StoreConfig):
        raise Exception("store_config 应该是 StoreConfig 类型，而不是 {}".format(type(store_config)))
    if not file_obj:
        return
    if store_config.kind == "file":
        content   = str(file_obj.read(), encoding="latin-1")
        md5_hash  = content_md5(content.encode("latin-1"))
        file_path = os.path.join(store_config.file_folder, md5_hash)
        with open(file_path, "wb") as f:
            f.write(bytes(content, encoding="latin-1"))
        return md5_hash
    elif store_config.kind == "minio":
        return put_object(file_obj, store_config)
    elif store_config.kind == "qiniu":
        return qiniu_put_object(file_obj, store_config)