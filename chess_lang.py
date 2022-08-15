from settings import get_settings
from discord_utils import *

commands = get_settings()["commands"] 

def accept_challenge_prompt(challenger, challengee):
    return f"{id_to_mention(challenger)} challenges {id_to_mention(challengee)} to a game.\nAccept by responding '{commands['accept_challenge']}' to this message."

def game_created(white_player, black_player):
    return f"New game between {id_to_mention(white_player)} and {id_to_mention(black_player)}\n{id_to_mention(white_player)} to move as white.\nType your move as a reply to this message."

def checkmate_desc(player):
    return f"Checkmate! {id_to_mention(player)} wins."

def stalemate_desc(player):
    return f"Stalemate - draw."

def next_turn(player, opponent, opponent_color, move):
    return f"{id_to_mention(player)} played {move}. {id_to_mention(opponent)}'s move as {opponent_color}."

def offer_draw(player, opponent):
    return f"{id_to_mention(player)} offers draw to {id_to_mention(opponent)} - accept?" 

def offer_draw_technical_error():
    return "Technical error, could not offer draw"

def game_ends_in_draw():
    return f"Game ends in a draw."

def game_end_technical_failure():
    return "Technical error, could not end game"

def game_end_by_resignation(player, opponent):
    return f"{id_to_mention(player)} resigned - {id_to_mention(opponent)} won."