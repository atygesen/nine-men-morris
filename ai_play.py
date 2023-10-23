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

player = game.board.players[0]
ai = MinimaxAI(game.board.players[0], game.board.players[1], game.rules, max_depth=4)
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
    my_p = len(board.pieces_by_player[player])
    other_p = len(board.pieces_by_player[other_player])

    s = abs(my_p - other_p)

    if result == "loss":
        s *= -1
    return s

def play():
    global running

    game.reset()
    ai.clear()

    print(eva.get_brain())

    t0 = time.perf_counter()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if game.is_game_over():
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

t0 = time.perf_counter()
idx = 0
pops = []
pop_scores = ga.scores
is_initial = True
best_brain = None
best_score = float("-inf")
while running:
    if idx == 0:
        with open(storage, "w") as fd:
            json.dump(brains, fd, indent=4)
        if best_score > 0:
            other_player.ai.evaluator.load_brain()
        if pops:
            # Get best pop
            print("pop won {:.2f}%".format(sum(1 for s in pop_scores if s > 0)/len(pop_scores)*100))
            best_i = np.argmax(pop_scores)
            if max(pop_scores) >= 0:
                best_score = max(pop_scores)
                best_brain = pops[best_i]
            eva.set_brain(best_brain)
            print("Scores:", pop_scores)
        b = eva.get_brain()
        pops = ga.generate_pops(b)
        pop_scores.clear()
        print(f"Generated new pop of length {len(pops)}")
    brain = pops[idx]
    eva.set_brain(brain)
    play()
    pop_scores.append(brains["score"][-1])
    idx = (idx + 1) % ga.n_pops

pygame.quit()