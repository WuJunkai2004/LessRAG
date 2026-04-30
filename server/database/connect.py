from pathlib import Path
from typing import Optional

from peewee import SqliteDatabase

from server.utils.logger import log


class _Database:
    _instance: Optional[SqliteDatabase] = None
    _db_path: Path = Path("datas/app.db")

    @classmethod
    def get_db(cls) -> SqliteDatabase:
        if cls._instance is None:
            cls._db_path.parent.mkdir(parents=True, exist_ok=True)
            cls._instance = SqliteDatabase(str(cls._db_path))
            log("database").info(f"Initialized database at {cls._db_path}")
        return cls._instance


def Database() -> SqliteDatabase:
    return _Database.get_db()
