from settings import get_settings
from setup import setup_tables
import sqlite3 as sl
from os import path

def get_db():
    settings = get_settings()
    dbfile = settings["dbfile"]
    if not path.exists(dbfile):
        setup_tables(dbfile)
    
    return sl.connect(dbfile)