import pygame

from .consts import COLORS


class TextBox:
    def __init__(self, x, y, width, height, text, **kwargs):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.text = text
        self.font_size = kwargs.pop("font_size", 30)
        self.font_type = kwargs.pop("font_type", "Microsoft Sans Serif")
        self.text_color = kwargs.pop("text_color", COLORS["white"])

    def render_text(self, width, height):
        font_size = self.font_size
        while True:
            font = pygame.font.SysFont(self.font_type, font_size)
            text_surf = font.render(self.text, True, self.text_color)

            if text_surf.get_width() < width and text_surf.get_height() < height:
                return text_surf

            font_size -= 1

    def draw(self, window, screen_width, screen_height):
        x, y = self.x * screen_width, self.y * screen_height
        width, height = self.width * screen_width, self.height * screen_height

        surface = pygame.Surface((width, height))
        surface_rect = surface.get_rect(topleft=(x, y))

        text_surface = self.render_text(width * 0.9, height * 0.9)
        text_rect = text_surface.get_rect(center=surface_rect.center)

        return window.blit(text_surface, text_rect)
