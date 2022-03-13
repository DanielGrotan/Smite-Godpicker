import clipboard
import pygame

from .consts import ALPHABET, COLORS


class InputField:
    def __init__(self, x, y, width, height, **kwargs):
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.default_text = kwargs.pop("default_text", "This is an input field.")
        self.default_text_color = kwargs.pop("default_text_color", COLORS["grey"])

        self.background_color = kwargs.pop("background_color", COLORS["black"])
        self.text_color = kwargs.pop("text_color", COLORS["white"])
        self.border_color_passive = kwargs.pop("border_color_passive", COLORS["white"])
        self.border_color_active = kwargs.pop(
            "border_color_active", COLORS["bright_green"]
        )
        self.border_width = kwargs.pop("border_width", 3)
        self.font_size = kwargs.pop("font_size", 30)
        self.font_type = kwargs.pop("font_type", "Microsoft Sans Serif")

        self.default_value = kwargs.pop("default_value", "")

        self.text = self.default_value
        self.selected = False
        self.rect = None
        self.pasted = False

    def draw(self, window, screen_width, screen_height):

        width, height = screen_width * self.width, screen_height * self.height
        x, y = screen_width * self.x, screen_height * self.y

        surface = pygame.Surface((width, height))
        surface.fill(self.background_color)

        self.rect = pygame.Rect(x, y, width, height)

        border_color = (
            self.border_color_active if self.selected else self.border_color_passive
        )

        pygame.draw.rect(
            surface, border_color, (0, 0, width, height), self.border_width
        )

        updated_area = window.blit(surface, self.rect)
        self.draw_text(window)

        return updated_area

    def render_text(self, text, color):
        font_size = self.font_size
        while True:
            font = pygame.font.SysFont(self.font_type, font_size)
            text_surf = font.render(text, True, color)

            if (
                text_surf.get_width() <= self.rect.width * 0.9
                and text_surf.get_height() <= self.rect.height * 0.9
            ):
                return text_surf

            font_size -= 1

    def draw_text(self, window: pygame.Surface):
        if self.text:
            text_surf = self.render_text(self.text, self.text_color)
        elif self.default_text and not self.selected:
            text_surf = self.render_text(self.default_text, self.default_text_color)
        else:
            return

        text_rect = text_surf.get_rect(center=self.rect.center)
        return window.blit(text_surf, text_rect)

    def check_press(self, mouse_pos):
        prev = self.selected
        self.selected = self.rect.collidepoint(mouse_pos)
        return self.selected != prev

    def update_text(self, key) -> bool:
        if not self.selected:
            return

        prev_text = self.text

        if key == "backspace":
            self.text = self.text[:-1]
        elif key == "space":
            self.text += " "
        elif key == "return":
            self.selected = False
        elif key == "escape":
            self.text = ""
        elif key in ALPHABET:
            self.text += key

        return self.text != prev_text

    def check_paste(self, keys_pressed):
        if not self.selected:
            return

        if (
            keys_pressed[pygame.K_LCTRL] or keys_pressed[pygame.K_RCTRL]
        ) and keys_pressed[pygame.K_v]:
            if not self.pasted:
                self.text += clipboard.paste()
                self.pasted = True
        else:
            self.pasted = False

        return self.pasted

    def get_text(self):
        return self.text

    def clear(self):
        self.text = ""
