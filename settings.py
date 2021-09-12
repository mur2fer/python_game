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

# direction constants
ROT_RIGHT = 0
ROT_UP = 90
ROT_LEFT = 180
ROT_DOWN = 270
RIGHT = 'RIGHT'
UP = 'UP'
LEFT = 'LEFT'
DOWN = 'DOWN'

# Player settings
PLAYER_DIMENSIONS = (64, 88)
PLAYER_BACKGROUND_COLOR = (255,0,228)
PLAYER_IMG_OFFSET = (PLAYER_DIMENSIONS[1]-TILESIZE)//2  # align player with tile
WALKING_SPEED = 4*TILESIZE
WALK_TIME = 1000*TILESIZE/WALKING_SPEED
RUNNING_SPEED = 8*TILESIZE
RUN_TIME = 1000*TILESIZE/RUNNING_SPEED
TIME_ROTATE = 100   # time waiting before moving after rotation
TIME_KEEP_MOVING = 100   # time after moving while player will move (and not only rotate) if input direction is different
PLAYER_IMAGES = {'UP_still': 'player/Male_player_still_up.png',
                 'DOWN_still': 'player/Male_player_still_down.png',
                 'LEFT_still': 'player/Male_player_still_left.png',
                 'RIGHT_still': 'player/Male_player_still_right.png',
                 'UP_walking1': 'player/Male_player_walking1_up.png',
                 'DOWN_walking1': 'player/Male_player_walking1_down.png',
                 'LEFT_walking1': 'player/Male_player_walking1_left.png',
                 'RIGHT_walking1': 'player/Male_player_walking1_right.png',
                 'UP_walking2': 'player/Male_player_walking2_up.png',
                 'DOWN_walking2': 'player/Male_player_walking2_down.png',
                 'LEFT_walking2': 'player/Male_player_walking2_left.png',
                 'RIGHT_walking2': 'player/Male_player_walking2_right.png',
                 'UP_run_still': 'player/Male_player_run_still_up.png',
                 'DOWN_run_still': 'player/Male_player_run_still_down.png',
                 'LEFT_run_still': 'player/Male_player_run_still_left.png',
                 'RIGHT_run_still': 'player/Male_player_run_still_right.png',
                 'UP_running1': 'player/Male_player_running1_up.png',
                 'DOWN_running1': 'player/Male_player_running1_down.png',
                 'LEFT_running1': 'player/Male_player_running1_left.png',
                 'RIGHT_running1': 'player/Male_player_running1_right.png',
                 'UP_running2': 'player/Male_player_running2_up.png',
                 'DOWN_running2': 'player/Male_player_running2_down.png',
                 'LEFT_running2': 'player/Male_player_running2_left.png',
                 'RIGHT_running2': 'player/Male_player_running2_right.png',}
PLAYER_HIT_RECT = pg.Rect(0, 0, TILESIZE, TILESIZE)
WALK_ANIM_LENGTH = 4     # number of frame in the full walk animation
STEP_ANIM_LENGTH = 2     # number of frames to do a step
WALK_ANIM_TIME = 3*WALK_TIME/5
WALK_STILL_TIME = 2*WALK_TIME/5
RUN_ANIM_TIME = 3*RUN_TIME/5
RUN_STILL_TIME = 2*RUN_TIME/5
ROT_ANIMATION = [('_still', 0), ('_walking1', TIME_ROTATE), ('_still', 0), ('_walking2', TIME_ROTATE)]
WALKING_ANIMATION = [('_still', WALK_STILL_TIME), ('_walking1', WALK_ANIM_TIME), ('_still', WALK_STILL_TIME), ('_walking2', WALK_ANIM_TIME)]
BONK_ANIMATION = [('_still', 2*WALK_STILL_TIME), ('_walking1', 2*WALK_ANIM_TIME), ('_still', 2*WALK_STILL_TIME), ('_walking2', 2*WALK_ANIM_TIME)]
RUNNING_ANIMATION = [('_run_still', RUN_STILL_TIME), ('_running1', RUN_ANIM_TIME), ('_run_still', RUN_STILL_TIME), ('_running2', RUN_ANIM_TIME)]

# NPC settings
NPC_DIMENSIONS = (56, 80)
NPC_BACKGROUND_COLOR = (115, 197, 165)
NPC_IMG_OFFSET = (NPC_DIMENSIONS[1]-TILESIZE)//2 + TILESIZE//16  # if npc sprite taller than tiles; number of pixels to shift upside
NPC_IMAGES = {'Ace_trainer': {'UP_still': 'NPC/Ace_trainer_still_up.png',
                              'DOWN_still': 'NPC/Ace_trainer_still_down.png',
                              'LEFT_still': 'NPC/Ace_trainer_still_left.png',
                              'RIGHT_still': 'NPC/Ace_trainer_still_right.png',
                              'UP_walking1': 'NPC/Ace_trainer_walking1_up.png',
                              'DOWN_walking1': 'NPC/Ace_trainer_walking1_down.png',
                              'LEFT_walking1': 'NPC/Ace_trainer_walking1_left.png',
                              'RIGHT_walking1': 'NPC/Ace_trainer_walking1_right.png',
                              'UP_walking2': 'NPC/Ace_trainer_walking2_up.png',
                              'DOWN_walking2': 'NPC/Ace_trainer_walking2_down.png',
                              'LEFT_walking2': 'NPC/Ace_trainer_walking2_left.png',
                              'RIGHT_walking2': 'NPC/Ace_trainer_walking2_right.png'}
              }
NPC_HIT_RECT = pg.Rect(0, 0, TILESIZE, TILESIZE)
MOVE = 0
ROTATE = 1
NPC_MOVEMENT_LIST = [(MOVE, UP), (MOVE, UP), (ROTATE, RIGHT), (MOVE, RIGHT), (MOVE, DOWN), (MOVE, DOWN), (MOVE, LEFT)]
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

# Fonts
ARIAL_FONT = pg.font.match_font('arial')
