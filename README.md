Klondike Solitaire (Python)
----------
A lightweight, offline implementation of Klondike Solitaire, written in Python using Pygame for the graphical interface and SQLite3 for persistent storage.
The project aims to provide a fast, accessible, and fully self‑contained solitaire experience without requiring internet access or large installation sizes.


Overview
---------
Klondike Solitaire is a single‑player card game where the objective is to arrange all 52 cards into four suit piles from Ace to King.
This project addresses several limitations of traditional and digital solitaire:
1)Physical solitaire requires space, setup time, and cannot be saved.
2)Many digital versions require internet access or large downloads.
3)Saving and resuming games is often limited.
This implementation runs entirely offline, stores data efficiently, and provides a familiar layout inspired by classic Microsoft Solitaire.

Features
--------
Gameplay
-Classic Klondike rules
-Two difficulty modes:
  -Easy: 1‑card draw
  -Hard: 3‑card draw
-Custom 8‑bit‑style card designs
-Click‑to‑move and drag‑and‑drop support
-Optional minimal sound effects (shuffle, deal)

Interface
-Menu page with Start, Difficulty, and Stats
-Stats page with a graph of wins and losses by date
-Game page with timer, save button, theme switcher, and back button
-Two selectable card‑back themes
-Clean, simple layout designed for clarity and usability

Saving and Loading
All game data is stored using SQLite tables:
-Playable piles
-Draw pile
-Solved piles
-Score and timer
-Save files named using date and time
-Load previous games from the game menu

Statistics
A dedicated stats table tracks:
-Wins
-Losses
-Date of play
Values increment automatically based on game results.

Installation
------------
Requirements
-Python 3.x
-Pygame
-SQLite3 (included with Python)
