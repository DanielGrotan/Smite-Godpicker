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
        self,
        data: dict[str, GodData],
        gods_picked: set[str],
        gods_banned: set[str],
        console_messages,
        amount: int = 1,
    ) -> list[str]:
        if not gods_picked:
            return [
                tup[0]
                for tup in sorted(
                    data.items(), key=lambda tup: tup[1].value, reverse=True
                )
                if tup[0] not in gods_banned
            ][:amount]

        god_ratings: list[tuple[str, int]] = []
        for god_name, god_data in data.items():
            if god_name in gods_banned | gods_picked:
                continue

            value = 0
            num_counters_you = 0
            num_you_counter = 0

            # Check counters
            for counter in self.counter_checker.get_counters(god_name):
                if counter in gods_banned:
                    continue
                if counter in gods_picked:
                    num_counters_you += 1
                    if (
                        data[god_name].matchups[counter][0]
                        + data[god_name].matchups[counter][1]
                        == 0
                    ):
                        lose_rate_against = 0.5
                        console_messages.append(
                            (
                                f"You have never played as {god_name} against the counter {counter}",
                                "warning",
                            )
                        )
                    else:
                        lose_rate_against = data[god_name].matchups[counter][1] / (
                            data[god_name].matchups[counter][0]
                            + data[god_name].matchups[counter][1]
                        )
                        console_messages.append(
                            (
                                f"Your lose rate as {god_name} against {counter} is {lose_rate_against}",
                                "normal",
                            )
                        )

                    value -= 5 * num_counters_you * lose_rate_against

            # Check if you counter
            for enemy_god in gods_picked:
                if enemy_god in gods_banned:
                    continue
                for counter in self.counter_checker.get_counters(enemy_god):
                    if counter == god_name:
                        if (
                            data[god_name].matchups[counter][0]
                            + data[god_name].matchups[counter][1]
                            == 0
                        ):
                            win_rate_against = 0.5
                            console_messages.append(
                                (
                                    f"You have never played as {god_name} against {enemy_god}, who they counter",
                                    "warning",
                                )
                            )
                        else:
                            win_rate_against = data[god_name].matchups[counter][0] / (
                                data[god_name].matchups[counter][0]
                                + data[god_name].matchups[counter][1]
                            )
                            console_messages.append(
                                (
                                    f"Your win rate as {god_name} against {enemy_god} is {win_rate_against}",
                                    "normal",
                                )
                            )
                        num_you_counter += 1
                        value += 5 * num_you_counter * win_rate_against
                        break

            # Add your skill with the character
            # Should only count for 1/3 of the toal value

            value = value / 3 * 2 + god_data.value / 3
            god_ratings.append((god_name, value))

        god_ratings.sort(key=lambda god: god[1], reverse=True)
        return [god[0] for god in god_ratings][:amount]

        """
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
        """
