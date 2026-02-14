# Chess

A chess application using python and kivy. This was made as the first project in my university.

## Video Demonstration

[Gravação de tela de 16-09-2024 20:06:22.webm](https://github.com/user-attachments/assets/accbdf90-243f-4327-9a96-b09e2c0c8680)

## Project Structure

After refactoring, the project has been reorganized into a clean Model/Controller/View structure:

- **chess_core/** - Pure game logic (no Kivy dependencies)
  - `board.py` - Board class and piece movement logic
  - `pieces.py` - Chess piece classes (Pawn, Rook, Bishop, etc.)
  - `square.py` - Square and EmptySquare classes
  - `rules.py` - Game rules (check, checkmate, turn handling)
  
- **game/** - Game controller
  - `controller.py` - GameController manages state and coordinates UI/model

- **app/** - Kivy UI components
  - `app.py` - ChessApp main application
  - `widgets.py` - BoardGrid and Sidebar widgets

- **kv/** - Kivy language files
  - `chess.kv` - Minimal KV layout file

- **main.py** - Application entry point

## Installing

### Pre-requisites

* Kivy 2.3
* python 3.10 or higher

### Running

1. Download or clone this repository
2. Install Kivy: `pip install kivy`
3. Run the application: `python main.py`

## Features

- Full chess gameplay with all piece movements
- Check and checkmate detection
- Pawn promotion to Queen
- En passant and castling support
- View auto-flips after each move
- Restart button to reset the game
- Turn indicator showing whose turn it is

## Image Sources

images found at https://greenchess.net/info.php?item=downloads

images use protected under creative commons license https://creativecommons.org/licenses/by-sa/3.0/deed.en

