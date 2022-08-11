# chessbot.py
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
import chess_db
import chess_controller

# Environment and client
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

# Settings
settings = get_settings()
commands = settings["commands"]
callsign = settings["callsign"]

# Storage
db = get_db()

# Event handlers
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Todo: add challenges to db to avoid re-using existing challenges

    # When listening for moves:
    # The white player replies to the message with a move
    # Detect that the message is a reply to a previous message
    # Check that that previous message is associated with a game state. If so, return the game state and players.
    # If the user replying the message is not any of the two players, ignore and return
    # If it's not the responder's turn, reply with a warning
    # If it is the correct player's turn, parse the content of the message and verify that the move is legal
    # If the move is legal, send a temporary message ("Playing move...") and note the id
    # Play the move on the parsed game state and save the new game state and message id to the db.
    # Update the message with a render of the new board state and tag the next player

    # Check if message is a response to an earlier message
    if message.reference is not None and message.reference.resolved:
        
        # ====================================================
        # Handle challenge response
        # ====================================================

        # Check if the message responded to is connected to an ongoing game
        if chess_controller.is_valid_game_response(message, client):
            # Is it a move?
            try:
                await chess_controller.play_move(message, client)
            except:
                # Todo: handle gracefully
                return
            return

        # Is it a response to a challenge?
        if commands["accept_challenge"] in message.content:
            try:
                await chess_controller.handle_challenge_reponse(message, client)
            except:
                return


    # Parse intent
    if message.content.startswith(f"!{callsign}"):
        # Parse the commands
        # Thoughs on commands:
        # Start new game, either open (first to join gets second role) or challenge (specify player)
        
        if commands["new_game_challenge"] in message.content:
            await chess_controller.new_game_challenge(message,client)

        #if commands["new_game_open"] in message.content:
            #opponent = message.mentions[0]
        # As experiment, just add new game
        #board = chess.Board()
        #player

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)