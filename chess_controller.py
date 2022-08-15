import os
import dbfactory
import discord
import chess
import chess.svg

import re
import chess_lang
import chess_db
import discord_utils

from dotenv import load_dotenv
from dbfactory import get_db
from cairosvg import svg2png

from settings import get_settings
commands = get_settings()["commands"]

# Patterns
mode_pattern = "|".join([key.lower() for key in chess_db.challenge_type.keys()])
challengee_pattern = r"<@\d+>"

# Endpoints
async def handle_challenge_reponse(message, client, verbose = 0):
    ref_id = message.reference.message_id
    try:
        challenge = chess_db.get_challenge(ref_id)
    except:
        verbose > 0 and print(f"Could not get challenge by ref id {ref_id}")
        raise Exception("Could not get challenge by ref id")
    if challenge is None:
        return
    
    # Message is a response to a challenge, make sure it's the right responder
    responder_id = discord_utils.mention_to_id(message.author.mention)
    challenge_id, challenger, challengee, challenge_type = challenge
    if responder_id != challengee:
        verbose > 0 and print(f"Invalid responder - challengee is {challengee} and responder is {responder_id}")
        return
    
    # Create a new game from the request
    channel = message.channel

    # Initial board layout is always the same, so use a pre-loaded one:
    file = discord.File("init_board.png", filename="board.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://board.png")

    new_message = await channel.send(file=file, embed=embed, content='Creating game...')
    new_message_id = new_message.id
    try:
        game = chess_db.new_game_from_challenge(challenge_id, new_message_id)
    except:
        verbose > 0 and print("Could not create new game from challenge")
        raise Exception("Could not create new game from challenge")
    if game is None:
        await new_message.edit(content='Failed to create game.')
        return
    board, white_player, black_player = game
    
    await new_message.edit(content=chess_lang.game_created(white_player, black_player))

def is_valid_game_response(message, client, verbose=0):
    ref_id = message.reference.message_id
    existing_game = chess_db.get_games(ref_id)
    
    if len(existing_game) == 0:
        return
    _, white_player, black_player, game_state, _, draw_offered = existing_game[0]
    board = chess.Board(game_state)
    is_white_turn = board.turn
    responder = discord_utils.mention_to_id(message.author.mention)
    is_player = responder == white_player or responder == black_player
    responders_turn = responder == white_player and is_white_turn or responder == black_player and not is_white_turn
    return is_player and (responders_turn or bool(draw_offered))

async def play_move(message, client, verbose=0):

    channel = message.channel
    player = discord_utils.mention_to_id(message.author.mention)
    message_id = message.id
    ref_id = message.reference.message_id
    game = chess_db.get_games(ref_id)[0]
    game_id, white_player, black_player, game_state, _, draw_offered = game
    board = chess.Board(game_state)
    is_white_turn = board.turn
    opponent, opponent_color = (black_player, "black") if is_white_turn else (white_player, "white")

    # Double check that it's actually the player's turn, or a draw has been offered
    is_player = player == white_player or player == black_player
    if not is_player:
        return

    # Is the move played a resignation (can be made at any time)?
    if commands["resign"] in message.content:
        await channel.send(chess_lang.game_end_by_resignation(player, opponent))
        # Delete the existing game
        delete_success = chess_db.end_game(ref_id)
        return

    
    players_turn = player == white_player and is_white_turn or player == black_player and not is_white_turn
    if not players_turn and not bool(draw_offered):
        verbose > 0 and print("No valid command")
        return # Ignore

    # Is the move an accepted draw?
    # A more convoluted truth statement, but makes it possible to play yourself and offer draw (useful for debugging)
    if commands["accept_draw"] in message.content and bool(draw_offered) and (player == black_player and is_white_turn \
            or player == white_player and not is_white_turn):
        draw_success = chess_db.end_game(ref_id)
        response_str = chess_lang.game_ends_in_draw() if draw_success else chess_lang.game_end_technical_failure()
        await channel.send(response_str)
        return

    # Is the move played an offered draw?
    if commands["offer_draw"] in message.content:
        new_message = await channel.send("Offering draw...")
        new_message_id = new_message.id
        offer_success = chess_db.set_offered_draw(ref_id, new_message_id)
        response_msg = chess_lang.offer_draw(player, opponent) if offer_success else chess_lang.offer_draw_technical_error()
        await new_message.edit(content=response_msg)
        return


    # Check that the move can be parsed
    try:
        move = chess.Move.from_uci(message.content)
    except:
        verbose > 0 and print(f"Move {message.content} could not be parsed")
        raise MalformedMoveException("Move cannot be parsed")

    # Check that the move is legal
    if move not in board.legal_moves:
        verbose > 0 and print(f"Illegal move {message.content}")
        raise IllegalMoveException("Illegal move")

    # Place the move
    board.push(move)

    # Check if game over:
    is_check = board.is_check()
    is_checkmate = board.is_checkmate()
    is_stalemate = board.is_stalemate()

    # Generate new image
    opponent_king = board.king(chess.WHITE if opponent_color == "white" else chess.BLACK)
    board_svg = chess.svg.board(board, lastmove=move, check=opponent_king if is_check or is_checkmate else None)
    filename = f"output_{message_id}.png"
    svg2png(bytestring=board_svg,write_to=filename, scale=2)
    if not os.path.exists(filename):
        verbose > 0 and print("Could not generate image for board state {board}")
        raise ImageExportException("Could not generate image")

    file = discord.File(filename, filename="board.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://board.png")

    # Display the new state
    new_message = await channel.send(file=file, embed=embed, content='Playing move...')
    new_message_id = new_message.id

    # Handle checkmates or stalemates
    if is_checkmate:
        end_success = chess_db.end_game(ref_id)
        checkmate_desc = chess_lang.checkmate_desc(player) if end_success else chess_lang.game_end_technical_failure()
        os.remove(filename)
        await new_message.edit(content=checkmate_desc)
        return
    
    if is_stalemate:
        end_success = chess_db.end_game(ref_id)
        stalemate_desc = chess_lang.stalemate_desc(player) if end_success else chess_lang.game_end_technical_failure()
        os.remove(filename)
        await new_message.edit(content=stalemate_desc)
        return

    # Save the move to the database and update the message
    db_success = chess_db.update_game(game_id, board.fen(), new_message_id)
    if not db_success:
        os.remove(filename)
        verbose > 0 and print("Could not update db")
        await new_message.edit(content="DB error, could not play move", file=None)
    
    played_move_desc = chess_lang.next_turn(player, opponent, "black" if is_white_turn else "white", message.content)
    await new_message.edit(content=played_move_desc)
    os.remove(filename)

async def new_game_challenge(message, client, verbose = 0):
    
    #challengee_matches = re.findall(challengee_pattern, message.content)
    challengee_matches = discord_utils.find_mention_id(message.content)
    if len(challengee_matches) == 0:
        verbose > 0 and print("No challengee")
        return # Todo: show error message
        
    # Todo: allow only one game mode
    mode_matches = re.findall(mode_pattern, message.content.lower())
    if not len(mode_matches):
        verbose > 0 and print("No valid mode")
        return
    mode = chess_db.challenge_type[mode_matches[0].upper()]

    challengee = challengee_matches[0]
    challenger = discord_utils.mention_to_id(message.author.mention)
    
    channel = message.channel
    new_message = await channel.send(f"Please wait...")
    success = chess_db.new_challenge(new_message.id, challenger, challengee, mode)
    response_str = chess_lang.accept_challenge_prompt(challenger, challengee) \
        if success \
        else "Could not create challenge"
    await new_message.edit(
        content=response_str
    )

# Exceptions
class IllegalMoveException(Exception):
    pass

class MalformedMoveException(Exception):
    pass

class WrongTurnException(Exception):
    pass

class ImageExportException(Exception):
    pass