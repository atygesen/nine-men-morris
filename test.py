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
    choice = ai.get_best_move()
    pr.dump_stats("test.prof")

pygame.quit()
