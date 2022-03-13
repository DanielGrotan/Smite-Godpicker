import pygame

from .consts import COLORS


class MatchStatus:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        enabled_draw_callback,
        disabled_draw_callback,
        **kwargs
    ):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.enabled_draw_callback = enabled_draw_callback
        self.disabled_draw_callback = disabled_draw_callback

        self.background_color = kwargs.get("background_color", COLORS["black"])
        self.border_color = kwargs.get("border_color", COLORS["white"])
        self.border_width = kwargs.get("border_width", 3)

        self.enabled = True

    def draw(self, window, screen_width, screen_height):
        x, y = self.x * screen_width, self.y * screen_height
        width, height = self.width * screen_width, self.height * screen_height

        surface = pygame.Surface((width, height))
        surface_rect = surface.get_rect(bottomleft=(x, y + self.border_width))

        surface.fill(self.background_color)

        pygame.draw.rect(
            surface, self.border_color, (0, 0, width, height), self.border_width
        )

        window.blit(surface, surface_rect)

        if self.enabled:
            callback = self.enabled_draw_callback
        else:
            callback = self.disabled_draw_callback

        for func in callback:
            func(window, screen_width, screen_height)

        return surface_rect

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def toggle(self):
        self.enabled = not self.enabled
