
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import math
import random

import sys
import os

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

        def checkwin():
            nonecounter = 0
            # check if 3 in a row
            # possible combinations:
            # 3 horizontal, 3 vertical, 2 diagonal
            for l in range(9):
                # horizontal
                # get left most tile
                # check if the two next to it are the same
                # done
                if(l%3 == 0 and self.xo_board[l] != "None"):
                    if(self.xo_board[l] == self.xo_board[l+1] == self.xo_board[l+2]):
                        return self.xo_board[l]

                # vertical
                # get top most tile
                # check if the two below it are the same
                if(l < 3 and self.xo_board[l] != "None"):
                    if(self.xo_board[l] == self.xo_board[l+3] == self.xo_board[l+6]):
                        return self.xo_board[l]

                # diagonal
                # get top left tile
                # check the diagonals
                if(self.xo_board[0] == self.xo_board[4] == self.xo_board[8] != "None"):
                    return self.xo_board[0]

                if(self.xo_board[2] == self.xo_board[4] == self.xo_board[6] != "None"):
                    return self.xo_board[2]

                # if draw
                if(l == 0):
                    nonecounter = 0
                if(self.xo_board[l] == "None"):
                    nonecounter += 1
                if(l == 8):
                    # print(nonecounter)
                    if(nonecounter == 0):
                        return "Draw"
            return "None"
        # checkwin()
        if(checkwin() == "X"):
            # you win
            print("X won")
            pangea.gained_countries.append(self.chunks[self.current_chunk].country)
            self.game_state = 0
        elif(checkwin() == "O"):
            # they win
            print("O won")
            self.game_state = 0
        elif(checkwin() == "Draw"):
            #bruh
            print("Draw")
            pass

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

        self.upsidedown = False
        # THE font
        dialogue_font = pygame.font.Font(fix_path("data\\Roboto.ttf"), 35)

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
                if(self.upsidedown):
                    game.win.blit(pygame.transform.flip(line, False, True), (50, game.textbox_y[0] + 70 + (50*i)))
                    continue
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
        self.upsidedown = False
        if game.game_state == 1:
            try:
                if self.dialogue_speaker_text[self.dialogue_index] == "PANGAEA":
                    game.win.blit(self.pangaea_sprites[self.dialogue_emotion[self.dialogue_index]], game.char_pos)
                elif self.dialogue_speaker_text[self.dialogue_index] == "AUSTRALIA":
                    self.upsidedown = True
                    game.win.blit(self.sprites[self.dialogue_emotion[self.dialogue_index]], game.char_pos)
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

        self.gained_countries = [] # list of countries they have beaten in x's and o's

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


def fix_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    abs_path = os.path.join(base_path, relative_path)

    if sys.platform == "linux" or sys.platform == "linux2":
        abs_path = abs_path.replace("\\", "/")

    print(abs_path)
    return abs_path


# Speechbubble sprite
speechbubble_var = pygame.image.load(fix_path('data\\sprites\\ICONS\\SpeechBubble.png'))
sea_var = pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\sea.png'))

# Loading all sprites to be used and adding them to dictionaries
pangaea_sprites = {
    "Default" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\pangea\\head.png')),
    "Head" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\pangea\\head.png')),
    "happy" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\pangea\\happy.png')),
    "angry" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\pangea\\angry.png')),
    "sad" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\pangea\\sad.png')),
    "SpeechBubble" : speechbubble_var
}
africa_sprites = {
    "Head" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\africa\\head.png')),
    "happy" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\africa\\happy.png')),
    "angry" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\africa\\angry.png')),
    "sad" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\africa\\sad.png')),
    "SpeechBubble" : speechbubble_var
}
australia_sprites = {
    "Head" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\australia\\head.png')),
    "happy" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\australia\\happy.png')),
    "angry" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\australia\\angry.png')),
    "sad" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\australia\\sad.png')),
    "SpeechBubble" : speechbubble_var
}
euraisa_sprites = {
    "Head" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\euraisa\\head.png')),
    "happy" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\euraisa\\happy.png')),
    "angry" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\euraisa\\angry.png')),
    "sad" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\euraisa\\sad.png')),
    "SpeechBubble" : speechbubble_var
}
india_sprites = {
    "Head" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\india\\head.png')),
    "happy" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\india\\happy.png')),
    "angry" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\india\\angry.png')),
    "sad" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\india\\sad.png')),
    "SpeechBubble" : speechbubble_var
}
north_america_sprites = {
    "Head" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\northAmerica\\head.png')),
    "happy" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\northAmerica\\happy.png')),
    "angry" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\northAmerica\\angry.png')),
    "sad" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\northAmerica\\sad.png')),
    "SpeechBubble" : speechbubble_var
}
south_america_sprites = {
    "Head" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\southAmerica\\head.png')),
    "happy" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\southAmerica\\happy.png')),
    "angry" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\southAmerica\\angry.png')),
    "sad" : pygame.image.load(fix_path('data\\sprites\\COUNTRIES\\southAmerica\\sad.png')),
    "SpeechBubble" : speechbubble_var
}

wave_sprites = {
    "Short" : pygame.image.load(fix_path('data\\sprites\\WaveShort.png')),
    "Medium" : pygame.image.load(fix_path('data\\sprites\\WaveMedium.png')),
    "Long" : pygame.image.load(fix_path('data\\sprites\\WaveLong.png')),
}

xo_sprite_dict = {
    "None" : pygame.image.load(fix_path("data\\sprites\\ICONS\\empty.png")),
    "X" : pygame.image.load(fix_path("data\\sprites\\ICONS\\x.png")),
    "O" : pygame.image.load(fix_path("data\\sprites\\ICONS\\o.png")),
}

# North America
NA_script = [

    "PANGAEA: Hey, North America! : happy",
    "NORTH AMERICA: Ay, Pangy my Mangy! What is going on? : happy",
    "PANGAEA: Oh, you know, just the usual. : sad",
    "PANGAEA: Hey, actually, it just occurred to me, |I had this little tiny idea that maybe you might wanna hear? : happy",
    "NORTH AMERICA : Fire away, my dude. : happy",
    "PANGAEA: Well, I was thinking maybe you, and me, |and all of the other continents could kind of come together - : happy",
    "NORTH AMERICA: Oh, to have like a party or something? : happy",
    "PANGAEA: No, not quite. I was thinking something a little more... permanent. |Like, living together permanently. : sad",
    "NORTH AMERICA: Oh, I don't know about that, man. |I can't see myself lasting more than two-hundred and seventy years |with that stuck-up Eurasia. : angry",
    "NORTH AMERICA: They're so far up their oceanic ridge, you know what I mean? : angry",
    "PANGAEA: Well, I don't think they're gonna be involved... |look, could you please just consider?  : sad",
    "PANGAEA: I think it would be a really good way to get to |know each other and really feel like we're part of a family! : sad",
    "NORTH AMERICA: ...Well, I can't deny your passion... : sad",
    "NORTH AMERICA: are you a gambler, Pangy? : happy",
    "PANGAEA: Uh... : sad",
    "NORTH AMERICA: 'Cause I'm thinking this- we play a little game of exes and ohs, |and if you win, I'll join your little country club. If I win... : happy",
    "PANGAEA: ... : sad",
    "NORTH AMERICA: ...You know what, let's just play. : sad"

]

# South America
SA_script = [

    "PANGAEA: Oi, South America! : happy",
    "SOUTH AMERICA: May I help you, Pangaea? : happy",
    "PANGAEA: Yes! Well, actually, I wouldn't call it helping. |If anything, I'll be the one helping you. : happy",
    "SOUTH AMERICA: What do you mean? Do you think I need help with something? : happy",
    "PANGAEA: No! That's not what I meant at all! I just meant... look, |I have an idea, and I'd like you to hear me out. : happy",
    "SOUTH AMERICA: Okay? : happy",
    "PANGAEA: See, I was thinking about us, the continents, |and how we're all so... distant from one another. : sad",
    "PANGAEA: Not even you and North America are close, |which raises a lot of questions as to why you're even named |North and South America, but that's besides the point... : sad",
    "SOUTH AMERICA: Beside what point exactly, Pangaea? |You haven't made an ounce of sense since you started talking at me. : angry",
    "PANGAEA: Right, okay, so, basically my point is that we should all be closer! |Like, physically closer. |Like, stuck together like one giant supercontinent closer. : happy",
    "SOUTH AMERICA: Okay, now I'm starting to miss ten seconds ago when you weren't |making sense but at least I didn't have that image in my head. : happy",
    "PANGAEA: Come on, Southy! Don't be that way! : happy",
    "SOUTH AMERICA: Please never call me that again. : angry",
    "PANGAEA: Okay, but at least tell me what's so bad about my idea? : sad",
    "SOUTH AMERICA: I don't know about you, but I don't quite fancy the idea of being |attached to you or any other continent, for that matter. |I like being an independent continent. : happy",
    "PANGAEA: But your name doesn't even make sense that way! |At least if we're all together, |you can be down south and justify your name! : happy",
    "SOUTH AMERICA: What is it with you and my name? : sad",
    "PANGAEA: Nothing... look, how about we settle this over a game of exes and ohs? : happy",
    "SOUTH AMERICA: Exes and ohs... North America loves that method of diplomacy. |Okay, Pangaea. You're on. : happy"


]

# India
india_script = [

    "PANGAEA: India! : happy",
    "INDIA: Pangaea. : happy",
    "PANGAEA: What is up, buddy? : happy",
    "INDIA: Nothing. : happy",
    "PANGAEA: Nothing? Well, isn't that a shame. |If only there was something somebody could do about that... : sad",
    "INDIA: ... : happy",
    "PANGAEA: ...Aren't you going to ask me if there's something I can do about that? : sad",
    "INDIA: Why would I do that? : angry",
    "PANGAEA: ...Because I implied there is something I can do about that? |With the tone of my voice? : angry",
    "INDIA: What if I don't care? : happy",
    "PANGAEA: ...Don't you want some excitement in your life? : happy",
    "INDIA: There has never once been excitement in my life. |I rose from the ocean and have drifted slowly around for millennia since. |Why now would I suddenly have a craving for something new? : angry",
    "PANGAEA: Well, I don't know about you, but it sort of seems |to me like you need excitement more than you might want it. And |I have the perfect thing to provide you with just the right amount of it. : happy",
    "INDIA: And what would that be? : happy",
    "PANGAEA: A new lifestyle! Picture this; |you, me, and all the other continents together as one super continent! : happy",
    "INDIA: My tectonic plates are quaking at the very thought. : happy",
    "PANGAEA: Oh, come on! It'll be fun! How about this |we play a round of exes and ohs, and if I win, you come and live with me and the others. : happy",
    "INDIA: Assuming the others are as bad at exes and ohs as I am. : sad",
    "PANGAEA: ...Yeah. : sad"

]

# Eurasia, one and two
euraisa1_script = [

    "PANGAEA: Hey there, Eurasia! : happy",
    "EURASIA: What do you want, Pangaea. : angry",
    "PANGAEA: Why do you assume that I want something? |Why can't I just be looking to catch up with an old friend? : happy",
    "EURASIA: I'm a big rock drifting through a sea of nothingness, the same as last time. |There's nothing to 'catch up' on. Now, what do you want? : angry",
    "PANGAEA: Well actually, you're wrong, because there is something to catch up on: |I have an idea. : happy",
    "EURASIA: Oh, boy. : angry",
    "PANGAEA: You see, I've been thinking: isn't it sad how you, me, |and all the other continents are just drifting around the place, |only bumping into each other every few million years? : happy",
    "EURASIA: No... : angry",
    "PANGAEA: Well, I was thinking it would be nice if we all joined together... permanently! |Like one big supercontinent as opposed to just a bunch of lonely mini continents! : happy",
    "EURASIA: ...That is, without a doubt, the dumbest idea I have ever heard. : angry",
    "PANGAEA: Why?! : sad",
    "EURASIA: Because nobody is going to agree to that. We'll all just clash together. |Besides, what would we be called? : angry",
    "PANGAEA: I don't know, I was thinking because it was my idea, |we could all collectively just… go by Pangaea? : happy",
    "EURASIA: Hah! Pangaea, you make me laugh. You will never be a supercontinent. : happy",
    "PANGAEA: Well, you'll know where to find us when we're all throwing our cool party together. |Spoiler alert: it won't be in this miserable corner of the ocean! : happy"

]

euraisa2_script = [

    "EURASIA: (spits out tea) Pangaea, is that you? : happy",
    "PANGAEA: 'Pangaea' is dead. My name is... actually, my name is still Pangaea, |I'm just bigger now, I guess. : happy",
    "EURASIA: You did it... you got all the other continents to join your little club. |I have to say, I'm impressed. : happy",
    "PANGAEA: Wow, Eurasia, are you complimenting me? |And it's not even a backhanded compliment! : happy",
    "EURASIA: Well, I kind of implied that I didn't think you had it in you. |Don't flatter yourself there, Pangaea. : happy",
    "PANGAEA: Whatever. So, have you reconsidered now that you can see all the fun you're missing out on? : happy",
    "EURASIA: You know what... yeah, actually. I have. : happy",
    "PANGAEA: Really? Wow, that was... not the answer I was expecting from you, Eurasia. : happy",
    "EURASIA: ...But only on one condition: I get to be the supercontinent's namesake. : happy",
    "PANGAEA: Woah, woah woah, hold it there, pal. |You can't just dismiss my idea and then try to hijack it when it starts to come to fruition. |If you're joining, it's under my name. : angry",
    "NORTH AMERICA: Challenge them to exes and ohs, Pangy! : happy",
    "AFRICA: Yeah, you beat all of us at the game! This won't be any different! : happy",
    "EURASIA: You heard your friends, Pangaea. We'll settle this disagreement over a simple little game of exes and ohs. |If you win, you get to keep your name and if I win... |Eurasia will get a whole lot bigger. : angry"
]

# Australia
australia_script = [

    "PANGAEA: G'day, Australia! : happy",
    "AUSTRALIA: You don't have to say g'day when you're talking to me, mate. : angry",
    "PANGAEA: Uh... yeah, haha. Anyway, I've got this idea, you wanna hear? : happy",
    "AUSTRALIA: Why not. Shoot. : happy",
    "PANGAEA: ...I'll just take that as a yes. |Okay, so, basically the idea is that all the continents live together, |as opposed to apart, which is obviously the way things are at the moment. : happy",
    "PANGAEA: How does that sound to you? : happy",
    "AUSTRALIA: Yeah, that sounds alright. : happy",
    "PANGAEA: ...I'm sorry, I'm having a little difficulty understanding |what you're saying. : sad",
    "AUSTRALIA: I said that sounds alright, mate! : angry",
    "PANGAEA: ...Yeah, I'm sorry man, I still have no idea what you're saying. |How about we decide over exes and ohs? : happy",
    "AUSTRALIA: There is literally no need for... oh, whatever. Let's get this done with. : angry"


]

# Africa
africa_script = [

    "PANGAEA: Hey, Africa! : happy",
    "AFRICA: Oh, hey there, Pangaea! All well? : happy",
    "PANGAEA: Yeah! I'm actually here with a proposition of sorts. : happy",
    "AFRICA: Oh, okay. What is it? : happy",
    "PANGAEA: Well, you know how all us continents are just kind of... drifting around, |only seeing each other every few million years? : happy",
    "AFRICA: Yeah? : sad",
    "PANGAEA: Well, wouldn't it be nice if we saw each other more regularly? : happy",
    "AFRICA: I suppose... I haven't really thought much about it. |The other continents don't converse much with me. : sad",
    "PANGAEA: Well, that's my point exactly. And I think I have a solution... : happy",
    "PANGAEA: We all move in together! |In the same spot in the ocean! What do you say? : happy",
    "AFRICA: Oh, wow... I don't know. It seems a bit radical. : sad",
    "PANGAEA: Well, how about I make it easier for you - We play a game of exes and ohs. |If I win, you're in. And if you win... : happy",
    "PANGAEA: You get to play me again and again until I win. : happy",
    "AFRICA: Doesn't sound like I have much in the way of choice, here. : angry",
    "PANGAEA: Hey, at least you'll get to spend more time with me either way. : happy"


]

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
    "Overlay" : pygame.image.load(fix_path('data\\sprites\\VNUI\\purpleoverlay.png')),
    "Textbox" : pygame.image.load(fix_path('data\\sprites\\VNUI\\DialogueBox.png'))
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
