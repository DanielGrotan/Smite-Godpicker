import json
import sys
import threading

import pygame

from .button import Button
from .check_box import CheckBox
from .console import Console
from .consts import COLORS
from .image_display import ImageDisplay
from .input_field import InputField
from .loading_bar import LoadingBar
from .logo import Logo
from .match_status import MatchStatus
from .settings import Settings
from .text_box import TextBox


class App:
    def __init__(
        self,
        window_size: tuple[int, int],
        api_scraper_bot,
        god_picker,
        title: str = "Smite God Picker™",
    ):
        pygame.init()

        self.window_size = window_size
        self.window = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        self.icon = pygame.image.load(
            "application/assets/smite_icon.png"
        ).convert_alpha()
        pygame.display.set_caption(title)
        pygame.display.set_icon(self.icon)

        self.layout_image = pygame.image.load(
            "application/assets/window_layout.png"
        ).convert()

        with open("application/settings.json") as settings:
            self.settings = json.load(settings)

        with open("files/all_gods.txt") as f:
            self.all_gods = set(god.strip() for god in f)

        self.FPS = 60

        self.name_input_field = InputField(
            1 / 75, 1 / 3.5, 5 / 75, 1 / 12, default_text="Your Name:", font_size=25
        )

        self.url_input_field = InputField(
            6.5 / 75, 1 / 3.5, 13 / 75, 1 / 12, default_text="Smitesource url:"
        )

        self.scrape_button = Button(20 / 75, 1 / 3.5, 4 / 75, 1 / 12, text="Scrape!")

        self.logo = Logo(
            1 / 75,
            1 / 75,
            1 / 5,
            "application/assets/smite_icon.png",
            "Smite God Picker™",
        )

        self.loading_bar = LoadingBar(1 / 75, 1 / 3.5 + (1 / 12 * 1.2), 23 / 75, 1 / 12)

        self.console = Console(1 / 75, 1, 23 / 75, 1 / 2, max_displayed_messages=6)

        self.get_gods_button = Button(
            16 / 35, 1 / 15, 23 / 75, 3 / 15, text="Get Gods", font_size=60
        )

        self.gods_picked_field = InputField(
            16 / 35, 7 / 15, 23 / 75, 3 / 15, default_text="Gods Picked:"
        )
        self.gods_banned_field = InputField(
            16 / 35, 11 / 15, 23 / 75, 3 / 15, default_text="Gods Banned:"
        )

        self.image_display = ImageDisplay(14 / 35, 0.5, 14.5 / 35, 0.615)

        self.match_status = MatchStatus(
            14 / 35,
            1,
            14.5 / 35,
            0.615,
            [self.gods_picked_field.draw, self.gods_banned_field.draw],
            [self.image_display.draw],
        )

        self.quit_button = Button(
            1 - 3.5 / 25, 11 / 15, 3 / 25, 3 / 15, text="Quit", font_size=60
        )

        self.settings_text_box = TextBox(
            11 / 15, 0, 3 / 15, 1 / 8, text="Settings", font_size=100
        )

        self.scrape_text_box = TextBox(
            10.5 / 15,
            1 / 6,
            2 / 15,
            1 / 10,
            text="Scrape After Recommendation",
            font_size=60,
        )
        self.scrape_check_box = CheckBox(
            5 / 6,
            1 / 6,
            1 / 15,
            1 / 10,
            state=self.settings["scrapeAfterRecommendation"],
        )

        self.disable_scrape_text_box = TextBox(
            10.5 / 15, 2 / 6, 2 / 15, 1 / 10, text="Disable Scraping", font_size=60
        )
        self.disable_scrape_check_box = CheckBox(
            5 / 6, 2 / 6, 1 / 15, 1 / 10, state=self.settings["disableScraping"]
        )

        self.amount_of_gods_text_box = TextBox(
            10.5 / 15, 3 / 6, 2 / 15, 1 / 10, text="Amount of Gods Returned"
        )

        self.amount_of_gods_field = InputField(
            5 / 6, 3 / 6, 1 / 15, 1 / 10, default_value=self.settings["amountGods"]
        )

        self.gods_no_play_field = InputField(
            10.5 / 15,
            4 / 6,
            3 / 15,
            1 / 10,
            default_value=", ".join(god.lower() for god in self.settings["godsNoPlay"]),
            default_text="Gods I Don't Want To Play As:",
        )

        self.save_settings_button = Button(
            10.5 / 15, 5 / 6, 3 / 15, 1 / 10, text="Save Settings"
        )

        self.settings_obj = Settings(
            1,
            0,
            1 / 3,
            1,
            self.settings_text_box.draw,
            self.scrape_text_box.draw,
            self.scrape_check_box.draw,
            self.disable_scrape_text_box.draw,
            self.disable_scrape_check_box.draw,
            self.amount_of_gods_text_box.draw,
            self.amount_of_gods_field.draw,
            self.gods_no_play_field.draw,
            self.save_settings_button.draw,
        )

        settings_icon = pygame.image.load(
            "application/assets/settings_icon.png"
        ).convert_alpha()
        self.settings_button = Button(
            9.2 / 10,
            0,
            0.8 / 10,
            0.8 / 10,
            sprite=settings_icon,
            sprite_size=(0.8 / 10, 0.8 / 10),
        )
        self.settings_button.resize(self.window_size)

        self.api_scraper_bot = api_scraper_bot
        self.data = {}
        self.god_picker = god_picker
        self.scrape = None

    def save_settings(self):
        self.settings["scrapeAfterRecommendation"] = self.scrape_check_box.get_state()
        self.settings["disableScraping"] = self.disable_scrape_check_box.get_state()

        if not self.amount_of_gods_field.get_text().isdigit():
            self.console.add_message(
                "Amount of gods to return must be a number", "error"
            )
            area = self.console.draw(self.window, *self.window_size)
            self.draw(area)
        else:
            self.settings["amountGods"] = self.amount_of_gods_field.get_text()

        gods = []
        for god in self.gods_no_play_field.get_text().split(", "):
            if not god:
                continue
            god = god.title() if god != "chang'e" else "Chang'e"
            if god not in self.all_gods:
                self.console.add_message(f"No data found for god {god}", "warning")
                area = self.console.draw(self.window, *self.window_size)
                self.draw(area)
                continue

            gods.append(god)

        self.settings["godsNoPlay"] = gods

        with open("application/settings.json", "w") as settings:
            json.dump(self.settings, settings)

        self.console.add_message("Saved settings", "normal")
        area = self.console.draw(self.window, *self.window_size)
        self.draw(area)

    def quit(self) -> None:
        pygame.quit()
        sys.exit()

    def draw(self, *update_area):
        if not update_area:
            pygame.display.update()
        else:
            pygame.display.update(update_area)

    def redraw(self):
        self.window.fill(COLORS["black"])

        self.name_input_field.draw(self.window, *self.window_size)
        self.url_input_field.draw(self.window, *self.window_size)
        self.scrape_button.draw(self.window, self.window_size)
        self.logo.draw(self.window, *self.window_size)
        self.loading_bar.draw(self.window, *self.window_size)
        self.console.draw(self.window, *self.window_size)
        self.get_gods_button.draw(self.window, self.window_size)
        self.match_status.draw(self.window, *self.window_size)
        self.quit_button.draw(self.window, self.window_size)

        pygame.draw.line(
            self.window,
            COLORS["white"],
            (int(self.window_size[0] * 5 / 6), 0),
            (int(self.window_size[0] * 5 / 6), self.window_size[1]),
            3,
        )

        self.settings_obj.draw(self.window, *self.window_size)
        self.settings_button.draw(self.window, self.window_size)
        self.draw()

    def start_scrape_thread(self):
        name = self.name_input_field.get_text()
        url = self.url_input_field.get_text()

        if not (name and url):
            return
        elif self.scrape is not None:
            if self.scrape.is_alive():
                self.console.add_message("Already scraping!", "warning")
                area = self.console.draw(self.window, *self.window_size)
                self.draw(area)
                return

        filepath = f"files/gods_data_{name}.pkl"
        self.scrape = threading.Thread(
            target=self.api_scraper_bot.get_player_data,
            daemon=True,
            args=[url, filepath, self.data, not self.settings["disableScraping"]],
        )

        self.data["gods_completed"] = 0
        self.loading_bar.reset()
        area = self.loading_bar.draw(self.window, *self.window_size)
        self.draw(area)

        self.console.clear()

        self.console.add_message("Starting scrape", "normal")
        area = self.console.draw(self.window, *self.window_size)
        self.draw(area)
        self.scrape.start()

    def run(self):
        clock = pygame.time.Clock()

        running = True
        self.redraw()
        while running:
            clock.tick(self.FPS)

            if "god_count" in self.data:
                self.loading_bar.set_max_value(self.data["god_count"])

            if "gods_completed" in self.data:
                if self.loading_bar.update_progress(self.data["gods_completed"]):
                    area = self.loading_bar.draw(self.window, *self.window_size)
                    self.draw(area)

            if "messages" in self.data:
                if self.data["messages"]:
                    self.console.add_message(*self.data["messages"][0])
                    del self.data["messages"][0]
                    area = self.console.draw(self.window, *self.window_size)
                    self.draw(area)

            keys_pressed = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if event.button == 1 and not self.settings_obj.enabled:
                        if self.name_input_field.check_press(mouse_pos):
                            area = self.name_input_field.draw(
                                self.window, *self.window_size
                            )
                            self.draw(area)
                        if self.url_input_field.check_press(mouse_pos):
                            area = self.url_input_field.draw(
                                self.window, *self.window_size
                            )
                            self.draw(area)
                        if self.gods_picked_field.check_press(mouse_pos):
                            area = self.gods_picked_field.draw(
                                self.window, *self.window_size
                            )
                            self.draw(area)
                        if self.gods_banned_field.check_press(mouse_pos):
                            area = self.gods_banned_field.draw(
                                self.window, *self.window_size
                            )
                            self.draw(area)
                        if self.scrape_button.check_collision(
                            mouse_pos, self.window_size
                        ):
                            self.start_scrape_thread()

                        if self.get_gods_button.check_collision(
                            mouse_pos, self.window_size
                        ):
                            if "data" in self.data:
                                gods_picked = set(
                                    god.title()
                                    for god in self.gods_picked_field.get_text().split(
                                        ", "
                                    )
                                )
                                gods_banned = set(
                                    god.title()
                                    for god in self.gods_banned_field.get_text().split(
                                        ", "
                                    )
                                )

                                gods_banned = gods_banned | set(
                                    self.settings["godsNoPlay"]
                                )

                                if self.match_status.enabled:
                                    best_gods = self.god_picker.get_best_gods(
                                        self.data["data"],
                                        gods_picked,
                                        gods_banned,
                                        self.data["messages"],
                                        amount=int(self.settings["amountGods"]),
                                    )

                                    god_data = [
                                        self.data["data"][god] for god in best_gods
                                    ]

                                    best_gods = [
                                        "-".join(god.lower().split(" "))
                                        for god in best_gods
                                    ]

                                    self.image_display.set_images(best_gods, god_data)

                                    self.match_status.disable()
                                    self.get_gods_button.text = "Back"

                                    if self.settings["scrapeAfterRecommendation"]:
                                        self.start_scrape_thread()

                                else:
                                    self.match_status.enable()
                                    self.get_gods_button.text = "Get Gods"
                                    self.gods_picked_field.clear()
                                    self.gods_banned_field.clear()

                                area = self.match_status.draw(
                                    self.window, *self.window_size
                                )
                                self.draw(area)

                                area = self.get_gods_button.draw(
                                    self.window, self.window_size
                                )
                                self.draw(area)
                            else:
                                self.console.add_message("No data loaded", "error")
                                area = self.console.draw(self.window, *self.window_size)
                                self.draw(area)

                        if self.quit_button.check_collision(
                            mouse_pos, self.window_size
                        ):
                            self.quit()

                        if self.settings_button.check_collision(
                            mouse_pos, self.window_size
                        ):
                            self.settings_obj.toggle()
                            area = self.settings_obj.draw(
                                self.window, *self.window_size
                            )
                            self.settings_button.draw(self.window, self.window_size)

                            self.draw(area)

                    elif event.button == 1 and self.settings_obj.enabled:

                        if self.settings_button.check_collision(
                            mouse_pos, self.window_size
                        ):
                            toggled = self.settings_obj.toggle()
                            area = self.settings_obj.draw(
                                self.window, *self.window_size
                            )
                            self.settings_button.draw(self.window, self.window_size)

                            self.redraw()
                        if self.scrape_check_box.check_collision(
                            mouse_pos, *self.window_size
                        ):
                            self.scrape_check_box.toggle()
                            area = self.scrape_check_box.draw(
                                self.window, *self.window_size
                            )
                            self.draw(area)

                        if self.disable_scrape_check_box.check_collision(
                            mouse_pos, *self.window_size
                        ):
                            self.disable_scrape_check_box.toggle()
                            area = self.disable_scrape_check_box.draw(
                                self.window, *self.window_size
                            )
                            self.draw(area)

                        if (
                            self.amount_of_gods_field.check_press(mouse_pos)
                            and self.settings_obj.enabled
                        ):
                            area = self.amount_of_gods_field.draw(
                                self.window, *self.window_size
                            )
                            self.draw(area)

                        if (
                            self.gods_no_play_field.check_press(mouse_pos)
                            and self.settings_obj.enabled
                        ):
                            area = self.gods_no_play_field.draw(
                                self.window, *self.window_size
                            )
                            self.draw(area)

                        if self.save_settings_button.check_collision(
                            mouse_pos, self.window_size
                        ):
                            self.save_settings()

                    elif event.button == 4:
                        self.console.do_scroll(mouse_pos, "up")
                    elif event.button == 5:
                        self.console.do_scroll(mouse_pos, "down")
                    else:
                        continue

                    area = self.console.draw(self.window, *self.window_size)
                    self.draw(area)

                elif event.type == pygame.KEYDOWN and not (
                    keys_pressed[pygame.K_LCTRL] or keys_pressed[pygame.K_RCTRL]
                ):
                    key = pygame.key.name(event.key)
                    if self.name_input_field.update_text(key):
                        update_area = self.name_input_field.draw(
                            self.window, *self.window_size
                        )
                        self.draw(update_area)
                    elif self.url_input_field.update_text(key):
                        update_area = self.url_input_field.draw(
                            self.window, *self.window_size
                        )
                        self.draw(update_area)
                    elif self.gods_picked_field.update_text(key):
                        update_area = self.gods_picked_field.draw(
                            self.window, *self.window_size
                        )
                        self.draw(update_area)
                    elif self.gods_banned_field.update_text(key):
                        update_area = self.gods_banned_field.draw(
                            self.window, *self.window_size
                        )
                        self.draw(update_area)
                    elif self.amount_of_gods_field.update_text(key):
                        update_area = self.amount_of_gods_field.draw(
                            self.window, *self.window_size
                        )
                        self.draw(update_area)
                    elif self.gods_no_play_field.update_text(key):
                        update_area = self.gods_no_play_field.draw(
                            self.window, *self.window_size
                        )
                        self.draw(update_area)
                    elif key == "escape":
                        toggled = self.settings_obj.toggle()
                        area = self.settings_obj.draw(self.window, *self.window_size)
                        self.settings_button.draw(self.window, self.window_size)

                        if toggled:
                            self.draw(area)
                        else:
                            self.redraw()
                            self.draw()

                elif event.type == pygame.VIDEORESIZE:
                    self.window_size = (event.w, event.h)
                    self.window = pygame.display.set_mode(
                        self.window_size, pygame.RESIZABLE
                    )
                    self.settings_button.resize(self.window_size)
                    self.redraw()

            if self.name_input_field.check_paste(keys_pressed):
                area = self.name_input_field.draw(self.window, *self.window_size)
                self.draw(area)
            if self.url_input_field.check_paste(keys_pressed):
                area = self.url_input_field.draw(self.window, *self.window_size)
                self.draw(area)
