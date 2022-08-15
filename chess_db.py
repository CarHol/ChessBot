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


def get_games(message_id):
    # Todo: make sure the id has a valid format
    db = get_db()
    with db:
        cur = db.cursor()
        cur.execute(f"""
            SELECT * FROM GAMES WHERE LastMessageId = '{message_id}';
        """)
        data = cur.fetchall()
    db.close()
    return data

def set_offered_draw(old_message_id, new_message_id):
    db = get_db()
    with db:
        data = (new_message_id, old_message_id)
        cur = db.cursor()
        cur.execute(f"""
            UPDATE GAMES
            SET LastMessageId = ?,
                OfferedDraw = 1
            WHERE
                LastMessageId = ?
        """, data)
        rows_affected = cur.rowcount
    return rows_affected == 1

def game_exists(message_id):
    data = get_games(message_id)
    return data is not None and len(data) > 0

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

def update_game(game_id, game_state, new_message_id):
    db = get_db()
    with db:
        data = (game_state, new_message_id, game_id)
        cur = db.cursor()
        cur.execute(f"""
            UPDATE GAMES
            SET GameState = ?,
                LastMessageId = ?
            WHERE
                Id = ?
        """, data)
        rows_affected = cur.rowcount
    return rows_affected == 1

def new_game(message_id, white_player, black_player, verbose=0):
    new_game_id = str(uuid.uuid1())
    new_board = chess.Board()
    new_game_state = new_board.fen()

    if verbose > 1:
        print(f"New game ID: {new_game_id}")
        print(f"New game board:\n{new_board}")
        print(f"New game state:\n{new_game_state}")

    db = get_db()
    with db:
        data = (new_game_id, white_player, black_player, new_game_state, message_id, 0)
        cur = db.cursor()
        cur.execute(f"""
            INSERT INTO GAMES (Id, WhitePlayer, BlackPlayer, GameState, LastMessageId, OfferedDraw) 
            values(?, ?, ?, ?, ?, ?)
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
        success = cur.rowcount == 1
    db.close()
    return success

def delete_challenge(message_id):
    db = get_db()
    with db:
        cur = db.cursor()
        cur.execute(f"""
            DELETE FROM CHALLENGES WHERE Id='{message_id}'
        """)
        success = cur.rowcount == 1
    
    db.close()
    return success

def end_game(message_id):
    db = get_db()
    with db:
        cur = db.cursor()
        cur.execute(f"""
            DELETE FROM GAMES WHERE LastMessageId='{message_id}'
        """)
        success = cur.rowcount == 1
    db.close()
    return success

def new_game_from_challenge(old_message_id, new_message_id, verbose=0):
    db = get_db()
    with db:
        cur = db.cursor()
        try:
            cur.execute(f"""
                SELECT * FROM CHALLENGES WHERE Id='{old_message_id}'
            """)
            res =  cur.fetchone()
        except:
            print("Could not fetch from db")
        if not res:
            verbose > 0 and print("No challenge found")
            return res
        
        _, challenger, challengee, game_mode = res
        verbose > 1 and print(f"Extracted data from result {res}")


        if game_mode == challenge_type["ASWHITE"]:
            white_player = challenger
            black_player = challengee
        elif game_mode == challenge_type["ASBLACK"]:
            white_player = challengee
            black_player = challenger
        elif game_mode == challenge_type["ASRANDOM"]:
            challenger_white = bool(random.getrandbits(1))
            white_player, black_player = (challenger, challengee) if challenger_white else (challengee, challenger)

        verbose > 1 and print(f"Set color white for {white_player} and black for {black_player}")
        try:
            board = new_game(new_message_id, white_player, black_player, verbose)
        except:
            print("Could not create new game after selecting color")

    db.close()
    try:
        delete_challenge_success = delete_challenge(old_message_id)
        verbose > 1 and delete_challenge_success and print(f"Deleted challenge by message id {old_message_id}")
    except:
        verbose > 0 and print("Could not delete challenge")
    return (board, white_player, black_player)