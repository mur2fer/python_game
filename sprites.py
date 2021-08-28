import pygame as pg
from random import uniform, choice, randint, random
from settings import *
import pytweening as tween
from itertools import chain
vec = pg.math.Vector2

ROT_RIGHT = 0
ROT_UP = 90
ROT_LEFT = 180
ROT_DOWN = 270

def collide_hit_rect(one: pg.sprite.Sprite, two: pg.sprite.Sprite) -> bool:
    """Test if two hitboxes collide.

    Args:
        one (pg.sprite.Sprite): sprite one
        two (pg.sprite.Sprite): sprite two

    Returns:
        bool: result of test
    """
    return one.hit_rect.colliderect(two.hit_rect)


def collide_with_group(sprite: pg.sprite.Sprite, group: pg.sprite.Group, dir: str):
    """Avoid sprite going through the elements from the group.

    Args:
        sprite (pg.sprite.Sprite): sprite to apply the function to
        group (pg.sprite.Group): group to collide with
        dir (str): direction of the movement
    """
    hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)  # list of sprites which collide
    if hits:
        if dir == 'x+':
            if hits[0].hit_rect.centerx >= sprite.hit_rect.centerx:  # obstacle to the right
                sprite.hit_rect.centerx = hits[0].hit_rect.left - sprite.hit_rect.width / 2
        if dir == 'x-':
            if hits[0].hit_rect.centerx <= sprite.hit_rect.centerx:  # obstacle to the left
                sprite.hit_rect.centerx = hits[0].hit_rect.right + sprite.hit_rect.width / 2
        if dir == 'y+':
            if hits[0].hit_rect.centery >= sprite.hit_rect.centery:  # obstacle down
                sprite.hit_rect.centery = hits[0].hit_rect.top - sprite.hit_rect.height / 2
        if dir == 'y-':
            if hits[0].hit_rect.centery <= sprite.hit_rect.centery:  # obstacle up
                sprite.hit_rect.centery = hits[0].hit_rect.bottom + sprite.hit_rect.height / 2


class Player(pg.sprite.Sprite):
    def __init__(self, game, x: int, y: int):
        """Create a Player in the game.

        Args:
            game (Game): game used
            x (int): horizontal position of player center
            y (int): vertical position of player center
        """
        self._layer = PLAYER_LAYER  # to display on the good layer
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = ROT_RIGHT
        self.last_rot = pg.time.get_ticks()
        self.last_moved = pg.time.get_ticks()
        self.dir = 'x+'
        self.moving = False

    def get_keys(self):
        """Use the player inputs to control the character.
        """
        if not self.moving:
            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                if self.rot == ROT_LEFT:        # already in the same direction as input
                    if pg.time.get_ticks() - self.last_rot > TIME_ROTATE:   # allow rotation without moving for short input
                        # move player
                        self.hit_rect.centerx -= TILESIZE
                        self.moving = True
                else:
                    if pg.time.get_ticks() - self.last_moved < TIME_KEEP_MOVING:   # not stoping if rotate while moving
                        self.hit_rect.centerx -= TILESIZE
                        self.moving = True
                    # rotate sprite
                    self.last_rot = pg.time.get_ticks()
                    self.rot = ROT_LEFT
                    self.image = pg.transform.rotate(self.game.player_img, self.rot)
                    self.dir = 'x-'
            elif keys[pg.K_RIGHT] or keys[pg.K_d]:
                if self.rot == ROT_RIGHT:       # already in the same direction as input
                    if pg.time.get_ticks() - self.last_rot > TIME_ROTATE:   # allow rotation without moving for short input
                        # move player
                        self.hit_rect.centerx += TILESIZE
                        self.moving = True
                else:
                    if pg.time.get_ticks() - self.last_moved < TIME_KEEP_MOVING:   # not stoping if rotate while moving
                        self.hit_rect.centerx += TILESIZE
                        self.moving = True
                    # rotate sprite
                    self.last_rot = pg.time.get_ticks()
                    self.rot = ROT_RIGHT
                    self.image = pg.transform.rotate(self.game.player_img, self.rot)
                    self.dir = 'x+'
            elif keys[pg.K_UP] or keys[pg.K_w]:
                if self.rot == ROT_UP:          # already in the same direction as input
                    if pg.time.get_ticks() - self.last_rot > TIME_ROTATE:   # allow rotation without moving for short input
                        # move player
                        self.hit_rect.centery -= TILESIZE
                        self.moving = True
                else:
                    if pg.time.get_ticks() - self.last_moved < TIME_KEEP_MOVING:   # not stoping if rotate while moving
                        self.hit_rect.centery -= TILESIZE
                        self.moving = True
                    # rotate sprite
                    self.last_rot = pg.time.get_ticks()
                    self.rot = ROT_UP
                    self.image = pg.transform.rotate(self.game.player_img, self.rot)
                    self.dir = 'y-'
            elif keys[pg.K_DOWN] or keys[pg.K_s]:
                if self.rot == ROT_DOWN:        # already in the same direction as input
                    if pg.time.get_ticks() - self.last_rot > TIME_ROTATE:   # allow rotation without moving for short input
                        # move player
                        self.hit_rect.centery += TILESIZE
                        self.moving = True
                else:
                    if pg.time.get_ticks() - self.last_moved < TIME_KEEP_MOVING:   # not stoping if rotate while moving
                        self.hit_rect.centery += TILESIZE
                        self.moving = True
                    # rotate sprite
                    self.last_rot = pg.time.get_ticks()
                    self.rot = ROT_DOWN
                    self.image = pg.transform.rotate(self.game.player_img, self.rot)
                    self.dir = 'y+'

            if self.moving:
                if keys[pg.K_SPACE]:
                    self.vel = vec(PLAYER_RUNNING_SPEED, 0).rotate(-self.rot)
                else:
                    self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
                collide_with_group(self, self.game.walls, self.dir)
                collide_with_group(self, self.game.items, self.dir)
                

    def update(self):
        """Move player.
        """
        self.get_keys()
        if self.moving:
            self.pos += self.vel * self.game.dt     # compute new sprite position
            self.rect = self.image.get_rect()
            self.rect.center = self.pos             # position sprite
            if self.rot == ROT_RIGHT and self.rect.centerx >= self.hit_rect.centerx:    # when sprite reach its hitbox
                self.moving = False
            elif self.rot == ROT_LEFT and self.rect.centerx <= self.hit_rect.centerx:   # when sprite reach its hitbox
                self.moving = False
            elif self.rot == ROT_UP and self.rect.centery <= self.hit_rect.centery:     # when sprite reach its hitbox
                self.moving = False
            elif self.rot == ROT_DOWN and self.rect.centery >= self.hit_rect.centery:   # when sprite reach its hitbox
                self.moving = False
            
            if not self.moving:
                self.last_moved = pg.time.get_ticks()
                self.vel = vec(0, 0)
                self.rect.center = self.hit_rect.center           # adjust sprite position on hitbox
                self.pos = (self.rect.centerx, self.rect.centery)   # register sprite position to avoid shifts
        


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x: int, y: int, w: int, h: int):
        """Create a wall.

        Args:
            game (Game ): game used
            x (int): horizontal position
            y (int): vertical position
            w (int): width
            h (int): height
        """
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Item(pg.sprite.Sprite):
    def __init__(self, game, pos: pg.math.Vector2, type: str):
        """Create a floating item.

        Args:
            game (Game): game used
            pos (pg.math.Vector2): position vector
            type (str): type of item
        """
        self._layer = ITEMS_LAYER       # use the good layer
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.hit_rect = pg.Rect(0, 0, TILESIZE, TILESIZE)
        self.hit_rect.center = self.rect.center

    def update(self):
        """Do nothing.
        """
        pass
