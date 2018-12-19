"""
        @api {GET} /api/album/:id 获取相册详情
        @apiName GetAlbum
        @apiGroup Album

        @apiExample DATA
        
        uid char(32) 
        status BOOL  # 0 delete, 1 normal 
        create_time DATETIME 
        name VARCHAR 
        desc VARCHAR 
        cover VARCHAR 
        dirname VARCHAR 

        @apiExample 返回值
        code    int
        message string
        data    DATA

        
"""
"""
        @api {GET} /api/audio/:id 获取详情
        @apiName GetAudio
        @apiGroup Audio

        @apiExample DATA
        
        uid char(32) 
        status BOOL  # 0 delete, 1 normal 
        create_time DATETIME 
        file_id VARCHAR 
        duration INT 

        @apiExample 返回值
        code    int
        message string
        data    DATA

        
"""
