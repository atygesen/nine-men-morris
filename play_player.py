#!/usr/bin/env python3
import pygame
from nnm.main import NineMenMorris, Phase
from nnm.ai.minimax import MinimaxAI
from nnm.ai.ga import GA
import json
from pathlib import Path
import time
import numpy as np
from pprint import pprint
import math

pygame.init()
screen = pygame.display.set_mode((860, 860))

game = NineMenMorris(screen)

running = True

player = game.board.players[0]
stopped = False

def play():
    global running, stopped

    t0 = time.perf_counter()
    while running:
        if game.is_ai_turn() and not game.is_game_over():
            game.play_ai()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                game.event_handler(event)

        if not stopped and game.is_game_over():
            state = game.get_phase()
            if state is Phase.DRAW:
                result = "draw"
            else:
                winner = game.get_winner()
                if winner is player:
                    result = "win"
                else:
                    result = "loss"
            print(f"Result: {result}.")
            stopped = True

        game.draw()
        pygame.display.flip()
while running:
    play()
pygame.quit()