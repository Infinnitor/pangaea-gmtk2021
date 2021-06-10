from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
pygame.init()


class game_info():
    def __init__(self, win_w, win_h, bg_colour):

        self.win_w = win_w
        self.win_h = win_h

        self.win = pygame.display.set_mode((win_w, win_h))
        pygame.display.set_caption("GMTK game jam")

        self.bg = bg_colour


game = game_info(win_w=1200, win_h=800, bg_colour=(0, 0, 0))

run = True
while run:
    pygame.time.delay(10)

    pygame.draw.rect(game.win, (155, 40, 40), (0, 0, game.win_w // 5, game.win_h // 5))
    pygame.display.update()
    game.win.fill(game.bg)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

pygame.quit()
