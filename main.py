from algorithm import GodPicker
from data import APIScraperBot

bot = APIScraperBot("files/chromedriver.exe", False)
data = bot.get_player_data(
    "https://smitesource.com/player/DanielGrotan-714491286",
    "files/gods_data_big_thor.pkl",
    False,
)

# https://smitesource.com/player/DanielGrotan-714491286")
# https://smitesource.com/player/yourmomgey69420-714534506

god_picker = GodPicker("files/god_counters.txt")


print(god_picker.get_best_gods(data, ["Ao Kuang", "Loki", "Arachne", "Athena"], 3))
