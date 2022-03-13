import pygame

from .consts import COLORS


class ImageDisplay:
    def __init__(self, x, y, width, height, **kwargs):
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.font_size = kwargs.pop("font_size", 30)
        self.font_type = kwargs.pop("font_type", "Microsoft Sans Serif")
        self.images = []
        self.god_data = []

    def set_images(self, god_names: list[str], god_data) -> None:
        self.images = []
        self.god_data = god_data

        for god in god_names:
            if god == "chang'e":
                god = "change"
            image = pygame.image.load(f"application/assets/{god}.jpg").convert_alpha()
            self.images.append(image)

    def get_font(self, width, height, text):
        font_size = self.font_size
        while True:
            font = pygame.font.SysFont(self.font_type, font_size)
            text_surf = font.render(text, True, COLORS["grey"])

            if text_surf.get_width() <= width and text_surf.get_height() <= height:
                return font
            font_size -= 1

    def draw(self, window, screen_width, screen_height):
        x, y = self.x * screen_width, self.y * screen_height
        width, height = self.width * screen_width, self.height * screen_height

        num_images = len(self.images)
        image_size = min(width / num_images * 0.9, height * 0.9)
        spacing = min(width / num_images * 0.1, height * 0.1)

        font = self.get_font(
            height / 2, height / 3, "1. Morgan Le Fay | Win Rate: 99.99%"
        )
        for i, tup in enumerate(zip(self.images, self.god_data)):
            image, data = tup
            image = pygame.transform.scale(image, (image_size, image_size))
            rect = image.get_rect(
                topleft=(x + spacing / 2 + (spacing + image_size) * i, y)
            )
            window.blit(image, rect)

            text = font.render(
                f"{i + 1}. {data.god_name} | Win Rate: {data.win_rate * 100:.2f}%",
                True,
                COLORS["white"],
            )
            text_rect = text.get_rect(
                midtop=(rect.centerx, rect.bottom + image_size * 0.2)
            )
            window.blit(text, text_rect)
