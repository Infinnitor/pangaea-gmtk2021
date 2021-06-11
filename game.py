from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
pygame.init()


class game_info():
    def __init__(self, win_w, win_h, chunks, start_chunk):

        self.win_w = win_w
        self.win_h = win_h

        self.win = pygame.display.set_mode((win_w, win_h))
        pygame.display.set_caption("Pangaea's wacky camera adventure")

        self.chunks = chunks

        self.current_chunk = start_chunk

        self.run = True

    def update_keys(self):

        self.keys = pygame.key.get_pressed()

    def change_chunk(direction):
        if direction == "Left":
            self.current_chunk - 1



class map_chunk():
    def __init__(self, index, name, countries, borders_dict, bg):

        self.index = index
        self.name = name

        self.countries = countries
        self.borders = borders_dict

        self.bg = bg

    def update_draw(self, game):
        game.win.fill(self.bg)


class player():
    def __init__(self, start_x, start_y, speed, start_width, start_height, sprites_dict):

        self.x = start_x
        self.y = start_y
        self.speed = speed

        self.width = start_width
        self.height = start_height

        self.sprites = sprites_dict

    def update_move(self, game):

        self.old_x = self.x
        self.old_y = self.y

        if game.keys[pygame.K_LEFT]:
            self.x -= self.speed

        if game.keys[pygame.K_RIGHT]:
            self.x += self.speed

        if game.keys[pygame.K_UP]:
            self.y -= self.speed

        if game.keys[pygame.K_DOWN]:
            self.y += self.speed

        on_border = self.border_check(game)

        if on_border:
            game.change_chunk(on_border)

    def border_check(self, game):

        border_pos = False

        if self.x + (self.width // 2) < 0:
            border_pos = "Left"

        elif self.x + (self.width // 2) > game.win_w:
            border_pos = "Right"

        elif self.y + (self.height // 2) < 0:
            border_pos = "Up"

        elif self.y + (self.height // 2) > game.win_h:
            border_pos = "Down"

        if border_pos:
            if game.chunks[game.current_chunk].borders[border_pos]:
                pass
            else:
                self.x = self.old_x
                self.y = self.old_y

    def update_draw(self, game):
        pygame.draw.rect(game.win, (155, 40, 40), (self.x, self.y, self.width, self.height))


local_chunks = [
    map_chunk(index=0, name="Top-Left", countries=("North America"), borders_dict={"Left" : False, "Right" : True, "Up" : False, "Down" : False}, bg=(0, 155, 100)),
    map_chunk(index=1, name="Top-Middle", countries=("Eurasia"), borders_dict={"Left": False, "Right": False, "Up": False, "Down": False}, bg=(183, 107, 103)),
    map_chunk(index=2, name="Top-Right", countries=("North America"), borders_dict={"Left" : True, "Right" : False, "Up" : False, "Down" : False}, bg=(140, 0, 219))
]


game = game_info(win_w=1200, win_h=720, chunks=local_chunks, start_chunk=1)

pangea = player(start_x=600, start_y=400, speed=5, start_width=100, start_height=100, sprites_dict=None)

clock = pygame.time.Clock()

while game.run:

    clock.tick(60)

    pygame.display.update()
    game.win.fill((0, 0, 0))
    game.update_keys()

    game.chunks[game.current_chunk].update_draw(game)
    pangea.update_move(game)
    pangea.update_draw(game)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.run = False

pygame.quit()
