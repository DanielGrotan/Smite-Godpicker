from __future__ import annotations

import pickle
from collections import defaultdict
from dataclasses import dataclass, field
from subprocess import CREATE_NO_WINDOW

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@dataclass
class GodData:
    god_name: str
    matchups: dict[str, list[int, int]] = field(init=False)
    total_wins: int = field(init=False, default=0)
    total_losses: int = field(init=False, default=0)

    def __post_init__(self):
        self.matchups = defaultdict(self.default_value)

    def win_against(self, gods: list[str]) -> None:
        self.total_wins += 1
        for god in gods:
            self.matchups[god][0] += 1

    def lose_against(self, gods: list[str]) -> None:
        self.total_losses += 1
        for god in gods:
            self.matchups[god][1] += 1

    def default_value(self) -> tuple[int, int]:
        return [0, 0]

    @property
    def win_rate(self) -> float:
        if self.total_wins + self.total_losses == 0:
            return 0

        return self.total_wins / (self.total_wins + self.total_losses)

    @property
    def value(self) -> float:
        x = min(self.total_wins + self.total_losses, 100)
        if x == 0:
            return 0

        return 10 / 7 * x ** 0.5 + self.win_rate * 10
        # return self.win_rate * min(self.total_wins, 100)

    def __lt__(self, other) -> bool:
        return self.value < other.value

    def __gt__(self, other) -> bool:
        return self.value > other.value


class APIScraperBot:
    def __init__(
        self,
        path_to_driver: str,
        show_window: bool = True,
        screen_size: tuple[int, int] = (800, 600),
    ):
        self.options = Options()
        self.path_to_driver = path_to_driver
        if not show_window:
            self.options.add_argument("--headless")
        self.options.add_argument(f"--window-size={screen_size[0]},{screen_size[1]}")
        self.options.add_argument("--log-level=3")
        self.driver = None

        self.PAGE_LOAD_WAIT_TIME = 60
        self.NEXT_LOAD_WAIT_TIME = 10
        self.PREV_LOAD_WAIT_TIME = 1
        self.IMG_AVATAR_XPATH = '//*[@id="app"]/div/main/div/div[2]/section/div[1]/img'
        self.RECENT_GAMES_XPATH = (
            '//*[@id="app"]/div[1]/main/div/div[2]/div/div[4]/div[2]/section'
        )
        self.MATCH_ID_CLASS = "match-id"
        self.NEXT_PAGE_CLASS = "next-btn"
        self.PREV_PAGE_CLASS = "prev-btn"

    def create_driver(self):
        chrome_service = ChromeService(self.path_to_driver)
        chrome_service.creationflags = CREATE_NO_WINDOW
        return Chrome(
            service=chrome_service,
            chrome_options=self.options,
        )

    def load_previous_data(self, filepath: str) -> tuple[dict[str, GodData], set[str]]:
        try:
            with open(filepath, "rb") as data_file:
                self.output["messages"].append(("Loaded previous data", "normal"))
                data, prev_seen = pickle.load(data_file)
                return data, prev_seen
        except FileNotFoundError:
            self.output["messages"].append(("Creating default data", "normal"))
            data = {}
            with open("files/all_gods.txt") as f:
                for god in f:
                    god = god.strip()
                    data[god] = GodData(god)

            prev_seen = set()
            self.save_data(data, prev_seen, filepath)
            return data, prev_seen

    def save_data(
        self, data: dict[str, GodData], seen: set[str], filepath: str
    ) -> None:
        with open(filepath, "wb") as data_file:
            pickle.dump([data, seen], data_file)

    def find_last_page(self) -> int:
        self.output["messages"].append(
            ("Finding out how many pages of data to process", "normal")
        )
        self.output["messages"].append(
            ("Finding out how many matches to process", "normal")
        )
        page = 0
        gods = 0
        while True:
            recent_matches_container = WebDriverWait(
                self.driver, self.PAGE_LOAD_WAIT_TIME
            ).until(EC.presence_of_element_located((By.XPATH, self.RECENT_GAMES_XPATH)))
            containers = WebDriverWait(
                recent_matches_container, self.PAGE_LOAD_WAIT_TIME
            ).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "ind-match-container")
                )
            )

            gods += len(containers)

            try:
                WebDriverWait(self.driver, self.NEXT_LOAD_WAIT_TIME).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, self.NEXT_PAGE_CLASS)
                    )
                )
            except TimeoutException:
                self.output["god_count"] = gods
                self.output["messages"].append(
                    (f"Found {page} pages of data with {gods} matches", "normal")
                )
                return page

            next_button = self.driver.find_element(By.CLASS_NAME, self.NEXT_PAGE_CLASS)
            actions = ActionChains(self.driver)
            actions.move_to_element(next_button).perform()
            next_button = self.driver.find_element(By.CLASS_NAME, self.NEXT_PAGE_CLASS)
            next_button.click()
            page += 1

    def move_page(self, page: int) -> bool:
        WebDriverWait(self.driver, self.PAGE_LOAD_WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, self.RECENT_GAMES_XPATH))
        )

        while True:
            try:
                WebDriverWait(self.driver, self.PREV_LOAD_WAIT_TIME).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, self.PREV_PAGE_CLASS)
                    )
                )
                prev_button = self.driver.find_element(
                    By.CLASS_NAME, self.PREV_PAGE_CLASS
                )
                prev_button.click()
                WebDriverWait(self.driver, self.PAGE_LOAD_WAIT_TIME).until(
                    EC.presence_of_element_located((By.XPATH, self.RECENT_GAMES_XPATH))
                )
            except TimeoutException:
                break

        for _ in range(page):
            try:
                WebDriverWait(self.driver, self.NEXT_LOAD_WAIT_TIME).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, self.NEXT_PAGE_CLASS)
                    )
                )
            except TimeoutException:
                return False

            next_button = self.driver.find_element(By.CLASS_NAME, self.NEXT_PAGE_CLASS)
            actions = ActionChains(self.driver)
            actions.move_to_element(next_button).perform()
            next_button = self.driver.find_element(By.CLASS_NAME, self.NEXT_PAGE_CLASS)
            next_button.click()
            # time.sleep(0.1)

            WebDriverWait(self.driver, self.PAGE_LOAD_WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, self.RECENT_GAMES_XPATH))
            )

        return True

    def get_matches(self, prev_seen: set[str]) -> set[str]:
        last_page = self.find_last_page()
        new_page = True
        seen = set()

        current_page = 0
        self.output["gods_completed"] = 0

        while new_page:
            index = 0
            while True:
                new_page = self.move_page(current_page)

                recent_matches_container = self.driver.find_element(
                    By.XPATH, self.RECENT_GAMES_XPATH
                )

                containers = recent_matches_container.find_elements(
                    By.CLASS_NAME, "ind-match-container"
                )

                if index >= len(containers):
                    break

                data = containers[index]
                loss = "loss" in data.get_attribute("class")
                god_name = data.find_element(By.CLASS_NAME, "god-name").text

                WebDriverWait(data, self.PAGE_LOAD_WAIT_TIME).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "nav-to-match"))
                )

                nav_to_match = data.find_element(By.CLASS_NAME, "nav-to-match")

                WebDriverWait(nav_to_match, self.PAGE_LOAD_WAIT_TIME).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "alt--text"))
                )

                view_match_button = nav_to_match.find_element(
                    By.CLASS_NAME, "alt--text"
                )

                try:
                    actions = ActionChains(self.driver)
                    actions.move_to_element(view_match_button).perform()
                    view_match_button = nav_to_match.find_element(
                        By.CLASS_NAME, "alt--text"
                    )
                    view_match_button.click()
                except ElementClickInterceptedException:
                    self.output["messages"].append(
                        ("Stop moving your mouse please :c", "error")
                    )
                    continue

                WebDriverWait(self.driver, self.PAGE_LOAD_WAIT_TIME).until(
                    EC.presence_of_element_located((By.CLASS_NAME, self.MATCH_ID_CLASS))
                )

                while True:
                    match_id = self.driver.find_element(
                        By.CLASS_NAME, self.MATCH_ID_CLASS
                    ).text
                    if match_id:
                        break

                if match_id in prev_seen:
                    self.output["messages"].append((f"Found old {match_id}", "normal"))
                    self.output["messages"].append(("Stopping scrape", "normal"))
                    self.driver.quit()
                    return seen

                if match_id == "":
                    print(current_page, index, len(containers))
                    self.driver.back()
                    continue

                if match_id and match_id not in seen:
                    self.output["messages"].append(
                        (f"New match found: {match_id}", "normal")
                    )
                    self.output["messages"].append(
                        (
                            f"You {'lost' if loss else 'won'} as {god_name}",
                            "error" if loss else "normal",
                        )
                    )
                    seen.add(match_id)

                    team_one_container = WebDriverWait(
                        self.driver, self.PAGE_LOAD_WAIT_TIME
                    ).until(
                        EC.presence_of_all_elements_located(
                            (By.CLASS_NAME, "team-one-container")
                        )
                    )[
                        1
                    ]

                    temp_text = team_one_container.find_element(
                        By.CLASS_NAME, "match-result"
                    ).text
                    if (temp_text == "Winning Team" and loss) or (
                        temp_text == "Losing Team" and not loss
                    ):
                        enemy_container = team_one_container
                    else:
                        enemy_container = WebDriverWait(
                            self.driver, self.PAGE_LOAD_WAIT_TIME
                        ).until(
                            EC.presence_of_all_elements_located(
                                (By.CLASS_NAME, "team-two-container")
                            )
                        )[
                            1
                        ]

                    enemy_gods = []
                    for enemy in enemy_container.find_elements(
                        By.CLASS_NAME, "player-container"
                    ):
                        enemy_god_name = enemy.find_element(
                            By.CLASS_NAME, "god-name"
                        ).text
                        enemy_gods.append(enemy_god_name)

                    if god_name not in self.data:
                        self.data[god_name] = GodData(god_name)

                    if loss:
                        self.data[god_name].lose_against(enemy_gods)
                    else:
                        self.data[god_name].win_against(enemy_gods)
                else:
                    if not new_page:
                        self.output["messages"].append(("Done scraping!", "normal"))
                        break
                    self.driver.back()
                    continue

                # time.sleep(1)

                self.driver.back()

                index += 1
                self.output["gods_completed"] += 1
                WebDriverWait(self.driver, self.PAGE_LOAD_WAIT_TIME).until(
                    EC.presence_of_element_located((By.XPATH, self.RECENT_GAMES_XPATH))
                )

            current_page += 1
            if current_page > last_page:
                self.output["messages"].append(("Done scraping!", "normal"))
                break

        self.driver.quit()

        return seen

    def get_player_data(
        self,
        smitesource_url: str,
        filepath: str,
        output: dict,
        update_data: bool = True,
    ) -> None:
        self.output = output
        self.output["messages"] = []
        self.data, prev_seen = self.load_previous_data(filepath)

        if not update_data:
            self.output["data"] = self.data
            self.output["messages"].append(("Done scraping!", "normal"))
            return

        self.driver = self.create_driver()
        self.driver.get(smitesource_url)
        self.output["messages"].append(("Looking for smitesource profile", "normal"))

        try:
            WebDriverWait(self.driver, self.PAGE_LOAD_WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, self.IMG_AVATAR_XPATH))
            )
            self.output["messages"].append(("Found smitesource profile", "normal"))

        except TimeoutException:
            self.output["messages"].append(
                ("Couldn't find smitesource profile", "error")
            )
            self.output["messages"].append(
                ("Make sure you don't have a private profile", "warning")
            )
            return

        new_seen = self.get_matches(prev_seen)
        self.save_data(self.data, prev_seen | new_seen, filepath)
        self.output["messages"].append((f"Saved data to {filepath}", "normal"))

        self.output["data"] = self.data
