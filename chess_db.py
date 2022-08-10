from dbfactory import get_db
from enum import Enum
import uuid
import chess
import random

challenge_type = {
    "ASWHITE": 0,
    "ASBLACK": 1,
    "ASRANDOM": 2
}

def game_exists(message_id):
    # Todo: make sure the id has a valid format
    db = get_db()
    with db:
        cur = db.cursor()
        cur.execute(f"""
            SELECT * FROM GAMES WHERE LastMessageId = '{message_id}';
        """)
        data = cur.fetchall()
    db.close()
    return len(data) > 0

def get_challenge(message_id):
    db = get_db()
    with db:
        cur = db.cursor()
        cur.execute(f"""
            SELECT * FROM CHALLENGES WHERE Id='{message_id}'
        """)
        res = cur.fetchone()
    db.close()

    return res

def new_game(message_id, white_player, black_player):
    new_game_id = str(uuid.uuid1())
    new_board = chess.Board()
    new_game_state = new_board.fen()

    db = get_db()
    with db:
        data = (new_game_id, white_player, black_player, new_game_state, message_id)
        cur = db.cursor()
        cur.execute(f"""
            INSERT INTO GAMES (Id, WhitePlayer, BlackPlayer, GameState, LastMessageId) 
            values(?, ?, ?, ?, ?)
        """, data)
    db.close()
    return new_board

def new_challenge(message_id, challenger, challengee, challenge_type):
    db = get_db()
    data = (message_id,challenger,challengee, challenge_type)
    with db:
        cur = db.cursor()
        cur.execute(f"""
            INSERT INTO CHALLENGES (Id, Challenger, Challengee, ChallengeType) 
            values(?,?,?,?)
        """, data)
    db.close()

def new_game_from_challenge(old_message_id, new_message_id):
    db = get_db()
    print(old_message_id)
    with db:
        cur = db.cursor()
        cur.execute(f"""
            SELECT * FROM CHALLENGES WHERE Id='{old_message_id}'
        """)
        res =  cur.fetchone()

        if not res:
            print("No challenge found")
            return res
        
        _, challenger, challengee, game_mode = res

        if game_mode == challenge_type["ASWHITE"]:
            white_player = challenger
            black_player = challengee
        elif game_mode == challenge_type["ASBLACK"]:
            white_player = challengee
            black_player = challenger
        elif game_mode == challenge_type["ASRANDOM"]:
            challenger_white = bool(random.getrandbits(1))
            white_player, black_player = (challenger, challengee) if challenger_white else (challenge, challenger)

        board = new_game(new_message_id, white_player, black_player)

    db.close()
    return (board, white_player, black_player)