# chessbot.py
import os
import dbfactory
import discord
import chess
import re
from settings import get_settings
from dotenv import load_dotenv
from dbfactory import get_db
import chess_db

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
        ref_id = message.reference.message_id
        challenge = chess_db.get_challenge(ref_id)
        if challenge is None:
            return
        
        # Message is a response to a challenge, make sure it's the right responder
        challenge_id, challenger, challengee, challenge_type = challenge
        if message.author.mention != challengee:
            print("Invalid responder")
            return
        
        # Check for the right keyword
        if commands["accept_challenge"] not in message.content:
            print("Invalid command")
            return
        
        # Create a new game from the request
        new_message = await message.channel.send(f"Creating game...")
        new_message_id = new_message.id
        game = chess_db.new_game_from_challenge(challenge_id, new_message_id)
        if game is None:
            await new_message.edit(content='Failed to create game.')
            return

        board, white_player, black_player = game
        await new_message.edit(content=f"{board}\n\n{white_player} to move.")


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
            new_message = await channel.send(f"{challenger} challenges {challengee} to a game. Accept?")
            chess_db.new_challenge(new_message.id, challenger, challengee, mode)
            print(new_message.id)
            print()

        #if commands["new_game_open"] in message.content:
            #opponent = message.mentions[0]
        # As experiment, just add new game
        #board = chess.Board()
        #player

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)