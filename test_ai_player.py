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
import cProfile

pygame.init()
screen = pygame.display.set_mode((860, 860))

game = NineMenMorris(screen)

player = game.board.players[0]
ai = MinimaxAI(game.board.players[0], game.rules, max_depth=4)
player.ai = ai
eva = ai.evaluator

ga = GA(n_pops=6)

storage = Path("brain.json")

eva.randomize_brain()
if storage.is_file():
    with storage.open() as fd:
        brains = json.load(fd)
else:
    brains = {"brains": [], "result": [], "turns": [], "generation": [], "score": []}

scores = {"draw": 0, "win": 0, "loss": 0}
for r in brains["result"]:
    scores[r] += 1

running = True
other_player = game.board.players[1]


def get_score(result, turns):
    global brains
    if result == "draw":
        return 0
    # s = math.exp(-(turns/100)**2)
    # if result == "loss":
    #     s *= -1

    board = game.board
    my_p = board.get_player_pieces_on_board(player)
    other_p = board.get_player_pieces_on_board(other_player)

    s = abs(my_p - other_p)

    if result == "loss":
        s *= -1
    return s

def play():
    global running

    game.reset()
    ai.reset()

    # print(eva.get_brain())

    t0 = time.perf_counter()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if game.is_game_over():
            running = False
            dt = time.perf_counter() - t0
            t0 = time.perf_counter()
            state = game.get_phase()
            if state is Phase.DRAW:
                result = "draw"
            else:
                winner = game.get_winner()
                if winner is player:
                    result = "win"
                else:
                    result = "loss"
            scores[result] += 1
            score = get_score(result, game.board.ply)
            brains["brains"].append(eva.get_brain())
            brains["result"].append(result)
            brains["turns"].append(game.board.ply)
            brains["score"].append(score)
            brains["generation"].append(ga.generation)
            print(f"Result: {result}. Current score: {scores}. Game over in {dt:.2f} s")
            return
    
        game.play_ai()
        game.draw()
        pygame.display.flip()

best_score = float("-inf")
for i, brain in enumerate(brains["brains"]):
    score = brains["score"][i]
    if score > best_score:
        # print("Setting brain with score", brains["result"][i], brains["turns"][i], score)
        best_score = score
        eva.set_brain(brain)

with cProfile.Profile() as pr:
    play()
    pr.dump_stats("ai_profile.prof")


pygame.quit()