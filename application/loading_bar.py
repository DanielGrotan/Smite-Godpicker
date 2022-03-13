import pygame

from .consts import COLORS


class LoadingBar:
    def __init__(self, x, y, width, height, default_value=0, **kwargs):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.max_value = None
        self.default_value = default_value
        self.progress = default_value

        self.background_color = kwargs.pop("background_color", COLORS["black"])
        self.border_color = kwargs.pop("border_color", COLORS["white"])
        self.fill_color = kwargs.pop("fill_color", COLORS["white"])
        self.border_width = kwargs.pop("border_width", 3)

    def draw(self, window, screen_width, screen_height):
        x, y = self.x * screen_width, self.y * screen_height
        width, height = self.width * screen_width, self.height * screen_height

        surface = pygame.Surface((width, height))
        surface_rect = surface.get_rect(topleft=(x, y))

        surface.fill(self.background_color)
        pygame.draw.rect(
            surface, self.border_color, (0, 0, width, height), self.border_width
        )

        if self.max_value is None:
            progress_percent = 0
        else:
            progress_percent = self.progress / self.max_value

        pygame.draw.rect(
            surface, self.fill_color, (0, 0, width * progress_percent, height)
        )

        return window.blit(surface, surface_rect)

    def set_max_value(self, value):
        if self.max_value is not None:
            return

        self.max_value = value

    def update_progress(self, progress) -> bool:
        prev_progress = self.progress

        self.progress = progress

        return self.progress != prev_progress

    def reset(self) -> bool:
        prev_progress = self.progress

        self.progress = self.default_value

        return self.progress != prev_progress
