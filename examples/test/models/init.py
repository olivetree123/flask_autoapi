from models import db
from models.album import Album
from models.audio import Audio

MODEL_LIST = [Album, Audio]

db.create_tables(MODEL_LIST)
