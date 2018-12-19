from flask import Flask
from flask_script import Manager

from models.init import MODEL_LIST
from flask_autoapi import AutoAPI
from flask_autoapi.command import GenerateDoc


app = Flask(__name__)
api = AutoAPI()
api.init_app(app, MODEL_LIST)
manager = Manager(app)
manager.add_command("doc", GenerateDoc(MODEL_LIST))

if __name__ == '__main__':
    manager.run()
    