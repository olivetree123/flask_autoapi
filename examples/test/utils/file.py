import os

from utils.functions import content_md5


def save_file(file_obj):
    if not file_obj:
        return
    content = str(file_obj.read(), encoding="latin-1")
    hash_value = content_md5(content.encode("latin-1"))
    file_path = os.path.join("/data/", hash_value)
    with open(file_path, "wb") as f:
        f.write(bytes(content, encoding="latin-1"))
    return hash_value, file_path