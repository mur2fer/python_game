import pygame as pg
vec = pg.math.Vector2

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

# game settings
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = BLACK

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Player settings
PLAYER_DIMENSIONS = (56, 84)#(37, 56)#(56, 84)
PLAYER_BACKGROUND_COLOR = (255,0,228)
PLAYER_IMG_OFFSET = (PLAYER_DIMENSIONS[1]-TILESIZE)//2 + TILESIZE//16  # if player sprite taller than tiles; number of pixels to shift upside
WALKING_SPEED = 4*TILESIZE
RUNNING_SPEED = 8*TILESIZE
TIME_ROTATE = 100   # time waiting before moving after rotation
TIME_KEEP_MOVING = 50   # time after moving while player will move (and not only rotate) if input direction is different
PLAYER_IMAGES = {'UP_still': 'player/Male_player_still_up.png',
                 'DOWN_still': 'player/Male_player_still_down.png',
                 'LEFT_still': 'player/Male_player_still_left.png',
                 'RIGHT_still': 'player/Male_player_still_right.png'}
PLAYER_HIT_RECT = pg.Rect(0, 0, TILESIZE, TILESIZE)

# NPC settings
NPC_DIMENSIONS = (56, 80)#(37, 52)#(56, 80)
NPC_BACKGROUND_COLOR = (115, 197, 165)
NPC_IMG_OFFSET = (NPC_DIMENSIONS[1]-TILESIZE)//2 + TILESIZE//16  # if npc sprite taller than tiles; number of pixels to shift upside
NPC_IMAGES = {'Ace_trainer': {'UP_still': 'NPC/Ace_trainer_still_up.png',
                              'DOWN_still': 'NPC/Ace_trainer_still_down.png',
                              'LEFT_still': 'NPC/Ace_trainer_still_left.png',
                              'RIGHT_still': 'NPC/Ace_trainer_still_right.png'}
              }
NPC_HIT_RECT = pg.Rect(0, 0, TILESIZE, TILESIZE)
NPC_MOVEMENT_LIST = ['up', 'up', 'right', 'down', 'down', 'left']
MOVEMENT_COOLDOWN = 2000        # time between two NPC movements

# Effects
NIGHT_COLOR = (20, 20, 20)
LIGHT_RADIUS = (500, 500)
LIGHT_MASK = "light_350_soft.png"

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 3
NPC_BELOW_LAYER = 2
NPC_ABOVE_LAYER = 4
ITEMS_LAYER = 1

# Items
ITEM_IMAGES = {'health': 'health_pack.png',
               'shotgun': 'obj_shotgun.png'}
BOB_RANGE = 10
BOB_SPEED = 0.3

# Sounds
BG_MUSIC = 'espionage.ogg'
EFFECTS_SOUNDS = {'level_start': 'level_start.wav'}
