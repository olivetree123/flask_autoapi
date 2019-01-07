from flask import Flask
from flask_script import Manager
from peewee import MySQLDatabase
from playhouse.shortcuts import model_to_dict
from peewee import CharField, BooleanField, IntegerField, Model, ForeignKeyField



db = MySQLDatabase(
    "test", 
    host="localhost", 
    port=3306, 
    user="root", 
    password="gaojian"
)

class School(Model):
    name = CharField(null=False, verbose_name="名称")
    
    class Meta:
        database = db


class User(Model):
    name   = CharField(null=False, verbose_name="名称")
    school = ForeignKeyField(School, backref="users")

    class Meta:
        database = db


MODEL_LIST = [School, User]
db.create_tables(MODEL_LIST)

def create_data():
    school = School.create(name="gaojian xiaoxue")
    user = User.create(name="gaojian", school=school)
    
def get_data():
    user = User.get_or_none(User.id == 1)
    print(model_to_dict(user))

if __name__ == "__main__":
    # create_data()
    get_data()
    