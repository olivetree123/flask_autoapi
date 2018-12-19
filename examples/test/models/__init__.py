from flask_autoapi.model import ApiModel

from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_DB


db = MySQLDatabase(
    MYSQL_DB, 
    host=MYSQL_HOST, 
    port=MYSQL_PORT, 
    user=MYSQL_USER, 
    password=MYSQL_PASSWORD
)


class BaseModel(ApiModel):

    class Meta:
        database = db