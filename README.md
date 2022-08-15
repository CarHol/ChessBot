# ChessBot
A simple chess bot for Discord in a messy early alpha state.

## Instructions
Start the bot by launching `chessbot.py` after defining the environment variable `DISCORD_TOKEN`, either directly in your environment or in a `.env` file.

Challenge another player to a game by sending the message `!chess challenge @user {mode}` in any channel where the bot is invited. `@user` should be a mention of another user in the server, and replace `{mode}` with one of the three available modes: `aswhite` to play as white, `asblack` to play as black and `asrandom` to flip a coin on which color to play. Respond `accept` to the resulting challenge message to start a game.

Play a move by responding to the resulting game board posted by the bot. Moves are written in UCI format, such as `a2a4` to move a piece from square A2 to square A4.

In place of a move you can also respond `resign` to resign the game, or `draw?` to offer a draw. Respond `accept` to the resulting draw offer to end the game in a draw. 

## Features still in progress
- Buttons for more intuitive interactions when accepting challenges, draws or resignations.
- Slash command in place of !chess token
- Stockfish integration
- Cleaner separation between Discord callbacks and game logic
- Multi-round matches

## Dependencies:
- `Python 3.7+` with `sqlite3`
- `cairosvg`
- Various Python dependencies specified in the file `dependencies`
