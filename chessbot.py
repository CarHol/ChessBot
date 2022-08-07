# chessbot.py
import os
import dbfactory
import discord
import chess
from settings import get_settings
from dotenv import load_dotenv
from dbfactory import get_db

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

    # Parse intent
    if message.content.startswith(f"!{callsign}"):
        # Parse the commands
        # Thoughs on commands:
        # Start new game, either open (first to join gets second role) or challenge (specify player)
        
        if commands["new_game_challenge"] in message.content:
            print(message.author.mention)
            print(message.content)
            print(message.id)

        if commands["new_game_open"] in message.content:
            #opponent = message.mentions[0]
        # As experiment, just add new game
        #board = chess.Board()
        #player

# Useful for later (detecting responses)
def check(m):
   if m.reference is not None:
        if m.reference.message_id = some_msg.id
            return True
   return False

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)