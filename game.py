from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
pygame.init()


class game_info(): # main game class
    def __init__(self, win_w, win_h, chunks, start_chunk):

        self.win_w = win_w
        self.win_h = win_h

        self.win = pygame.display.set_mode((win_w, win_h))
        pygame.display.set_caption("Pangaea's wacky camera adventure") # epic

        self.chunks = chunks

        self.current_chunk = start_chunk

        self.run = True

    def update_keys(self):
        # self.keys is a list if current keys that are pressed
        self.keys = pygame.key.get_pressed()

    # Function called by player when current chunk needs to be changed
    def change_chunk(self, direction):

        # Changes the current_chunk variable based on the given border that the player is crossing
        if direction == "Left":
            self.current_chunk -= 1

        elif direction == "Right":
            self.current_chunk += 1

        elif direction == "Up": # 3 because 3x3 space
            self.current_chunk -= 3

        elif direction == "Down":
            self.current_chunk += 3


class map_chunk(): # "Room" or "Chunk" where each country will be in
    def __init__(self, index, name, countries, borders_dict, bg):

        # Where the chunk appears in the game.chunks list, might be used for validation
        self.index = index

        # The name of the chunk, used so we can distinguish lol
        self.name = name

        # List of countries that appear in the chunk
        self.countries = countries

        # Dictionary of chunks borders, where borders that can be crossed are True, and ones that cannot are False
        self.borders = borders_dict

        # Colour to display for background (WILL BE REPLACED WITH A SPRITE)
        self.bg = bg

    # Function for drawing the current chunk
    def update_draw(self, game):
        game.win.fill(self.bg)


# THE player (you)
class player():
    def __init__(self, start_x, start_y, speed, start_width, start_height, sprites_dict):

        # Starting position for player
        self.x = start_x
        self.y = start_y

        # Speed player moves at
        self.speed = speed

        # Dimensions of player, used for calculations and drawing (DRAWING WILL USE SPRITE)
        self.width = start_width
        self.height = start_height

        # Currently unused dictionary of sprites that the country can use
        self.sprites = sprites_dict
        self.sprite_status = "Default"

        # All sprites are initally facing right, must be flipped to turn left
        self.facing_right = True

    # Function for updating movement of player
    def update_move(self, game):
        # Get the position you are before you update
        self.old_x = self.x
        self.old_y = self.y

        # Move player based on what keys are down
        if game.keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.facing_right = False

        elif game.keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.facing_right = True

        if game.keys[pygame.K_UP]:
            self.y -= self.speed

        elif game.keys[pygame.K_DOWN]:
            self.y += self.speed

        on_border = self.border_check(game) # Is false if not on border

        # If the player is actually on a border
        if on_border:
            # Moves the player to the other side of the screen
            if on_border == "Left":
                self.x = game.win_w - (self.width // 2)

            elif on_border == "Right":
                self.x = self.width // 2

            elif on_border == "Up":
                self.y = game.win_h - (self.height // 2)

            elif on_border == "Down":
                self.y = self.height // 2

            # Calls the change_chunk() function with information about current border
            game.change_chunk(on_border)

    # Function for checking whether player is on a border
    def border_check(self, game): # checks which border you are on

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
            # If the given border is a wall (False), then the player cannot cross it
            if game.chunks[game.current_chunk].borders[border_pos]:
                return border_pos

            # Reverts them to their position for they moved
            else:
                self.x = self.old_x
                self.y = self.old_y
                return False

    # Function for drawing the player character (WILL BE UPDATED TO USE A SPRITE)
    def update_draw(self, game):
        pygame.draw.rect(game.win, (155, 40, 40), (self.x, self.y, self.width, self.height))

        if self.facing_right:
            blit_sprite = self.sprites[self.sprite_status]
        else:
            blit_sprite = pygame.transform.flip(self.sprites[self.sprite_status], True, False)

        game.win.blit(blit_sprite, (self.x, self.y))


pangaea_sprites = {"Default" : pygame.image.load('data/sprites/PanDefault.png')}

# List of chunks generated when they are instantiated
local_chunks = [
    map_chunk(index=0, name="Top-Left", countries=("Green"), borders_dict={"Left" : False, "Right" : True, "Up" : False, "Down" : True}, bg=(0, 155, 100)),
    map_chunk(index=1, name="Top-Middle", countries=("Red"), borders_dict={"Left": True, "Right": True, "Up": False, "Down": True}, bg=(183, 107, 103)),
    map_chunk(index=2, name="Top-Right", countries=("Purple"), borders_dict={"Left" : True, "Right" : False, "Up" : False, "Down" : True}, bg=(98, 62, 238)),
    map_chunk(index=3, name="Middle-Left", countries=("Yellow"), borders_dict={"Left" : False, "Right" : True, "Up" : True, "Down" : True}, bg=(255, 218, 110)),
    map_chunk(index=4, name="Middle-Middle", countries=("Dark Cyan"), borders_dict={"Left": True, "Right": True, "Up": True, "Down": True}, bg=(58, 135, 189)),
    map_chunk(index=5, name="Middle-Right", countries=("Grey"), borders_dict={"Left" : True, "Right" : False, "Up" : True, "Down" : True}, bg=(43, 59, 65)),
    map_chunk(index=6, name="Bottom-Left", countries=("North America"), borders_dict={"Left" : False, "Right" : True, "Up" : True, "Down" : False}, bg=(0, 155, 100)),
    map_chunk(index=7, name="Bottom-Middle", countries=("Brown"), borders_dict={"Left": True, "Right": True, "Up": True, "Down": False}, bg=(121, 83, 69)),
    map_chunk(index=8, name="Bottom-Right", countries=("North America"), borders_dict={"Left" : True, "Right" : False, "Up" : True, "Down" : False}, bg=(140, 0, 219))
]


game = game_info(win_w=1280, win_h=720, chunks=local_chunks, start_chunk=1)

pangea = player(start_x=600, start_y=400, speed=5, start_width=150, start_height=100, sprites_dict=pangaea_sprites)

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
