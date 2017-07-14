from tabulate import tabulate
from pubg import GameContext, GameStats, GlobalStats

class MessageBuilder(object):
    def __init__(self):
        pass

    def build_global_stats(self, stats: GlobalStats) -> str:
        message = "```Markdown\n"
        message += "# " + stats.profile.name + "\n"
        message += "> " + stats.game_context.mode + "@" + stats.game_context.region + "\n"
        message += "\n"
        message += tabulate(stats.values(), headers="firstrow")
        message += "```"

        return message

    def build_result_message(self, message_header: str, stats: GameStats, game_context: GameContext):
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