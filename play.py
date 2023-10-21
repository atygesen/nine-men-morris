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

ga = GA(n_pops=4)

storage = Path("brain.json")

eva.randomize_brain()
if storage.is_file():
    with storage.open() as fd:
        brains = json.load(fd)
else:
    brains = {"brains": [], "result": [], "turns": []}

scores = {"draw": 0, "win": 0, "loss": 0}
# if score_f.is_file():
    # with score_f.open() as fd:
    #     scores = json.load(fd)
for r in brains["result"]:
    scores[r] += 1

running = True

def play():
    global running

    t0 = time.perf_counter()
    while running:
        if game.is_game_over():
            dt = time.perf_counter() - t0
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
            brains["brains"].append(eva.get_brain())
            brains["result"].append(result)
            brains["turns"].append(game.board.ply)
            print(f"Result: {result}. Current score: {scores}. Game over in {dt:.2f} s")
            with open(storage, "w") as fd:
                json.dump(brains, fd, indent=4)
            game.reset()
            ai.clear()
            return
        if game.is_ai_turn() and not game.is_game_over():
            game.play_ai()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                game.event_handler(event)
        game.draw()
        pygame.display.flip()

def get_score(i=-1):
    global brains
    result = brains["result"][i]
    if result == "draw":
        return 0
    turns = brains["turns"][i]
    s = math.exp(-(turns/100)**2)
    if result == "loss":
        s *= -1
    return s

best_score = float("-inf")
for i, brain in enumerate(brains["brains"]):
    score = get_score(i)
    if score > best_score:
        print("Setting brain with score", brains["result"][i], brains["turns"][i], score)
        best_score = score
        eva.set_brain(brain)

t0 = time.perf_counter()
idx = 0
pops = []
pop_scores = []
while running:
    if idx == 0:
        print("Generating new pop")
        if pops:
            # Get best pop
            print("pop won {:.2f}%".format(sum(1 for s in pop_scores if s > 0)/len(pop_scores)*100))
            best_i = np.argmax(pop_scores)
            eva.set_brain(pops[best_i])
        pops = ga.generate_pops(eva.get_brain())
        # print("New brains:")
        # pprint(pops)
        pop_scores.clear()
    brain = pops[idx]
    eva.set_brain(brain)
    play()
    score = get_score()
    pop_scores.append(score)
    idx = (idx + 1) % ga.n_pops

pygame.quit()