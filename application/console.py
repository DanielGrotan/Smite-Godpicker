import pygame

from .consts import COLORS


class Console:
    def __init__(self, x, y, width, height, **kwargs):
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.position = kwargs.pop('position', "bottomleft")
        self.background_color = kwargs.pop('background_color', COLORS["black"])
        self.text_normal_color = kwargs.pop('text_normal_color', COLORS["console_text_color_green"])
        self.text_error_color = kwargs.pop('text_error_color', COLORS["console_text_color_red"])
        self.text_warning_color = kwargs.pop('text_warning_color', COLORS["console_text_color_yellow"])
        self.border_color = kwargs.pop('border_color', COLORS["white"])
        self.border_width = kwargs.pop('border_width', 3)
        self.max_displayed_messages = kwargs.pop('max_displayed_messages', 4)
        self.font_type = kwargs.pop("font", "Microsoft Sans Serif")
        self.font_size = 30
        self.message_count = 0
        self.scroll = 0

        self.messages: list[tuple[str, str]] = []
    
    def get_font(self, width, height, text):
        font_size = self.font_size
        while True:
            font = pygame.font.SysFont(self.font_type, font_size)
            text_surf = font.render(text, True, COLORS["grey"])

            if (
                text_surf.get_width() <= width
                and text_surf.get_height() <= height
            ):
                return font
            font_size-=1
        
    
    def draw(self, window, screen_width, screen_height):
        x, y = self.x * screen_width, self.y * screen_height
        width, height = self.width * screen_width, self.height * screen_height

        surface = pygame.Surface((width, height))
        surface.fill(self.background_color)

        match self.position:
            case "bottomleft":
                self.surface_rect = surface.get_rect(bottomleft=(x, y + self.border_width))
        
                pygame.draw.rect(surface, self.border_color, (0, 0, width, height), self.border_width)
        
        if self.messages:
            if self.scroll == 0:
                messages = self.messages[-self.max_displayed_messages:]
            else:
                messages = self.messages[-self.max_displayed_messages - self.scroll:-self.scroll]
            actual_messages = [message[0] for message in messages]
            font = self.get_font(width * 0.9, height * 0.9, max(actual_messages, key=len))
            text_height = height / self.max_displayed_messages
            for i, message in enumerate(messages):
                message, message_type = message
                if message_type == "normal":
                    color = self.text_normal_color
                elif message_type == "warning":
                    color = self.text_warning_color
                elif message_type == "error":
                    color = self.text_error_color
                else:
                    continue

                text_surf = font.render(message, True, color)
                rect = pygame.Rect(width * 0.05, text_height * i, width * 0.95, text_height)
                text_rect = text_surf.get_rect(midleft=rect.midleft)
                surface.blit(text_surf, text_rect)

        return window.blit(surface, self.surface_rect)
            
    def add_message(self, message, message_type):
        self.message_count += 1
        self.messages.append((f"{self.message_count}: {message}", message_type))
    
    def clear(self):
        self.message_count = 0
        self.messages = []
    
    def do_scroll(self, mouse_pos, direction) -> bool:
        if not self.surface_rect.collidepoint(mouse_pos):
            return False
        
        prev_scroll = self.scroll

        if direction == "up":
            self.scroll = max(min(len(self.messages) - self.max_displayed_messages, self.scroll + 1), 0)
        elif direction == "down":
            self.scroll = max(0, self.scroll - 1)
        
        return self.scroll != prev_scroll
