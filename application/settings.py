import pygame

from .consts import COLORS


class Settings:
    def __init__(self, x, y, width, height, *draw_callback, **kwargs):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.draw_callback = draw_callback

        self.location = kwargs.pop('location', "topright")
        self.background_color = kwargs.pop('background_color', COLORS["black"])
        self.border_color = kwargs.pop('border_color', COLORS["white"])
        self.text_color = kwargs.pop('text_color', COLORS["white"])
        self.border_width = kwargs.pop('border_width', 3)
        self.font_type = kwargs.pop('font_type', "Microsoft Sans Serif")
        self.font_size = kwargs.pop('font_size', 30)
    
        self.enabled = False
    
    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled
    
    def draw(self, window, screen_width, screen_height):
        if not self.enabled:
            return

        x, y = self.x * screen_width, self.y * screen_height
        width, height = self.width * screen_width, self.height * screen_height

        surface = pygame.Surface((width, height))
        surface.fill(self.background_color)
        
        match self.location:
            case "topright":
                surface_rect = surface.get_rect(topright=(x, y))
        
        pygame.draw.rect(surface, self.border_color, (0, 0, width, height), self.border_width)

        area = window.blit(surface, surface_rect)

        for func in self.draw_callback:
            func(window, screen_width, screen_height)

        return area
