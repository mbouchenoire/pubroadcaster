from pubg import GameContext
from message_builder import MessageBuilder


class CommandHandler(object):
    _INVALID_FORMAT_MESSAGE = "This is not a valid command." \
                              " The format should be : `!pubg <profile_name> <mode>@<region>`"
    _ALLOWED_MODES = ["solo", "duo", "squad"]
    _ALLOWED_REGIONS = ["eu", "na", "sa"]

    def __init__(self, discord_client, pubg_tracker, message_builder) -> None:
        self._discord_client = discord_client
        self._pubg_tracker = pubg_tracker
        self._message_builder = message_builder

    async def handle(self, command) -> None:
        if command.content.startswith("!pubg"):
            await self.handle_pubg(command)

    async def handle_pubg(self, command):
        parts = command.content.split(" ")

        if len(parts) != 3:
            return await self._discord_client.send_message(command.channel, CommandHandler._INVALID_FORMAT_MESSAGE)

        profile_name = parts[1]
        mode_region_text = parts[2]

        if "@" not in mode_region_text:
            return await self._discord_client.send_message(command.channel, CommandHandler._INVALID_FORMAT_MESSAGE)

        mode = mode_region_text.split("@")[0]

        if mode not in CommandHandler._ALLOWED_MODES:
            return await self._discord_client.send_message(command.channel, "'" + mode + "' is not a valid mode!")

        region = mode_region_text.split("@")[1]
        
        if region not in CommandHandler._ALLOWED_REGIONS:
            return await self._discord_client.send_message(command.channel, "'" + region + "' is not a valid region!")

        profile = self._pubg_tracker.retreive_profile(profile_name)
        game_context = GameContext(profile.defaultSeason, region, mode)
        message = MessageBuilder.build_global_stats(profile.get_global_stats(game_context))

        return await self._discord_client.send_message(command.channel, message)
