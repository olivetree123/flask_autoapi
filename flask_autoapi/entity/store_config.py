

class StoreConfig(object):
    def __init__(self, 
                kind="", 
                bucket="", 
                minio_url="", 
                minio_secure=False,
                minio_access_key="", 
                minio_secret_key="",
                qiniu_url = "",
                qiniu_access_key = "",
                qiniu_secret_key = ""):
        if not kind in ("file", "minio", "qiniu"):
            raise Exception("存储方式只能是 file/minio，暂不支持 {}".format(kind))
        self.kind=kind
        self.bucket = bucket
        self.minio_url = minio_url
        self.minio_secure = minio_secure
        self.minio_access_key = minio_access_key
        self.minio_secret_key = minio_secret_key
        self.qiniu_url = qiniu_url
        self.qiniu_access_key = qiniu_access_key
        self.qiniu_secret_key = qiniu_secret_key
        self._is_valid()
    
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
            self.qiniu_secret_key:
            return True
        raise Exception("配置错误")