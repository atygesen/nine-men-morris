#!/usr/bin/env python3
import pygame
from nnm.main import NineMenMorris
import cProfile

pygame.init()
screen = pygame.display.set_mode((860, 860))

game = NineMenMorris(screen)

game.board.toggle_player()

with cProfile.Profile() as pr:
    ai = game.current_player.ai
    moves = list(game.rules.iter_current_moves())
    choice = ai.select_move(moves)
    pr.dump_stats("test.prof")

pygame.quit()