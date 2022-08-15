# chessbot.py
import os
import argparse
import re

import dbfactory
import discord
import chess
import chess.svg

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

parser = argparse.ArgumentParser(description='A simple Discord bot for playing Chess.')
parser.add_argument('--verbose',  '--v', type=int)
args = parser.parse_args()
verbose = args.verbose if args.verbose is not None else 0

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
        print(f"Received message response: {message.content}")
        # Check if the message responded to is connected to an ongoing game
        if chess_controller.is_valid_game_response(message, client, verbose):
            # Is it a move?
            try:
                await chess_controller.play_move(message, client, verbose)
            except:
                print(f"Could not play move {message.content}")
                # Todo: handle gracefully
                return
            return
        print("Not a valid game response")
        # Is it a response to a challenge?
        print(f"Message '{message.content.lower()}' matches command: {commands['accept_challenge'] in message.content }")
        if commands["accept_challenge"] in message.content:
            try:
                await chess_controller.handle_challenge_reponse(message, client, verbose)
            except:
                print("Could not handle challenge acceptance")
                return


    # Parse intent
    if message.content.startswith(f"!{callsign}"):
        
        if commands["new_game_challenge"] in message.content:
            await chess_controller.new_game_challenge(message, client, verbose)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)