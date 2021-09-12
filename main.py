# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 23
# Lighting Effect
# Video link: https://youtu.be/IWm5hi5Yrvk
import pygame as pg
import sys
from random import choice, random
from os import path
from settings import *
from sprites import *
from tilemap import *


def draw_text(surface: pg.surface.Surface, text: str, font_name: str, size: int, color: tuple, x: int, y: int, align="topleft", background=None):
    """Draw text on a surface.

    Args:
        surface (pg.surface.Surface): surface where to draw text
        text (str): text to display
        font_name (str): font path
        size (int): font size
        color (tuple): text color, (R, G, B) format
        x (int): text position on horizontal axis
        y (int): text position on vertical axis
        align (str, optional): (x, y) position compared to text. Defaults to "topleft".
        background (tuple, optional): background color to optimize computation. Defaults to None
    """
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, color, background)
    text_rect = text_surface.get_rect(**{align: (x, y)})
    surface.blit(text_surface, text_rect)


class Game:
    def __init__(self):
        """Class used to create the game.
        """
        pg.mixer.pre_init(44100, -16, 4, 2048)                          # initialize sound mixer
        pg.init()                                                       # initialize pygame
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()                                    # game clock
        self.load_data()

    def load_data(self):
        """Load data used by the game.
        """
        # folders path
        game_folder = path.dirname(__file__)
        self.img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        self.map_folder = path.join(game_folder, 'maps')
        
        # load images
        self.player_images = {}
        for image in PLAYER_IMAGES:
            self.player_images[image] = pg.image.load(path.join(self.img_folder, PLAYER_IMAGES[image])).convert_alpha()
            self.player_images[image] = pg.transform.scale(self.player_images[image], PLAYER_DIMENSIONS)
            self.player_images[image].set_colorkey(PLAYER_BACKGROUND_COLOR)     # remove background pixels
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(self.img_folder, ITEM_IMAGES[item])).convert_alpha()
        # Sound loading
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
        
        # create pause screen background
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        # create dialog box
        self.dialog_box = pg.Surface((WIDTH, HEIGHT/4))
        self.dialog_box.fill(WHITE)
        # lighting effect
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(self.img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)                             # resize image
        self.light_rect = self.light_mask.get_rect()

    def new(self):
        """Initialize all variables and do all the setup for a new game.
        """
        # create sprite groups
        self.map_sprites = pg.sprite.LayeredUpdates()                   # use layers to display sprites
        self.walls = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.npcs = pg.sprite.Group()
        self.players = pg.sprite.Group()
        
        # create the map
        self.map = TiledMap(path.join(self.map_folder, 'level1.tmx'))
        self.above_map = TiledMap(path.join(self.map_folder, 'level1_above_layer.tmx'))
        self.map_img = self.map.make_map()
        self.above_map_img = self.above_map.make_map(0)
        self.map.rect = self.map_img.get_rect()
        self.above_map.rect = self.above_map_img.get_rect()
        self.ncpc_list = []
        self.NPC_images = {}
        # create objects and walls on the map
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'NPC':
                self.NPC_images[tile_object.type] = {}
                for image in NPC_IMAGES[tile_object.type]:
                    self.NPC_images[tile_object.type][image] = pg.image.load(path.join(self.img_folder, NPC_IMAGES[tile_object.type][image])).convert_alpha()
                    self.NPC_images[tile_object.type][image] = pg.transform.scale(self.NPC_images[tile_object.type][image], NPC_DIMENSIONS)
                    self.NPC_images[tile_object.type][image].set_colorkey(NPC_BACKGROUND_COLOR)     # remove background pixels
                self.ncpc_list.append(NPC(self, obj_center.x, obj_center.y, tile_object.type))
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name in ['health', 'shotgun']:
                Item(self, obj_center, tile_object.name)
                
        # create the game camera
        self.camera = Camera(self.map.width, self.map.height)
        # initialize the game parameters
        self.draw_debug = False
        self.paused = False
        self.night = False
        self.freezed = False
        self.showing_message = False
        # play the start sound
        self.effects_sounds['level_start'].play()

    def run(self):
        """Run the game loop.
        
        Set self.playing = False to end the game.
        """
        self.playing = True
        pg.mixer.music.play(loops=-1)               # loop the music
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0  # get the elapsed time between two frames
            self.events()
            self.update()
            self.draw()

    def quit(self):
        """Close the game.
        """
        pg.quit()
        sys.exit()

    def update(self):
        """Update all the elements of the game.
        """
        self.screen.fill(BLACK)
        self.map_sprites.update()   # use the method update for each sprite
        self.camera.update(self.player) # the camera follow the player

    def render_fog(self):
        """Draw the light mask (gradient) onto fog image.
        """
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center  # light on the player
        self.fog.blit(self.light_mask, self.light_rect)     # make white gradient on the player, everything else is black
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)     # make white transparent, black stay black

    def draw(self):
        """Update the screen.
        """
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))   # fps
        self.screen.blit(self.map_img, self.camera.apply(self.map))     # draw the map at the correct position for the camera
        # update sprites on the map
        for sprite in self.map_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))   # draw the sprites at the correct position for the camera
            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1) # draw hitboxes
        self.screen.blit(self.above_map_img, self.camera.apply(self.above_map))     # draw the above elements at the correct position for the camera
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)   # draw walls hitboxes

        if self.night:
            self.render_fog()
        # HUD functions
        # displaying message
        if self.showing_message:
            dialog_box = self.dialog_box.copy()
            for index, text in enumerate(self.messages[self.message_index]):
                draw_text(dialog_box, text, ARIAL_FONT, 20, BLACK, 20, 20 + 40*index, background=WHITE)
            self.screen.blit(dialog_box, (0, 3*HEIGHT/4))
        # pause screen
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            draw_text(self.screen, "Paused", ARIAL_FONT, 105, RED, WIDTH / 2, HEIGHT / 2, align="center")
        pg.display.flip()   # update screen

    def events(self):
        """Manage player inputs.
        """
        # catch all events here
        events = pg.event.get()
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    if self.showing_message:
                        self.scroll_messages()
                elif event.key == pg.K_e:
                    if self.showing_message:
                        self.scroll_messages()
                    elif not self.freezed:
                        self.player.interact()
                elif event.key == pg.K_ESCAPE:
                    self.quit()
                elif event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                elif event.key == pg.K_p:
                    self.paused = not self.paused
                elif event.key == pg.K_n:
                    self.night = not self.night
            elif event.type == pg.QUIT:
                self.quit()
        # control player on the map
        if not self.freezed:
            self.player.get_keys()
    
    def display_messages(self, messages: list):
        """Display dialog box with elements from message list.

        Args:
            messages (list): list of messages to display
        """
        self.messages = messages
        self.messages_nb = len(messages)
        self.message_index = 0
        if self.message_index < self.messages_nb:
            self.showing_message = True
        else:
            self.freezed = False
    
    def scroll_messages(self):
        self.message_index += 1
        if self.message_index >= self.messages_nb:
            self.showing_message = False
            self.freezed = False

    def show_start_screen(self):
        """Do NOT draw a start screen.
        """
        pass

    def wait_for_key(self):
        """Wait for the player to press a key and release it.
        """
        pg.event.wait()     # clear events
        waiting = True
        while waiting:
            self.clock.tick(FPS)    # wait during a frame
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:  # when key released
                    waiting = False

# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
