import pygame as pg
from random import uniform, choice, randint, random
from settings import *
import pytweening as tween
from itertools import chain
vec = pg.math.Vector2


def collide_hit_rect(one: pg.sprite.Sprite, two: pg.sprite.Sprite) -> bool:
    """Test if two hitboxes collide.

    Args:
        one (pg.sprite.Sprite): sprite one
        two (pg.sprite.Sprite): sprite two

    Returns:
        bool: result of test
    """
    return one.hit_rect.colliderect(two.hit_rect)


def collide_with_group(sprite: pg.sprite.Sprite, group: pg.sprite.Group, dir: str) -> bool:
    """Avoid sprite going through the elements from the group.

    Args:
        sprite (pg.sprite.Sprite): sprite to apply the function to
        group (pg.sprite.Group): group to collide with
        dir (str): direction of the movement
    
    Returns:
        bool: True when sprite collide with group
    """
    hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)  # list of sprites which collide
    if hits:
        if hits[0] == sprite:
            return False
        if dir == RIGHT:
            if hits[0].hit_rect.centerx >= sprite.hit_rect.centerx:  # obstacle to the right
                sprite.hit_rect.centerx = hits[0].hit_rect.left - sprite.hit_rect.width / 2
        if dir == LEFT:
            if hits[0].hit_rect.centerx <= sprite.hit_rect.centerx:  # obstacle to the left
                sprite.hit_rect.centerx = hits[0].hit_rect.right + sprite.hit_rect.width / 2
        if dir == DOWN:
            if hits[0].hit_rect.centery >= sprite.hit_rect.centery:  # obstacle down
                sprite.hit_rect.centery = hits[0].hit_rect.top - sprite.hit_rect.height / 2
        if dir == UP:
            if hits[0].hit_rect.centery <= sprite.hit_rect.centery:  # obstacle up
                sprite.hit_rect.centery = hits[0].hit_rect.bottom + sprite.hit_rect.height / 2
        return True
    return False


class Player(pg.sprite.Sprite):
    def __init__(self, game, x: int, y: int):
        """Create a Player in the game.

        Args:
            game (Game): game used
            x (int): horizontal position of player center
            y (int): vertical position of player center
        """
        self._layer = PLAYER_LAYER  # to display on the good layer
        self.groups = game.all_sprites, game.players
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_images['RIGHT_still']
        self.rect = self.image.get_rect()
        self.rect.center = (x, y-PLAYER_IMG_OFFSET)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = (x, y)
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = ROT_RIGHT
        self.dir = RIGHT
        self.last_rot = pg.time.get_ticks()
        self.moving = False
        self.running = False
        self.last_moved = pg.time.get_ticks()
        self.animation = None
        self.animation_length = 0
        self.animation_index = 0
        self.animated = 0
        self.started_animation = pg.time.get_ticks()
    
    def increment_animation(self):
        """Increment the animation step and update image.
        """
        self.animation_index += 1
        if self.animation_index >= self.animation_length:
            self.animation_index = 0
        self.image = self.game.player_images[self.dir + self.animation[self.animation_index][0]]
        self.started_animation = pg.time.get_ticks()
    
    def move(self, move_x: int, move_y: int, is_running: bool, use_anim=False):
        """Move the player and start the movement animatiion.

        Args:
            move_x (int): x deplacement to move player
            move_y (int): y deplacement to move player
            is_running (bool): indicate if the player needs to run
            use_anim (optional, bool): indicate if animate movement
        """
        # select speed
        if is_running:
            self.vel = vec(RUNNING_SPEED, 0).rotate(-self.rot)
            self.running = True
        else:
            self.vel = vec(WALKING_SPEED, 0).rotate(-self.rot)
            self.running = False
        # move hitbox
        self.hit_rect.centerx += move_x
        self.hit_rect.centery += move_y
        isColliding = collide_with_group(self, self.game.walls, self.dir)
        isColliding = isColliding or collide_with_group(self, self.game.items, self.dir)
        isColliding = isColliding or collide_with_group(self, self.game.npcs, self.dir)
        # choose Player animation
        if isColliding:
            self.animation = PLAYER_BONK_ANIMATION
            self.animated = PLAYER_STEP_ANIM_LENGTH
        elif self.running:
            self.animation = PLAYER_RUNNING_ANIMATION
            self.animated = PLAYER_STEP_ANIM_LENGTH
        else:
            self.animation = PLAYER_WALKING_ANIMATION
            self.animated = PLAYER_STEP_ANIM_LENGTH
        self.animation_length = len(self.animation)
        if(use_anim):
            # start animation
            self.increment_animation()
        self.moving = True
    
    def rotate(self, rot: int, dir: str, use_anim=False):
        """Rotate the player.

        Args:
            rot (int): rotation in degrees
            dir (str): constant LEFT, RIGHT, UP or DOWN
            use_anim (optional, bool): indicate if animate rotation
        """
        self.dir = dir
        self.rot = rot
        self.last_rot = pg.time.get_ticks()
        self.animation = PLAYER_ROT_ANIMATION
        self.animated = PLAYER_STEP_ANIM_LENGTH
        self.animation_length = len(self.animation)
        if(use_anim):
            self.increment_animation()
    
    def dir_key_pressed(self, rot: int, dir: str, move_x: int, move_y: int, is_running: bool):
        """Do the correct action when a direction key is pressed.

        Args:
            rot (int): rotation in degrees
            dir (str): constant LEFT, RIGHT, UP or DOWN
            move_x (int): x deplacement when move player
            move_y (int): y deplacement when move player
            is_running (bool): indicate if the player need to run when moving
        """
        if self.rot == rot:        # already in the same direction as input
            if not self.animated and (pg.time.get_ticks() - self.last_rot > TIME_ROTATE):   # allow rotation without moving for short input
                self.move(move_x, move_y, is_running, use_anim=True)
        elif not self.animated:
            self.rotate(rot, dir, use_anim=False)
            # not stoping if rotate while moving
            if pg.time.get_ticks() - self.last_moved < TIME_KEEP_MOVING:
                self.move(move_x, move_y, is_running, use_anim=False)
            # play the good animation between rotate and move
            self.increment_animation()

    def get_keys(self):
        """Use the player inputs to control the character.
        """
        if not self.moving:
            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                self.dir_key_pressed(ROT_LEFT, LEFT, -TILESIZE, 0, keys[pg.K_SPACE])
            elif keys[pg.K_RIGHT] or keys[pg.K_d]:
                self.dir_key_pressed(ROT_RIGHT, RIGHT, TILESIZE, 0, keys[pg.K_SPACE])
            elif keys[pg.K_UP] or keys[pg.K_w]:
                self.dir_key_pressed(ROT_UP, UP, 0, -TILESIZE, keys[pg.K_SPACE])
            elif keys[pg.K_DOWN] or keys[pg.K_s]:
                self.dir_key_pressed(ROT_DOWN, DOWN, 0, TILESIZE, keys[pg.K_SPACE])

    def update(self):
        """Move player.
        """
        self.get_keys()
        # manage animation steps
        if self.animated and (pg.time.get_ticks() - self.started_animation > self.animation[self.animation_index][1]):
            self.animated -= 1
            if self.animated:
                self.increment_animation()
        # move sprite
        if self.moving:
            self.pos += self.vel * self.game.dt     # compute new sprite position
            self.rect = self.image.get_rect()
            self.rect.center = (self.pos.x, self.pos.y-PLAYER_IMG_OFFSET)       # position sprite
            if self.rot == ROT_RIGHT and self.pos.x >= self.hit_rect.centerx:    # when sprite reach its hitbox
                self.moving = False
            elif self.rot == ROT_LEFT and self.pos.x <= self.hit_rect.centerx:   # when sprite reach its hitbox
                self.moving = False
            elif self.rot == ROT_UP and self.pos.y <= self.hit_rect.centery:     # when sprite reach its hitbox
                self.moving = False
            elif self.rot == ROT_DOWN and self.pos.y >= self.hit_rect.centery:   # when sprite reach its hitbox
                self.moving = False
            # when end of deplacement
            if not self.moving:
                self.last_moved = pg.time.get_ticks()
                self.vel = vec(0, 0)
                self.rect.center = (self.hit_rect.centerx, self.hit_rect.centery-PLAYER_IMG_OFFSET) # adjust sprite position on hitbox
                self.pos = vec(self.hit_rect.centerx, self.hit_rect.centery)   # register sprite position to avoid shifts
        # reset sprite if not animated
        if not self.animated and (pg.time.get_ticks() - self.last_moved > TIME_KEEP_MOVING):
            self.animation = PLAYER_WALKING_ANIMATION
            self.running = False
            self.image = self.game.player_images[self.dir + self.animation[self.animation_index][0]]
            self.rect = self.image.get_rect()
            self.rect.center = (self.pos.x, self.pos.y-PLAYER_IMG_OFFSET)


class NPC(pg.sprite.Sprite):
    def __init__(self, game, x: int, y: int, type: str):
        """Create a NPC in the game.

        Args:
            game (Game): game used
            x (int): horizontal position of NPC center
            y (int): vertical position of NPC center
            type (str): type of NPC
        """
        self.type = type
        self._layer = NPC_BELOW_LAYER
        self.groups = game.all_sprites, game.npcs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.NPC_images[self.type]['DOWN_still']
        self.rect = self.image.get_rect()
        self.rect.center = (x, y-NPC_IMG_OFFSET)
        self.hit_rect = NPC_HIT_RECT
        self.hit_rect.center = (x, y)
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = ROT_DOWN
        self.last_rot = pg.time.get_ticks()
        self.last_moved = pg.time.get_ticks()
        self.move_index = 0
        self.dir = DOWN
        self.moving = False
    
    def move(self, dir: str):
        """Move the NPC and manage its rotation.

        Args:
            dir (str): deplacement direction
        """
        if dir == LEFT:
            self.hit_rect.centerx -= TILESIZE
            self.moving = True
            if self.rot != ROT_LEFT:
                # rotate sprite
                self.last_rot = pg.time.get_ticks()
                self.rot = ROT_LEFT
                self.image = self.game.NPC_images[self.type]['LEFT_still']
                self.dir = LEFT
        elif dir == RIGHT:
            self.hit_rect.centerx += TILESIZE
            self.moving = True
            if self.rot != ROT_RIGHT:
                # rotate sprite
                self.last_rot = pg.time.get_ticks()
                self.rot = ROT_RIGHT
                self.image = self.game.NPC_images[self.type]['RIGHT_still']
                self.dir = RIGHT
        elif dir == UP:
            self.hit_rect.centery -= TILESIZE
            self.moving = True
            if self.rot != ROT_UP:
                # rotate sprite
                self.last_rot = pg.time.get_ticks()
                self.rot = ROT_UP
                self.image = self.game.NPC_images[self.type]['UP_still']
                self.dir = UP
        elif dir == DOWN:
            self.hit_rect.centery += TILESIZE
            self.moving = True
            if self.rot != ROT_DOWN:
                # rotate sprite
                self.last_rot = pg.time.get_ticks()
                self.rot = ROT_DOWN
                self.image = self.game.NPC_images[self.type]['DOWN_still']
                self.dir = DOWN
        
        if self.moving:
            self.vel = vec(WALKING_SPEED, 0).rotate(-self.rot)
            collide_with_group(self, self.game.walls, self.dir)
            collide_with_group(self, self.game.items, self.dir)
            collide_with_group(self, self.game.npcs, self.dir)
            collide_with_group(self, self.game.players, self.dir)
    
    def update(self):
        """Update NPC.
        """
        # update layer to display above or below the player
        if (self._layer == NPC_BELOW_LAYER) and (self.game.player.pos.y < self.pos.y):
            self.game.all_sprites.change_layer(self, NPC_ABOVE_LAYER)
        elif (self._layer == NPC_ABOVE_LAYER) and (self.game.player.pos.y > self.pos.y):
            self.game.all_sprites.change_layer(self, NPC_BELOW_LAYER)
        # do deplacement loop
        if not self.moving and (pg.time.get_ticks() - self.last_moved > MOVEMENT_COOLDOWN):
            self.move(NPC_MOVEMENT_LIST[self.move_index])
            if self.rect.center != (self.hit_rect.centerx, self.hit_rect.centery-NPC_IMG_OFFSET):
                # if hitbox have move, increment move_index
                self.move_index += 1
                if self.move_index == len(NPC_MOVEMENT_LIST):
                    self.move_index = 0
        # move sprite
        if self.moving:
            self.pos += self.vel * self.game.dt     # compute new sprite position
            self.rect = self.image.get_rect()
            self.rect.center = (self.pos.x, self.pos.y-NPC_IMG_OFFSET)       # position sprite
            if self.rot == ROT_RIGHT and self.pos.x >= self.hit_rect.centerx:    # when sprite reach its hitbox
                self.moving = False
            elif self.rot == ROT_LEFT and self.pos.x <= self.hit_rect.centerx:   # when sprite reach its hitbox
                self.moving = False
            elif self.rot == ROT_UP and self.pos.y <= self.hit_rect.centery:     # when sprite reach its hitbox
                self.moving = False
            elif self.rot == ROT_DOWN and self.pos.y >= self.hit_rect.centery:   # when sprite reach its hitbox
                self.moving = False
            
            if not self.moving:
                self.last_moved = pg.time.get_ticks()
                self.vel = vec(0, 0)
                self.rect.center = (self.hit_rect.centerx, self.hit_rect.centery-NPC_IMG_OFFSET) # adjust sprite position on hitbox
                self.pos = vec(self.hit_rect.centerx, self.hit_rect.centery)   # register sprite position to avoid shifts


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
