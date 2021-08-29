import pygame as pg
import pytmx
from settings import *


class TiledMap:
    def __init__(self, filename: str):
        """Create a tiled map from a tmx file.

        Args:
            filename (str): file path
        """
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface: pg.Surface):
        """Draw the map on a surface.

        Args:
            surface (pg.Surface): surface
        """
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):     # draw tiles of tileLayers
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self, alpha=255):
        """Create the map image.
        
        Args:
            alpha (int, optional): map baground alpha. Defaults to 255 (opaque).

        Returns:
            pg.Surface: map image
        """
        temp_surface = pg.Surface((self.width, self.height)).convert_alpha()
        temp_surface.fill((0, 0, 0, alpha))
        self.render(temp_surface)
        return temp_surface


class Camera:
    def __init__(self, width: int, height: int):
        """Create a camera to know where the screen is on the map.

        Args:
            width (int): camera width
            height (int): camera height
        """
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity: pg.sprite.Sprite) -> pg.Rect:
        """Return the rect where the sprite needs to be drawn.

        Args:
            entity (pg.sprite.Sprite): sprite to know position on screen

        Returns:
            pg.Rect: rect where the sprite needs to be drawn
        """
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect: pg.Rect) -> pg.Rect:
        """Return the rect where the rect needs to be drawn.

        Args:
            rect (pg.Rect): rect to know position on screen

        Returns:
            pg.Rect: rect where the rect needs to be drawn
        """
        return rect.move(self.camera.topleft)

    def update(self, target: pg.sprite.Sprite):
        """Move the camera to follow the target.

        Args:
            target (pg.sprite.Sprite): sprite to follow
        """
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)
