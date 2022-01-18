from flask import Flask
from flask_apidoc import ApiDoc

from models.init import MODEL_LIST
from flask_autoapi import AutoAPI
from flask_autoapi.command import GenerateApiDoc

app = Flask(__name__)
doc = ApiDoc(app=app)
api = AutoAPI()
doc.init_app(app)
api.init_app(app, MODEL_LIST)
app.cli.add_command(GenerateApiDoc(api), "apidoc")

if __name__ == "__main__":
    app.run(port=5111)
