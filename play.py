#!/usr/bin/env python3
import pygame
from nnm.main import NineMenMorris

pygame.init()
screen = pygame.display.set_mode((860, 860))

game = NineMenMorris(screen)

running = True
while running:
    if game.is_ai_turn() and not game.is_game_over():
        game.play_ai()
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.event_handler(event)
    game.draw()
    pygame.display.flip()

pygame.quit()