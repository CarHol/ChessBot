import sqlite3 as sl
from os import path, remove
from settings import get_settings

def setup_tables(dbpath):
    if path.exists(dbpath):
        remove(dbpath)
    
    with sl.connect(dbpath) as con:
        # Create a users' table:
        con.execute("""
            CREATE TABLE USERS (
                Id TEXT NOT NULL PRIMARY KEY,
                DiscordId TEXT
            );
        """)

        # Create a games table
        con.execute("""
            CREATE TABLE GAMES (
                Id TEXT NOT NULL PRIMARY KEY,
                WhitePlayer TEXT,
                BlackPlayer TEXT,
                GameState TEXT NOT NULL,
                LastMove TEXT NOT NULL,
                FOREIGN KEY (WhitePlayer) references USERS(Id)
                FOREIGN KEY (BlackPlayer) references USERS(Id)
            );
        """)

def main():
    settings = get_settings()
    setup_tables(settings["dbfile"])

if __name__ == "__main__":
    main()