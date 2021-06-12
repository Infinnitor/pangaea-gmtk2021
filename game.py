from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import math
import random

import pygame
pygame.init()


# Class for containing all relevant info about game's state
class game_info():
    def __init__(self, win_w, win_h, chunks, start_chunk, waves_dict, vn_sprites, xo_sprites):

        # Screen size info
        self.win_w = win_w
        self.win_h = win_h

        # Instantiating window
        self.win = pygame.display.set_mode((win_w, win_h))
        pygame.display.set_caption("Pangaea's wacky camera adventure") # epic

        # List of all chunk objects
        self.chunks = chunks

        # Chunk that player is currently on
        self.current_chunk = start_chunk

        # Bool to run mainloop
        self.run = True

        # Sprites to use for waves
        self.waves_sprites = waves_dict

        # Game state, 0 - exploration, 1 - VN, 2 - minigame
        self.game_state = 0

        self.vn_sprites = vn_sprites
        self.char_pos = (self.win_w - 500, 100)

        self.xo_sprites = xo_sprites

    def update_keys(self):
        # self.keys is a list if current keys that are pressed
        self.keys = pygame.key.get_pressed()
        self.mouse = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()

        if not any([self.keys[pygame.K_SPACE], self.keys[pygame.K_UP], self.keys[pygame.K_DOWN], self.keys[pygame.K_LEFT], self.keys[pygame.K_RIGHT]]):
            self.nonepressed = True
        else:
            self.nonepressed = False

        self.update_info()

    def update_info(self):
        if self.game_state == 2:
            self.char_pos = (self.win_w - 250, 350)

        else:
            self.char_pos = (self.win_w - 500, 100)

    # Function for updating various aspects of the UI
    def update_VNUI(self):

        # Smooth movment of overlay
        if self.overlay_x[0] < -500:
            self.overlay_x[0] += self.overlay_x[1]
            self.overlay_x[1] += 1
        else:
            self.overlay_x[0] = 0

        # If the textbox has not reached its destination
        if not self.textbox_still:
            # Smooth movment of textbox
            if self.textbox_y[0] > self.win_h - 310:
                self.textbox_y[0] -= self.textbox_y[1]
                self.textbox_y[1] += 0.5
            else:
                self.textbox_y[0] = self.win_h - 310
                self.textbox_still = True

        # Display UI elements
        self.win.blit(self.vn_sprites["Overlay"], (self.overlay_x[0], 0))

        self.chunks[self.current_chunk].country.update_character(self)

        self.win.blit(self.vn_sprites["Textbox"], (30, self.textbox_y[0]))

        if self.textbox_still:
            self.chunks[self.current_chunk].country.update_talk(self)

    # Function for initialising overlay and changing game state
    def VN_init(self):
        self.overlay_x = [0 - self.vn_sprites["Overlay"].get_size()[0], 15]

        self.textbox_y = [self.win_h, 5]
        self.textbox_still = False

        self.game_state = 1

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

    def minigame_init(self): # gamestate 2
        self.game_state = 2
        self.xo_board = ["None" for empty in range(9)]
        self.xo_turn = "X"

        sq_side = 150
        offset_x = 350
        offset_y = 100

        self.xo_square_side = sq_side
        self.xo_positions = []

        for y in range(3):
            for x in range(3):
                self.xo_positions.append((x * (sq_side + sq_side // 4) + offset_x, y * (sq_side + sq_side // 4) + offset_y))

    def minigame_update(self):

        self.win.blit(self.vn_sprites["Overlay"], (self.overlay_x[0], 0))
        self.chunks[self.current_chunk].country.update_character(game)

        positions = self.xo_positions

        def mouse_check(pos1, pos2, mouse_pos):

            if mouse_pos[0] > pos1[0] and mouse_pos[0] < pos2[0]:
                if mouse_pos[1] > pos1[1] and mouse_pos[1] < pos2[1]:
                    return True

            return False

        for i, square in enumerate(self.xo_board):

            self.win.blit(self.xo_sprites[square], (positions[i][0], positions[i][1]))

        if self.mouse[0]:
            for i, square in enumerate(self.xo_board):
                if mouse_check((positions[i][0], positions[i][1]), (positions[i][0] + self.xo_square_side, positions[i][1] + self.xo_square_side), self.mouse_pos):

                    if self.xo_board[i] == "None":
                        self.xo_board[i] = self.xo_turn
                        if self.xo_turn == "X":
                            self.xo_turn = "O"
                        else:
                            self.xo_turn = "X"


# Class for islands that appear in chunks
class island():
    def __init__(self, x, y, name, sprites_dict, dialogue, pangaea_sprites):

        # Position of island on chunk
        self.x = x
        self.y = y

        # Variables for adding bobbing
        self.wave_x = 0
        self.y_mod = 0

        # Variables for disambiguation and stuff
        self.name = name
        self.status = "Head"

        # Dictionary of all sprites for a given country
        self.sprites = sprites_dict
        self.pangaea_sprites = pangaea_sprites

        # Variables for tracking dialogue info across multiple frames
        self.dialogue_index = 0

        # THE font
        dialogue_font = pygame.font.SysFont(None, 50)

        # Create two lists for the speaker and text
        self.dialogue_obj = []
        self.dialogue_speaker = []
        self.dialogue_speaker_text = []
        self.dialogue_emotion = []
        for text in dialogue:

            # Split dialogue on a colon to get both the speaker and their dialogue
            t = text.split(":")

            # # Appending all the information about the speaker and emotion to some lists
            self.dialogue_emotion.append(t[2].replace(" ", ""))
            self.dialogue_speaker_text.append(t[0])
            self.dialogue_speaker.append(dialogue_font.render(t[0], True, (40, 40, 155)))

            # Splitting dialogue on | to form newlines
            dialogue_text = t[1].split("|")
            label = []
            for line in dialogue_text:
                label.append(dialogue_font.render(line, True, (0, 0, 0)))
            self.dialogue_obj.append(label) # List of lines in that dialogue

        # If space key was pressed last frame
        self.space_key_buffer = False

    # Function for updating dialogue on VNUI
    def update_talk(self, game):

        # Display dialogue
        try:
            game.win.blit(self.dialogue_speaker[self.dialogue_index], (80, game.textbox_y[0] + 15))

            for i, line in enumerate(self.dialogue_obj[self.dialogue_index]):
                game.win.blit(line, (50, game.textbox_y[0] + 70 + (50*i)))

        except IndexError:
            game.minigame_init() # Finishing dialogue, probs a better way of doing this lol

        # Check if space key is being pressed for the first time
        if game.keys[pygame.K_SPACE]:
            if not self.space_key_buffer:
                self.space_key_buffer = True

                self.dialogue_index += 1

        else:
            self.space_key_buffer = False

    # Function that just bobs the wee island and checks for space key press
    def update_move(self, game):
        self.bob()

        if game.keys[pygame.K_SPACE] and game.game_state == 0:
            game.VN_init()

    # Update
    def update_character(self, game):
        if game.game_state == 1:
            try:
                if self.dialogue_speaker_text[self.dialogue_index] == "PANGAEA":
                    game.win.blit(self.pangaea_sprites[self.dialogue_emotion[self.dialogue_index]], game.char_pos)
                else:
                    game.win.blit(self.sprites[self.dialogue_emotion[self.dialogue_index]], game.char_pos)
            except IndexError:
                pass

        elif game.game_state == 2:
            game.win.blit(self.sprites["angry"], game.char_pos)
        else:
            return

    # Function for drawing the island in the ocean
    def update_draw(self, game):
        game.win.blit(self.sprites[self.status], (self.x, self.y + self.y_mod))

        image_width = self.sprites[self.status].get_size()[0]
        game.win.blit(self.sprites["SpeechBubble"], (self.x + image_width, self.y - (self.y // 3) + self.y_mod))

    # Function for adding a small bob to the island
    def bob(self):

        # Creates a value for y_mod using a cosine wave given an x position and wavelenth + period
        self.wave_x += 1
        self.y_mod = 10 * math.cos(self.wave_x * 0.08)


# "Room" or "Chunk" where each country will be in
class map_chunk():
    def __init__(self, index, name, country, borders_dict, bg):

        # Where the chunk appears in the game.chunks list, might be used for validation
        self.index = index

        # The name of the chunk, used so we can distinguish lol
        self.name = name

        # List of countries that appear in the chunk
        self.country = country

        # Dictionary of chunks borders, where borders that can be crossed are True, and ones that cannot are False
        self.borders = borders_dict

        # Colour to display for background (WILL BE REPLACED WITH A SPRITE)
        self.bg = bg
        self.onscreen = False

    # Function for drawing the current chunk
    def update_draw(self, game):

        # Create a list of waves if the player has just moved to this chunk
        if not self.onscreen:

            self.waves_num = random.randint(19, 30)

            self.waves_obj = []
            for w in range(self.waves_num):
                self.make_wave(x=random.randint(0, game.win_w), game=game)

            self.onscreen = True

        # Fill the background with blue
        game.win.blit(self.bg, (0, 0))

        # If a wave is missing replace it
        if len(self.waves_obj) < self.waves_num:
            self.make_wave(x=-20, game=game)

        # Update all waves
        for w in self.waves_obj:
            w.update_move(self, game)
            w.update_draw(game)

        if self.country != None:
            self.country.update_move(game)
            self.country.update_draw(game)

    # Function for making waves
    def make_wave(self, x, game):
        self.waves_obj.append(wave(
            start_x=x,
            start_y=random.randint(0, game.win_h),
            length=random.choice(["Short", "Medium", "Long"]),
            sprites=game.waves_sprites))


# Wave class
class wave():
    def __init__(self, start_x, start_y, length, sprites):

        # Position
        self.x = start_x
        self.y = start_y

        # Modifier to the Y of where it is drawn
        self.y_mod = 0

        # Sprite to use, based on length of the wave
        self.sprite = sprites[length]

    def update_move(self, parent_chunk, game):
        self.x += 0.4

        # y_mod is set to y at a given point in a cosine wave
        self.y_mod = 10 * math.cos(self.x * 0.01)

        # If offscreen, delete
        if self.x > game.win_w:
            parent_chunk.waves_obj.remove(self)

    # Draw with given sprite
    def update_draw(self, game):
        game.win.blit(self.sprite, (self.x, self.y + self.y_mod))


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

        self.blinking = [False, 0]

        # Making a cool wave to bob the island up and down
        self.wave_x = 0
        self.y_mod = 0

    # Function for updating movement of player
    def update_move(self, game):
        # Get the position you are before you update
        self.old_x = self.x
        self.old_y = self.y

        if game.game_state == 0:
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
                self.x = 0

            elif on_border == "Up":
                self.y = game.win_h - (self.height // 2)

            elif on_border == "Down":
                self.y = 0

            # Calls the change_chunk() function with information about current border
            game.change_chunk(on_border)

        # If up and down are not pressed, then the island can play the bobbing animation
        if not any((game.keys[pygame.K_UP], game.keys[pygame.K_DOWN])):
            self.bob()

    # Function for adding a small bob to the island
    def bob(self):

        # Creates a value for y_mod using a cosine wave given an x position and wavelenth + period
        self.wave_x += 1
        self.y_mod = 10 * math.cos(self.wave_x * 0.08)

    # Function for checking whether player is on a border
    def border_check(self, game):

        border_pos = False

        # Checks which border you are on
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
        # Hitbox for island
        # pygame.draw.rect(game.win, (155, 40, 40), (self.x, self.y, self.width, self.height))

        # If the sprite is facing right then it does not need to be flipped
        blit_sprite = self.sprites[self.sprite_status]

        # Blit the given sprite at the position of the island
        game.win.blit(blit_sprite, (self.x, self.y + self.y_mod))


# Speechbubble sprite
speechbubble_var = pygame.image.load('data/sprites/ICONS/SpeechBubble.png')
sea_var = pygame.image.load('data/sprites/COUNTRIES/sea.png')

# Loading all sprites to be used and adding them to dictionaries
pangaea_sprites = {
    "Default" : pygame.image.load('data/sprites/COUNTRIES/pangea/head.png'),
    "Head" : pygame.image.load('data/sprites/COUNTRIES/pangea/head.png'),
    "happy" : pygame.image.load('data/sprites/COUNTRIES/pangea/happy.png'),
    "angry" : pygame.image.load('data/sprites/COUNTRIES/pangea/angry.png'),
    "sad" : pygame.image.load('data/sprites/COUNTRIES/pangea/sad.png'),
    "SpeechBubble" : speechbubble_var
}
africa_sprites = {
    "Head" : pygame.image.load('data/sprites/COUNTRIES/africa/head.png'),
    "happy" : pygame.image.load('data/sprites/COUNTRIES/africa/happy.png'),
    "angry" : pygame.image.load('data/sprites/COUNTRIES/africa/angry.png'),
    "sad" : pygame.image.load('data/sprites/COUNTRIES/africa/sad.png'),
    "SpeechBubble" : speechbubble_var
}
australia_sprites = {
    "Head" : pygame.image.load('data/sprites/COUNTRIES/australia/head.png'),
    "happy" : pygame.image.load('data/sprites/COUNTRIES/australia/happy.png'),
    "angry" : pygame.image.load('data/sprites/COUNTRIES/australia/angry.png'),
    "sad" : pygame.image.load('data/sprites/COUNTRIES/australia/sad.png'),
    "SpeechBubble" : speechbubble_var
}
euraisa_sprites = {
    "Head" : pygame.image.load('data/sprites/COUNTRIES/euraisa/head.png'),
    "happy" : pygame.image.load('data/sprites/COUNTRIES/euraisa/happy.png'),
    "angry" : pygame.image.load('data/sprites/COUNTRIES/euraisa/angry.png'),
    "sad" : pygame.image.load('data/sprites/COUNTRIES/euraisa/sad.png'),
    "SpeechBubble" : speechbubble_var
}
india_sprites = {
    "Head" : pygame.image.load('data/sprites/COUNTRIES/india/head.png'),
    "happy" : pygame.image.load('data/sprites/COUNTRIES/india/happy.png'),
    "angry" : pygame.image.load('data/sprites/COUNTRIES/india/angry.png'),
    "sad" : pygame.image.load('data/sprites/COUNTRIES/india/sad.png'),
    "SpeechBubble" : speechbubble_var
}
north_america_sprites = {
    "Head" : pygame.image.load('data/sprites/COUNTRIES/northAmerica/head.png'),
    "happy" : pygame.image.load('data/sprites/COUNTRIES/northAmerica/happy.png'),
    "angry" : pygame.image.load('data/sprites/COUNTRIES/northAmerica/angry.png'),
    "sad" : pygame.image.load('data/sprites/COUNTRIES/northAmerica/sad.png'),
    "SpeechBubble" : speechbubble_var
}
south_america_sprites = {
    "Head" : pygame.image.load('data/sprites/COUNTRIES/southAmerica/head.png'),
    "happy" : pygame.image.load('data/sprites/COUNTRIES/southAmerica/happy.png'),
    "angry" : pygame.image.load('data/sprites/COUNTRIES/southAmerica/angry.png'),
    "sad" : pygame.image.load('data/sprites/COUNTRIES/southAmerica/sad.png'),
    "SpeechBubble" : speechbubble_var
}

wave_sprites = {
    "Short" : pygame.image.load('data/sprites/WaveShort.png'),
    "Medium" : pygame.image.load('data/sprites/WaveMedium.png'),
    "Long" : pygame.image.load('data/sprites/WaveLong.png'),
}

xo_sprite_dict = {
    "None" : pygame.image.load("data/sprites/ICONS/empty.png"),
    "X" : pygame.image.load("data/sprites/ICONS/x.png"),
    "O" : pygame.image.load("data/sprites/ICONS/o.png"),
}

# North America
text_file = open("data/scripts/northAmerica.txt", "r").readlines()
NA_script = [i.replace("\n", "") for i in text_file]

# South America
text_file = open("data/scripts/southAmerica.txt", "r").readlines()
SA_script = [i.replace("\n", "") for i in text_file]

# India
text_file = open("data/scripts/india.txt", "r").readlines()
india_script = [i.replace("\n", "") for i in text_file]

# Eurasia, one and two
text_file = open("data/scripts/euraisa1.txt", "r").readlines()
euraisa1_script = [i.replace("\n", "") for i in text_file]
text_file = open("data/scripts/euraisa2.txt", "r").readlines()
euraisa2_script = [i.replace("\n", "") for i in text_file]

# Australia
text_file = open("data/scripts/australia.txt", "r").readlines()
australia_script = [i.replace("\n", "") for i in text_file]

# Africa
text_file = open("data/scripts/africa.txt", "r").readlines()
africa_script = [i.replace("\n", "") for i in text_file]

# Island objects
north_america = island(x=200, y=150, name="NORTH AMERICA", sprites_dict=north_america_sprites, dialogue=NA_script, pangaea_sprites=pangaea_sprites)
south_america = island(x=200, y=150, name="SOUTH AMERICA", sprites_dict=south_america_sprites, dialogue=SA_script, pangaea_sprites=pangaea_sprites)
africa = island(x=800, y=300, name="AFRICA", sprites_dict=africa_sprites, dialogue=africa_script, pangaea_sprites=pangaea_sprites)
india = island(x=800, y=300, name="INDIA", sprites_dict=india_sprites, dialogue=india_script, pangaea_sprites=pangaea_sprites)
australia = island(x=500, y=300, name="AUSTRALIA", sprites_dict=australia_sprites, dialogue=australia_script, pangaea_sprites=pangaea_sprites)

# List of chunks generated when they are instantiated
local_chunks = [
    map_chunk(index=0, name="Top-Left", country=south_america, borders_dict={"Left" : False, "Right" : True, "Up" : False, "Down" : True}, bg=sea_var),
    map_chunk(index=1, name="Top-Middle", country=north_america, borders_dict={"Left": True, "Right": True, "Up": False, "Down": True}, bg=sea_var),
    map_chunk(index=2, name="Top-Right", country=None, borders_dict={"Left" : True, "Right" : False, "Up" : False, "Down" : True}, bg=sea_var),
    map_chunk(index=3, name="Middle-Left", country=None, borders_dict={"Left" : False, "Right" : True, "Up" : True, "Down" : True}, bg=sea_var),
    map_chunk(index=4, name="Middle-Middle", country=None, borders_dict={"Left": True, "Right": True, "Up": True, "Down": True}, bg=sea_var),
    map_chunk(index=5, name="Middle-Right", country=africa, borders_dict={"Left" : True, "Right" : False, "Up" : True, "Down" : True}, bg=sea_var),
    map_chunk(index=6, name="Bottom-Left", country=None, borders_dict={"Left" : False, "Right" : True, "Up" : True, "Down" : False}, bg=sea_var),
    map_chunk(index=7, name="Bottom-Middle", country=india, borders_dict={"Left": True, "Right": True, "Up": True, "Down": False}, bg=sea_var),
    map_chunk(index=8, name="Bottom-Right", country=australia, borders_dict={"Left" : True, "Right" : False, "Up" : True, "Down" : False}, bg=sea_var)
]

# UI elements for VN screen
vn_sprites_dict = {
    "Overlay" : pygame.image.load('data/sprites/VNUI/purpleoverlay.png'),
    "Textbox" : pygame.image.load('data/sprites/VNUI/DialogueBox.png')
    }

# Instantiate object for storing game info
game = game_info(win_w=1280, win_h=720, chunks=local_chunks, start_chunk=4, waves_dict=wave_sprites, vn_sprites=vn_sprites_dict, xo_sprites=xo_sprite_dict)

# Instantiate player object
pangea = player(start_x=600, start_y=400, speed=5, start_width=270, start_height=170, sprites_dict=pangaea_sprites)

# Maintain consistent framerate
clock = pygame.time.Clock()

# Mainloop
while game.run:
    clock.tick(60)

    # Update pygame display and delete everything
    pygame.display.update()
    game.win.fill((0, 0, 0))

    # Update which keys are pressed down by the user
    game.update_keys()

    # Draw the current chunk
    game.chunks[game.current_chunk].update_draw(game)

    # Update the player character's movement and draw them
    pangea.update_move(game)
    pangea.update_draw(game)

    if game.game_state == 1:
        # VN TIME
        game.update_VNUI()

    if game.game_state == 2:
        # minigame time
        game.minigame_update()
        pass

    # Check for closing of window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.run = False

# When mainloop is broken, quit
pygame.quit()
