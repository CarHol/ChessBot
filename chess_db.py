from dbfactory import get_db
import uuid
import chess

class ChessDB:
    def __init__(self):
        self._db = get_db()

    def game_exists(message_id):
        # Todo: make sure the id has a valid format
        data = self._db.execute(f"""
            SELECT * FROM GAMES WHERE LastMessageId = '{message_id}'
        """)
        return len(data) > 0

    def new_game(message_id, white_player, black_player):
        new_game_id = str(uuid.uuid1())
        new_game_state = chess.Board().fen()
        self._db.execute("""
            INSERT INTO GAMES (Id, WhitePlayer, BlackPlayer, GameState, LastMessageId) 
            values({new_game_id}, {white_player}, {black_player}, {new_game_state}, {message_id})
        """)