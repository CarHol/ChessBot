import os
import dbfactory
import discord
import chess
import chess.svg

import re
import chess_lang

from dotenv import load_dotenv
from dbfactory import get_db
from cairosvg import svg2png

from settings import get_settings
commands = get_settings()["commands"]
import chess_db

async def handle_challenge_reponse(message, client):
    ref_id = message.reference.message_id
    challenge = chess_db.get_challenge(ref_id)
    if challenge is None:
        return
    
    # Message is a response to a challenge, make sure it's the right responder
    challenge_id, challenger, challengee, challenge_type = challenge
    if message.author.mention != challengee:
        print("Invalid responder")
        return
    
    # Create a new game from the request
    channel = message.channel

    # Initial board layout is always the same, so use a pre-loaded one:
    file = discord.File("init_board.png", filename="board.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://board.png")

    new_message = await channel.send(file=file, embed=embed, content='Creating game...')
    new_message_id = new_message.id
    game = chess_db.new_game_from_challenge(challenge_id, new_message_id)
    if game is None:
        await new_message.edit(content='Failed to create game.')
        return
    board, white_player, black_player = game
    
    await new_message.edit(content=chess_lang.game_created(white_player, black_player))

def is_valid_game_response(message, client):
    ref_id = message.reference.message_id
    existing_game = chess_db.get_games(ref_id)
    
    if len(existing_game) == 0:
        return
    _, white_player, black_player, game_state, _, draw_offered = existing_game[0]
    board = chess.Board(game_state)
    is_white_turn = board.turn
    responder = message.author.mention
    is_player = responder == white_player or responder == black_player
    responders_turn = responder == white_player and is_white_turn or responder == black_player and not is_white_turn
    return is_player and (responders_turn or bool(draw_offered))

async def play_move(message, client):

    channel = message.channel
    player = message.author.mention
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
        await channel.send(f"{player} resigned - {opponent} won.")
        # Delete the existing game
        delete_success = chess_db.end_game(ref_id)
        return

    
    players_turn = player == white_player and is_white_turn or player == black_player and not is_white_turn
    if not players_turn and not bool(draw_offered):
        print("No valid command")
        return # Ignore


    # Is the move an accepted draw?
    # A more convoluted truth statement, but makes it possible to play yourself and offer draw (useful for debugging)
    if commands["accept_draw"] in message.content and bool(draw_offered) and (player == black_player and is_white_turn \
            or player == white_player and not is_white_turn):
        draw_success = chess_db.end_game(ref_id)
        response_str = chess_lang.game_ends_in_draw() if draw_success else game_end_technical_failure()
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
        raise MalformedMoveException("Move cannot be parsed")

    # Check that the move is legal
    if move not in board.legal_moves:
        raise IllegalMoveException("Illegal move")

    # Place the move and generate a new image
    board.push(move)
    filename = f"output_{message_id}.png"
    svg2png(bytestring=chess.svg.board(board),write_to=filename, scale=2)
    if not os.path.exists(filename):
        raise ImageExportException("Could not generate image")

    file = discord.File(filename, filename="board.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://board.png")

    # Check if game over:
    is_checkmate = board.is_checkmate()
    is_stalemate = board.is_stalemate()

    # Display the new state
    new_message = await channel.send(file=file, embed=embed, content='Playing move...')
    new_message_id = new_message.id

    # Handle checkmates or stalemates
    if is_checkmate:
        print("Stalemate")
        end_success = chess_db.end_game(ref_id)
        checkmate_desc = chess_lang.checkmate_desc(player) if end_success else chess_lang.game_end_technical_failure()
        os.remove(filename)
        await new_message.edit(content=checkmate_desc)
        return 
    
    if is_stalemate:
        print("Checkmate")
        end_success = chess_db.end_game(ref_id)
        stalemate_desc = chess_lang.stalemate_desc(player) if end_success else chess_lang.game_end_technical_failure()
        os.remove(filename)
        await new_message.edit(content=stalemate_desc)
        return

    # Save the move to the database and update the message
    db_success = chess_db.update_game(game_id, board.fen(), new_message_id)
    if not db_success:
        os.remove(filename)
        print("Could not update db")
        await new_message.edit(content="DB error, could not play move", file=None)
    
    played_move_desc = chess_lang.next_turn(player, opponent, "black" if is_white_turn else "white", message.content)
    await new_message.edit(content=played_move_desc)
    os.remove(filename)


# Exceptions
class IllegalMoveException(Exception):
    pass

class MalformedMoveException(Exception):
    pass

class WrongTurnException(Exception):
    pass

class ImageExportException(Exception):
    pass