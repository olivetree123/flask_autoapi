from qiniu import Auth, put_data, etag

from flask_autoapi.entity.store_config import StoreConfig

def qiniu_put_object(file_obj, store_config):
    if not isinstance(store_config, StoreConfig):
        raise Exception("store_config 应该是 StoreConfig 类型，而不是 {}".format(type(store_config)))
    q = Auth(store_config.qiniu_access_key, store_config.qiniu_secret_key)
    token = q.upload_token(store_config.bucket, file_obj.name, 3600)
    r, info = put_data(token, file_obj.name, file_obj.read())
    return r["hash"]