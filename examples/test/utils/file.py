import os

from utils.functions import content_md5


def save_file(file_obj):
    if not file_obj:
        return
    content   = str(file_obj.read(), encoding="latin-1")
    md5_hash  = content_md5(content.encode("latin-1"))
    file_path = os.path.join("/data/", md5_hash)
    with open(file_path, "wb") as f:
        f.write(bytes(content, encoding="latin-1"))
    return md5_hash, file_path