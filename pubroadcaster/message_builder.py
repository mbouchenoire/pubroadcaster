from tabulate import tabulate
from pubg import GameContext, GameStats, GlobalStats


class MessageBuilder(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def build_global_stats(stats: GlobalStats) -> str:
        message = "```Markdown\n"
        message += "# " + stats.profile.name + "\n"
        message += "> " + stats.game_context.mode + "@" + stats.game_context.region + "\n"
        message += "\n"
        message += tabulate(stats.values(), headers="firstrow")
        message += "```"

        return message

    @staticmethod
    def build_result_message(message_header: str, stats: GameStats, game_context: GameContext) -> str:
        concatenated_stats = []

        for individual_stats in stats:
            concatenated_stats.append(individual_stats.values())

        headers = stats[0].headers()

        message = "```Markdown\n"
        message += "# " + message_header + "\n"
        message += "> " + game_context.mode + "@" + game_context.region + "\n"
        message += "\n"
        message += tabulate(concatenated_stats, headers=headers)
        message += "```"

        return message
