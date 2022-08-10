from settings import get_settings

commands = get_settings()["commands"] 

def accept_challenge_prompt(challenger, challengee):
    return f"{challenger} challenges {challengee} to a game.\nAccept by responding '{commands['accept_challenge']}' to this message."

def game_created(white_player, black_player, board_layout):
    return f"New game between {white_player} and {black_player}:\n{board_layout}\n{white_player} to move as white.\nType your move as a reply to this message."