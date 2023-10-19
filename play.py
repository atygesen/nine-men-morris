#!/usr/bin/env python3
import pygame
from nnm.main import NineMenMorris

pygame.init()
screen = pygame.display.set_mode((860, 860))

game = NineMenMorris(screen)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.event_handler(event)
    game.draw()
    pygame.display.flip()

pygame.quit()