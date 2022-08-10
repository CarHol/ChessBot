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

# Patterns
mode_pattern = "|".join([key.lower() for key in chess_db.challenge_type.keys()])

# Storage
db = get_db()

# Event handlers
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Todo: add challenges to db to avoid re-using existing challenges

    # When requesting a challenge:
    # Parse the message for challenge keyword, challenge mode and opponent tag
    # Compose a new message:
    #   "@challenger challenges @opponent, both colors"
    #   "@challenger challenges @opponent, as white"
    #   "@challenger challenges @opponent, as black"
    # Leave the loop and wait for a response

    # When accepting (should ideally be a button)
    # Check the challenge mode (default is asboth)
    # If fixed challenge mode, create a new game 

    # When creating a new game:
    # Send a placeholder message with content like "Creating game..."
    # Use the message id from that message and create a new row in the db with a fresh game
    # When the entry in the db is created, update the message, stating that it is white's turn (tag players)
    #   and draw the board.

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
    if message.reference is not None and message.reference.resolved:
        # Is it a response to a challenge?
        if commands["accept_challenge"] in message.content:
            try:
                await chess_controller.handle_challenge_reponse(message, client)
            except:
                return

        # Check if the message responded to is connected to an ongoing game
        if not chess_controller.is_valid_game_response(message, client):
            print("Received false")
            return

        print("Received true")
        # If it is, attempt to register the response
        try:
            print("Entering controller")
            await chess_controller.play_move(message, client)
        except:
            # Todo: handle gracefully
            return


    # Parse intent
    if message.content.startswith(f"!{callsign}"):
        # Parse the commands
        # Thoughs on commands:
        # Start new game, either open (first to join gets second role) or challenge (specify player)
        
        if commands["new_game_challenge"] in message.content:
            challengee_pattern = r"<@\d+>"
            challengee_matches = re.findall(challengee_pattern, message.content)
            if len(challengee_matches) == 0:
                print("No challengee")
                return # Todo: show error message
            
            # Todo: allow only one game mode
            mode_matches = re.findall(mode_pattern, message.content.lower())
            if not len(mode_matches):
                print("No valid mode")
                return
            mode = chess_db.challenge_type[mode_matches[0].upper()]

            challengee = challengee_matches[0]
            challenger = message.author.mention
            
            channel = message.channel
            new_message = await channel.send(f"Please wait...")
            success = chess_db.new_challenge(new_message.id, challenger, challengee, mode)
            response_str = chess_lang.accept_challenge_prompt(challenger, challengee) \
                if success \
                else "Could not create challenge"
            await new_message.edit(
                content=response_str
            )

        #if commands["new_game_open"] in message.content:
            #opponent = message.mentions[0]
        # As experiment, just add new game
        #board = chess.Board()
        #player

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)