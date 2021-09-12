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


def find_at_pos(group: pg.sprite.Group, x: int, y:int) -> pg.sprite.Sprite:
    """Find a sprite from a group at the position specified.

    Args:
        group (pg.sprite.Group): Group where searching
        x (int): horizontal position
        y (int): vertical position

    Returns:
        pg.sprite.Sprite: the sprite found, or None
    """
    for sprite in group.sprites():
        if sprite.hit_rect.centerx == x and sprite.hit_rect.centery == y:
            return sprite
    return None


class Player(pg.sprite.Sprite):
    def __init__(self, game, x: int, y: int):
        """Create a Player in the game.

        Args:
            game (Game): game used
            x (int): horizontal position of player center
            y (int): vertical position of player center
        """
        self._layer = PLAYER_LAYER  # to display on the good layer
        self.groups = game.map_sprites, game.players
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
            use_anim (optional, bool): indicate if animate movement. Defaults to False
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
            self.animation = BONK_ANIMATION
            self.animated = STEP_ANIM_LENGTH
        elif self.running:
            self.animation = RUNNING_ANIMATION
            self.animated = STEP_ANIM_LENGTH
        else:
            self.animation = WALKING_ANIMATION
            self.animated = STEP_ANIM_LENGTH
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
            use_anim (optional, bool): indicate if animate rotation. Defaults to False
        """
        self.dir = dir
        self.rot = rot
        self.last_rot = pg.time.get_ticks()
        self.animation = ROT_ANIMATION
        self.animated = STEP_ANIM_LENGTH
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
    
    def interact_with(self, sprite: pg.sprite.Sprite):
        """Do nothing.
        
        Args:
            sprite(pg.sprite.Sprite): sprite to interact with
        """
        pass
    
    def interact(self):
        """Find a sprite in front of the player and interact with it.
        """
        # find the sprite to interact with
        if self.rot == ROT_RIGHT:
            sprite = find_at_pos(self.game.map_sprites, self.hit_rect.centerx + TILESIZE, self.hit_rect.centery)
        elif self.rot == ROT_LEFT:
            sprite = find_at_pos(self.game.map_sprites, self.hit_rect.centerx - TILESIZE, self.hit_rect.centery)
        elif self.rot == ROT_UP:
            sprite = find_at_pos(self.game.map_sprites, self.hit_rect.centerx, self.hit_rect.centery - TILESIZE)
        elif self.rot == ROT_DOWN:
            sprite = find_at_pos(self.game.map_sprites, self.hit_rect.centerx, self.hit_rect.centery + TILESIZE)
        # interact with sprite found
        if sprite != None:
            sprite.interact_with(self)

    def get_keys(self):
        """Use the player inputs to control the character on the map.
        """
        if self.moving or self.animated:
            return
        # use
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_q]:
            self.dir_key_pressed(ROT_LEFT, LEFT, -TILESIZE, 0, keys[pg.K_SPACE])
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.dir_key_pressed(ROT_RIGHT, RIGHT, TILESIZE, 0, keys[pg.K_SPACE])
        elif keys[pg.K_UP] or keys[pg.K_z]:
            self.dir_key_pressed(ROT_UP, UP, 0, -TILESIZE, keys[pg.K_SPACE])
        elif keys[pg.K_DOWN] or keys[pg.K_s]:
            self.dir_key_pressed(ROT_DOWN, DOWN, 0, TILESIZE, keys[pg.K_SPACE])

    def update(self):
        """Move player.
        """
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
            self.animation = WALKING_ANIMATION
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
        self.groups = game.map_sprites, game.npcs
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
        self.dir = DOWN
        self.moving = False
        self.move_index = 0
        self.last_moved = pg.time.get_ticks()
        self.animation = None
        self.animation_length = 0
        self.animation_index = 0
        self.animated = 0
        self.started_animation = pg.time.get_ticks()
    
    def interact_with(self, player: Player):
        """Do nothing.
        
        Args:
            player(Player): player to interact with
        """
        # can't interact with moving NPC
        if self.animated or self.moving:
            return
        # rotate NPC to face the player
        if (self.hit_rect.centerx < player.hit_rect.centerx) and (self.rot != ROT_RIGHT):
            self.rotate(ROT_RIGHT, RIGHT, True)
        elif (self.hit_rect.centerx > player.hit_rect.centerx) and (self.rot != ROT_LEFT):
            self.rotate(ROT_LEFT, LEFT, True)
        elif (self.hit_rect.centery > player.hit_rect.centery) and (self.rot != ROT_UP):
            self.rotate(ROT_UP, UP, True)
        elif (self.hit_rect.centery < player.hit_rect.centery) and (self.rot != ROT_DOWN):
            self.rotate(ROT_DOWN, DOWN, True)
        # freeze game
        self.game.freezed = True
        # display dialogue
        self.game.display_messages(["test1", "test2"])
    
    def increment_animation(self):
        """Increment the animation step and update image.
        """
        self.animation_index += 1
        if self.animation_index >= self.animation_length:
            self.animation_index = 0
        self.image = self.game.NPC_images[self.type][self.dir + self.animation[self.animation_index][0]]
        self.started_animation = pg.time.get_ticks()
    
    def move(self, move_x: int, move_y: int, rot: int, dir: str) -> bool:
        """Move the NPC and start the movement animatiion.

        Args:
            move_x (int): x deplacement to move NPC
            move_y (int): y deplacement to move NPC
            rot (int): rotation in degrees
            dir (str): constant LEFT, RIGHT, UP or DOWN
        
        Returns:
            True if not colliding
        """
        self.dir = dir
        self.rot = rot
        # move hitbox
        self.hit_rect.centerx += move_x
        self.hit_rect.centery += move_y
        isColliding = collide_with_group(self, self.game.walls, self.dir)
        isColliding = isColliding or collide_with_group(self, self.game.items, self.dir)
        isColliding = isColliding or collide_with_group(self, self.game.npcs, self.dir)
        isColliding = isColliding or collide_with_group(self, self.game.players, self.dir)
        # animate as needed
        if not isColliding:
            self.vel = vec(WALKING_SPEED, 0).rotate(-self.rot)
            self.animation = WALKING_ANIMATION
            self.animated = STEP_ANIM_LENGTH
            self.animation_length = len(self.animation)
            self.increment_animation()
            self.moving = True
            return True
        else:
            self.rotate(rot, dir, use_anim=True)
            self.moving = False
            return False
    
    def rotate(self, rot: int, dir: str, use_anim=False) -> bool:
        """Rotate the NPC.

        Args:
            rot (int): rotation in degrees
            dir (str): constant LEFT, RIGHT, UP or DOWN
            use_anim (optional, bool): indicate if animate rotation. Default to False
        
        Returns:
            True
        """
        self.dir = dir
        self.rot = rot
        self.animation = ROT_ANIMATION
        self.animated = STEP_ANIM_LENGTH
        self.animation_length = len(self.animation)
        if(use_anim):
            self.increment_animation()
        return True
    
    def get_move_parameters(self, dir: str) -> tuple:
        """Returns the parameters needed for self.move().

        Args:
            dir (str): constant LEFT, RIGHT, UP or DOWN

        Returns:
            tuple:  (move_x: int, move_y: int, rot: int, dir: str)
        """
        if dir == UP:
            return (0, -TILESIZE, ROT_UP, UP)
        elif dir == DOWN:
            return (0, +TILESIZE, ROT_DOWN, DOWN)
        elif dir == LEFT:
            return (-TILESIZE, 0, ROT_LEFT, LEFT)
        else:
            return (+TILESIZE, 0, ROT_RIGHT, RIGHT)
    
    def update(self):
        """Update NPC.
        """
        # NPC move only when game not freezed
        if not self.game.freezed:
            # do deplacement loop
            if not self.moving and not self.animated and (pg.time.get_ticks() - self.last_moved > MOVEMENT_COOLDOWN):
                movement = NPC_MOVEMENT_LIST[self.move_index]
                move_tuple = self.get_move_parameters(movement[1])
                success = False
                if movement[0] == MOVE:
                    success = self.move(move_tuple[0], move_tuple[1], move_tuple[2], move_tuple[3])
                else:
                    success = self.rotate(move_tuple[2], move_tuple[3], use_anim=True)
                self.last_moved = pg.time.get_ticks()
                if success:
                    # increment move_index
                    self.move_index += 1
                    if self.move_index == len(NPC_MOVEMENT_LIST):
                        self.move_index = 0
        # update layer to display above or below the player
        if (self._layer == NPC_BELOW_LAYER) and (self.game.player.pos.y < self.pos.y):
            self.game.map_sprites.change_layer(self, NPC_ABOVE_LAYER)
        elif (self._layer == NPC_ABOVE_LAYER) and (self.game.player.pos.y > self.pos.y):
            self.game.map_sprites.change_layer(self, NPC_BELOW_LAYER)
        # manage animation steps
        if self.animated and (pg.time.get_ticks() - self.started_animation > self.animation[self.animation_index][1]):
            self.animated -= 1
            if self.animated:
                self.increment_animation()
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
        self.groups = game.map_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.hit_rect = pg.Rect(0, 0, TILESIZE, TILESIZE)
        self.hit_rect.center = self.rect.center
    
    def interact_with(self, sprite: pg.sprite.Sprite):
        """Do nothing.
        
        Args:
            sprite(pg.sprite.Sprite): sprite to interact with
        """
        pass

    def update(self):
        """Do nothing.
        """
        pass
