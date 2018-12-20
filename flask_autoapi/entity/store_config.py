

class StoreConfig(object):
    def __init__(self, 
                kind="", 
                file_folder="", 
                minio_url="", 
                minio_bucket="", 
                minio_secure=False,
                minio_access_key="", 
                minio_secret_key=""):
        if not kind in ("file", "minio"):
            raise Exception("存储方式只能是 file/minio，暂不支持 {}".format(kind))
        self.kind=kind
        self.file_folder = file_folder
        self.minio_url = minio_url
        self.minio_bucket = minio_bucket
        self.minio_secure = minio_secure
        self.minio_access_key = minio_access_key
        self.minio_secret_key = minio_secret_key
        self._is_valid()
    
    def _is_valid(self):
        # 验证配置的完整性
        if self.kind == "file" and self.file_folder:
            return True
        elif self.kind == "minio" and \
            self.minio_url and \
            self.minio_bucket and \
            self.minio_access_key and \
            self.minio_secret_key:
            return True
        raise Exception("配置错误")