from server.database.connect import Database
from server.database.models import Chunk, Collection, Document
from server.utils.logger import log


def setup():
    """Create tables and initial data"""
    db = Database()
    db.connect(True)

    models = [Collection, Document, Chunk]
    db.create_tables(models)
    log("database").info("Database tables created.")
