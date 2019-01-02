from flask import Flask
from flask_script import Manager
from peewee import MySQLDatabase
from peewee import CharField, BooleanField, IntegerField, Model, ManyToManyField



db = MySQLDatabase(
    "test", 
    host="localhost", 
    port=3306, 
    user="root", 
    password="gaojian"
)

class Tag(Model):
    name = CharField(null=False, unique=True, verbose_name="名称")
    
    class Meta:
        database = db


class App(Model):
    name = CharField(null=False, verbose_name="名称")
    tags = ManyToManyField(Tag, backref="apps")

    class Meta:
        database = db

AppTag = App.tags.get_through_model()

MODEL_LIST = [App, Tag, AppTag]
db.create_tables(MODEL_LIST)

def create_data():
    app = App.create(name="gaojian")
    tag = Tag.create(name="gaojian_tag")
    app.tags.add(tag.id)

def get_data():
    # app = App.get_or_none(App.id == 1)
    apps = App.select(App, AppTag, Tag).join(AppTag).join(Tag)
    for app in apps:
        for tag in app.tags:
            print(tag.id, tag.name)

if __name__ == "__main__":
    # app = Flask(__name__)
    # create_data()
    get_data()
    # app.run()