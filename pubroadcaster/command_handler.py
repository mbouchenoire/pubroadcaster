class CommandHandler(object):
    def __init__(self, discord_client, pubg_tracker, message_builder):
        self.discord_client = discord_client
        self.pubg_tracker = pubg_tracker
        self.message_builder = message_builder
        self.INVALID_FORMAT_MESSAGE = "This is not a valid command. The format should be : `!pubg <profile_name> <mode>@<region>`"
        self.ALLOWED_MODES = ["solo", "duo", "squad"]
        self.ALLOWED_REGIONS = ["eu", "na", "sa"]

    async def handle(self, command):
        if command.content.startswith("!pubg"):
            await self.handle_pubg(command)

    async def handle_pubg(self, command):
        parts = command.content.split(" ")

        if len(parts) != 3:
            return await self.discord_client.send_message(command.channel, self.INVALID_FORMAT_MESSAGE)

        profile_name = parts[1]
        mode_region_text = parts[2]

        if "@" not in mode_region_text:
            return await self.discord_client.send_message(command.channel, self.INVALID_FORMAT_MESSAGE)

        mode = mode_region_text.split("@")[0]

        if mode not in self.ALLOWED_MODES:
            return await self.discord_client.send_message(command.channel, "'" + mode + "' is not a valid mode!")

        region = mode_region_text.split("@")[1]
        
        if region not in self.ALLOWED_REGIONS:
            return await self.discord_client.send_message(command.channel, "'" + region + "' is not a valid region!")

        profile = self.pubg_tracker.get_profile(profile_name)
        message = self.message_builder.build_stats(profile_name, profile, region, profile.defaultSeason, mode)

        return await self.discord_client.send_message(command.channel, message)