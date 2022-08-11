import sqlite3 as sl
from os import path, remove
from settings import get_settings

def setup_tables(dbpath):
    if path.exists(dbpath):
        remove(dbpath)
    
    with sl.connect(dbpath) as con:

        # Create a games table
        con.execute("""
            CREATE TABLE GAMES (
                Id TEXT NOT NULL PRIMARY KEY,
                WhitePlayer TEXT NOT NULL,
                BlackPlayer TEXT NOT NULL,
                GameState TEXT NOT NULL,
                LastMessageId TEXT NOT NULL UNIQUE,
                OfferedDraw INTEGER NOT NULL
            );
        """)

        # Create a challenges table
        con.execute("""
            CREATE TABLE CHALLENGES (
                Id TEXT NOT NULL PRIMARY KEY,
                Challenger TEXT NOT NULL,
                Challengee TEXT,
                ChallengeType INTEGER NOT NULL
            );
        """)

def main():
    settings = get_settings()
    setup_tables(settings["dbfile"])

if __name__ == "__main__":
    main()