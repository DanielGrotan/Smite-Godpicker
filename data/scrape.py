import pickle
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Protocol

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Match:
    pass


@dataclass
class GodData:
    god_name: str
    matchups: dict[str, list[int, int]] = field(init=False)
    total_wins: int = field(init=False, default=0)
    total_losses: int = field(init=False, default=0)

    def __post_init__(self):
        self.matchups = defaultdict(self.default_value)

    def win_against(self, gods: list[str]):
        self.total_wins += 1
        for god in gods:
            self.matchups[god][0] += 1

    def lose_against(self, gods: list[str]):
        self.total_losses += 1
        for god in gods:
            self.matchups[god][1] += 1

    def default_value(self):
        return [0, 0]

    @property
    def win_rate(self):
        if self.total_wins + self.total_losses == 0:
            return 0

        return self.total_wins / (self.total_wins + self.total_losses)

    @property
    def value(self):
        x = min(self.total_wins + self.total_losses, 100)
        if x == 0:
            return 0

        return 10 / 7 * x ** 0.5 + self.win_rate * 10

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
        options = Options()

        if not show_window:
            options.add_argument("--headless")
        options.add_argument(f"--window-size={screen_size[0]},{screen_size[1]}")
        self.driver = Chrome(executable_path=path_to_driver, chrome_options=options)

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

    def load_previous_data(self, filepath) -> dict[str, GodData]:
        try:
            with open(filepath, "rb") as data_file:
                return pickle.load(data_file)
        except FileNotFoundError:
            return {}, 0

    def save_data(self, data, latest_match_id: int, filepath: str):
        with open(filepath, "wb") as data_file:
            pickle.dump([data, latest_match_id], data_file)

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
            next_button.click()
            time.sleep(0.1)

            WebDriverWait(self.driver, self.PAGE_LOAD_WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, self.RECENT_GAMES_XPATH))
            )

        return True

    def get_matches(self, stop_id: int) -> tuple[int, list[Match]]:
        new_page = True
        seen = set()
        latest_match_id = None

        current_page = 0
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

                actions = ActionChains(self.driver)
                actions.move_to_element(view_match_button).perform()

                view_match_button.click()

                WebDriverWait(self.driver, self.PAGE_LOAD_WAIT_TIME).until(
                    EC.presence_of_element_located((By.CLASS_NAME, self.MATCH_ID_CLASS))
                )

                match_id = self.driver.find_element(
                    By.CLASS_NAME, self.MATCH_ID_CLASS
                ).text
                if match_id == stop_id:
                    return

                if match_id not in seen:
                    seen.add(match_id)
                    if latest_match_id is None:
                        latest_match_id = match_id

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

                time.sleep(1)

                self.driver.back()

                index += 1
                WebDriverWait(self.driver, self.PAGE_LOAD_WAIT_TIME).until(
                    EC.presence_of_element_located((By.XPATH, self.RECENT_GAMES_XPATH))
                )

            current_page += 1

        self.driver.quit()

        return latest_match_id if latest_match_id is not None else stop_id

    def get_player_data(
        self, smitesource_url: str, filepath: str, update_data: bool = True
    ) -> dict[str, GodData]:
        self.data, latest_match_id = self.load_previous_data(filepath)

        if not update_data:
            return self.data

        self.driver.get(smitesource_url)

        try:
            WebDriverWait(self.driver, self.PAGE_LOAD_WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, self.IMG_AVATAR_XPATH))
            )

        except TimeoutException:
            print("Couldn't find player profile")
            return {}

        latest_match_id = self.get_matches(latest_match_id)
        self.save_data(self.data, latest_match_id, filepath)

        return self.data
