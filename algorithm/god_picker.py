from collections import defaultdict

from data import GodData


class CounterCheck:
    def __init__(self, filename: str):
        self.file = filename
        self.counters = defaultdict(list)
        self.read_data()

    def read_data(self) -> None:
        try:
            with open(self.file, "r") as f:
                content = f.read()
            for line in content.split("\n"):
                gods = line.split(",")
                self.counters[gods[0]] = gods[1:]
        except FileNotFoundError:
            print("no such file")

    def get_counters(self, god_name: str):
        return self.counters[god_name]


class GodPicker:
    def __init__(self, filename: str):
        self.counter_checker = CounterCheck(filename)

    def get_best_gods(
        self, data: dict[str, GodData], gods_picked: set[str], amount: int = 1
    ) -> list[str]:
        if not gods_picked:
            return sorted(data.keys(), key=lambda key: data[key], reverse=True)

        decrease_value = 4.5
        increase_value = 4.5
        gods = []
        for god, god_data in data.items():
            value = god_data.value

            for counter in self.counter_checker.get_counters(god):
                if (
                    data[god].matchups[counter][0] + data[god].matchups[counter][1]
                ) == 0:
                    lose_rate = 0.5
                else:
                    lose_rate = data[god].matchups[counter][1] / (
                        data[god].matchups[counter][0] + data[god].matchups[counter][1]
                    )

                if counter in gods_picked:
                    value -= decrease_value * lose_rate * 2
                    decrease_value *= 1.2

            for enemy_god in gods_picked:
                if (
                    data[god].matchups[enemy_god][0] + data[god].matchups[enemy_god][1]
                    == 0
                ):
                    win_rate = 0.5
                else:
                    win_rate = data[god].matchups[enemy_god][0] / (
                        data[god].matchups[enemy_god][0]
                        + data[god].matchups[enemy_god][1]
                    )

                if god in self.counter_checker.get_counters(enemy_god):
                    value += increase_value * win_rate * 2
                    increase_value *= 1.2

                value += win_rate * 10

            gods.append((god, value))

        gods.sort(key=lambda god: god[1], reverse=True)
        return [god[0] for god in gods][:amount]
