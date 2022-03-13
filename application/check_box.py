import pygame

from .consts import COLORS


class CheckBox:
    def __init__(self, x, y, width, height, **kwargs):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.state = kwargs.pop("state", False)
        self.off_color = kwargs.pop("off_color", COLORS["check_box_off_color"])
        self.on_color = kwargs.pop("on_color", COLORS["check_box_on_color"])
        self.border_color = kwargs.pop("border_color", COLORS["white"])
        self.border_width = kwargs.pop("border_width", 3)

    def toggle(self):
        self.state = not self.state

    def get_state(self):
        return self.state

    def draw(self, window, screen_width, screen_height):
        x, y = self.x * screen_width, self.y * screen_height
        width, height = self.width * screen_width, self.height * screen_height

        if self.state:
            color = self.on_color
        else:
            color = self.off_color

        surface = pygame.Surface((width, height))
        surface_rect = surface.get_rect(topleft=(x, y))
        surface.fill(color)

        pygame.draw.rect(
            surface, self.border_color, (0, 0, width, height), self.border_width
        )

        return window.blit(surface, surface_rect)

    def check_collision(self, mouse_pos, screen_width, screen_height):
        x, y, width, height = (
            self.x * screen_width,
            self.y * screen_height,
            self.width * screen_width,
            self.height * screen_height,
        )

        if mouse_pos[0] > x and mouse_pos[0] < x + width:
            if mouse_pos[1] > y and mouse_pos[1] < y + height:
                return True
        return False
