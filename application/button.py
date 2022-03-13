import pygame

from .consts import COLORS


class Button:
    def __init__(self, x: int, y: int, width: int, height: int, **kwargs):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.color = kwargs.pop("color", COLORS["black"])
        self.text = kwargs.pop("text", "")
        self.outlined = kwargs.pop("outlined", True)
        self.outlinecolor = kwargs.pop("outlinecolor", COLORS["white"])
        self.sprite = kwargs.pop("sprite", None)
        self.sprite_size = kwargs.pop("sprite_size", (0, 0))
        self.font_type = kwargs.pop("font", "Microsoft Sans Serif")
        self.font_size = kwargs.pop("font_size", 30)
        self.original_sprite = self.sprite
        self.button_size = 0

    def draw(self, window, screen_size, screen_height=None):
        if screen_height is not None:
            screen_size = [screen_size, screen_height]
        area = None
        if self.sprite is not None:
            area2 = window.blit(
                self.sprite,
                (screen_size[0] * self.x, screen_size[1] * self.y),
            )
        else:
            border_constant = 6
            if self.outlined:
                area = pygame.draw.rect(
                    window,
                    self.outlinecolor,
                    (
                        screen_size[0] * self.x,
                        screen_size[1] * self.y,
                        screen_size[0] * self.width,
                        screen_size[1] * self.height,
                    ),
                )
            area2 = pygame.draw.rect(
                window,
                self.color,
                (
                    screen_size[0] * self.x + border_constant / 2,
                    screen_size[1] * self.y + border_constant / 2,
                    screen_size[0] * self.width - border_constant,
                    screen_size[1] * self.height - border_constant,
                ),
            )
            font_size = self.font_size
            while True:
                font = pygame.font.SysFont(self.font_type, font_size)
                text_surf = font.render(self.text, True, COLORS["grey"])

                if (
                    text_surf.get_width() <= screen_size[0] * self.width * 0.9
                    and text_surf.get_height() <= screen_size[1] * self.height * 0.9
                ):
                    rect = pygame.Rect(
                        screen_size[0] * self.x,
                        screen_size[1] * self.y,
                        screen_size[0] * self.width,
                        screen_size[1] * self.height,
                    )
                    text_rect = text_surf.get_rect(center=rect.center)
                    window.blit(text_surf, text_rect)
                    break

                font_size -= 1

        return area2 if self.sprite is not None else area

    def check_collision(
        self, mouse_coords: tuple[int, int], screen_size: tuple[int, int]
    ) -> bool:

        x, y = self.x * screen_size[0], self.y * screen_size[1]
        width, height = self.width * screen_size[0], self.height * screen_size[1]

        if self.sprite is not None:
            width, height = self.button_size, self.button_size
        if mouse_coords[0] > x and mouse_coords[0] < x + width:
            if mouse_coords[1] > y and mouse_coords[1] < y + height:
                return True
        return False

    def resize(self, screen_size: tuple[int, int]):
        if self.sprite is not None:
            self.button_size = max(
                screen_size[0] * self.sprite_size[0],
                screen_size[1] * self.sprite_size[1],
            )
            self.sprite = pygame.transform.scale(
                self.original_sprite, (self.button_size, self.button_size)
            )
