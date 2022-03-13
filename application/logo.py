import pygame

from .consts import COLORS


class Logo:
    def __init__(self, x, y, height, logo_path: str, text: str, **kwargs):
        self.x, self.y = x, y
        self.height = height
        self.image = pygame.image.load(logo_path)
        self.text = text
        self.font_type = kwargs.pop("font_type", "Microsoft Sans Serif")
        self.font_size = kwargs.pop("font_size", 100)
        self.text_color = kwargs.pop("text_color", COLORS["gold"])

    def render_text(self, width, height):
        font_size = self.font_size
        while True:
            font = pygame.font.SysFont(self.font_type, font_size)
            text_surf = font.render(self.text, True, self.text_color)

            if (
                text_surf.get_width() <= width * 0.9
                and text_surf.get_height() <= height * 0.9
            ):
                return text_surf

            font_size -= 1

    def draw(self, window, screen_width, screen_height):
        x, y, = (
            self.x * screen_width,
            self.y * screen_height,
        )
        height = screen_height * self.height

        scaled_image = pygame.transform.scale(self.image, (height, height))
        area = window.blit(scaled_image, (x, y))

        rect = pygame.Rect(
            x + (height * 1.1),
            y,
            min(height * 4, screen_width * 2 / 5 - height),
            height,
        )
        text_surf = self.render_text(
            min(height * 4, screen_width * 2 / 5 - height), height
        )
        window.blit(text_surf, text_surf.get_rect(midbottom=rect.midbottom))

        return area, rect
