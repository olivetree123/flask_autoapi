=============
Flask AutoAPI
=============
Flask AutoAPI 是一个 flask 扩展，根据模型自动生成 API 接口和文档。

API 接口基于 flask_restful 和 peewee，文档使用 ApiDoc 生成。


安装
=============
    npm install apidoc -g
    
    pip install flask-autoapi


存储
=============
FileIDField 可以自动处理请求中的文件，你只需要在 Model 的 Meta中配置好存储的方式。建议在模型基类中进行配置。

同时，还支持将文本转存成文件，当用户通过 get 接口获取信息时，又会自动将文件转成文本返回，对用户完全透明。

目前支持3种存储方式，分别为 文件存储、Minio 对象存储和七牛对象存储。

存储配置方式
::

    class BaseModel(ApiModel):
        class Meta:
            database = db     
            # 文件存储配置
            # store_kind = "file"
            # 在文件存储中，bucket 为文件夹路径
            # bucket = "/Users/gao/code/iLearning"

            # minio 存储配置        
            bucket = "blog"
            minio_url = ""
            minio_access_key = ""
            minio_secret_key = ""

            # qiniu 存储配置
            # store_kind = "qiniu"
            # bucket = "blog"
            # qiniu_url = ""
            # qiniu_access_key = ""
            # qiniu_secret_key = ""
            # qiniu_bucket_url = ""



存储使用方式
::

    cover = FileIDField(null=False, verbose_name="封面", source_name="cover", source_type="file")

* source_name

  该属性表示发送请求时的参数名称，参数名称可以与Field 名称不一致。默认值为 Field 名称。

* source_type

  发送请求时参数的类型，允许的值为 file/string。默认为 file。


文档
=============
借助于 ApiDoc，只需一条命令便可生成文档
::

    python index.py doc

我们对文档做了大量优化，看起来更舒服。

TODO  
=============
1. 存储分离出去  
2. EndPiont 重载    √  
3. 允许修改字段的值   √
4. 返回时过滤掉不需要的字段     √  
5. 有些字段不需要出现在文档上   √  
6. MethodField     √
7. list 接口分页    √
8. 记录所有 POST/PUT/DELETE 操作的日志
9. 入库之前，用户可能需要有自定义的操作     √
10. 对于 unique key，应该禁止插入相同的数据，但不应该500
11. 支持 mini_json，该方法不处理 ApiMethodField 和 ApiManyToManyField
12. 支持自定义 serialize
13. ApiFileIDField 字段支持搜索（仅针对文本文件或字符串）