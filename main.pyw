from algorithm import GodPicker
from application import App
from data import APIScraperBot

bot = APIScraperBot("files/chromedriver.exe", False, (1920, 1080))
god_picker = GodPicker("files/god_counters.txt")

# https://smitesource.com/player/Weak3n-925039
# https://smitesource.com/player/DanielGrotan-714491286
# https://smitesource.com/player/yourmomgey69420-714534506

app = App((1734, 600), bot, god_picker)
app.run()
