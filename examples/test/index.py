from flask import Flask

from models.init import MODEL_LIST
from flask_autoapi import AutoAPI
from flask_autoapi.command import GenerateApiDoc

app = Flask(__name__)
api = AutoAPI()
api.init_app(app, MODEL_LIST)
app.cli.add_command(GenerateApiDoc(MODEL_LIST), "doc")

if __name__ == "__main__":
    app.run()
