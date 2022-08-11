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

    # Check if message is a response to an earlier message
    if message.reference is not None and message.reference.resolved:

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
        
        if commands["new_game_challenge"] in message.content:
            await chess_controller.new_game_challenge(message,client)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)