import os
import logging
import tempfile
import urllib.request
import discord
import pubg
from typing import List


class UpdateBotProfileCommand(object):
    MAXIMUM_TEXT_LENGTH = 15

    def __init__(self, discord_client: discord.Client, avatar_bytes: bytearray, name: str, text: str):
        self._discord_client = discord_client
        self._avatar_bytes = avatar_bytes
        self._name = name
        self._text = text

    async def execute(self):
        try:
            if self._text is not None:
                logging.info("updating bot presence ('{}')".format(self._text))
                await self._discord_client.change_presence(game=discord.Game(name=self._text))
        except:
            logging.exception("could not change bot presence")

        try:
            if self._avatar_bytes is not None:
                logging.info("updating bot avatar...")
                await self._discord_client.edit_profile(password=None,
                                                        username=self._name,
                                                        avatar=self._avatar_bytes)
                logging.info("bot avatar uploaded successfully")
        except:
            logging.exception("could not change bot avatar")


class UpdateKingOfTheHillCommand(object):
    def __init__(self,
                 discord_client: discord.Client,
                 game_stats: List[pubg.GameStats]) -> None:

        if len(game_stats) < 1:
            raise ValueError("there must be at least one King Of The Hill")

        self._discord_client = discord_client
        self._game_stats = game_stats

    @staticmethod
    def __sort_profiles__(game_stats: List[pubg.GameStats]) -> List[pubg.Profile]:
        game_stats.sort(key=lambda g: g.score(), reverse=True)
        return list(map(lambda g: g.profile, game_stats))

    @staticmethod
    def __get_avatar_bytes__(profile: pubg.Profile) -> bytearray:
        avatar_hash = hash(profile.Avatar)
        avatar_file_path = os.path.join(tempfile.gettempdir(), str(avatar_hash))

        if not os.path.isfile(avatar_file_path):
            urllib.request.urlretrieve(profile.Avatar, avatar_file_path)

        f = open(avatar_file_path, "rb")

        try:
            return f.read()
        finally:
            f.close()

    @staticmethod
    def __get_kings_text__(profiles: List[pubg.Profile]):
        if len(profiles) < 1:
            raise ValueError("there must be at least of King Of The Hill")

        separator_count = len(profiles)-1
        characters_per_profile = (UpdateBotProfileCommand.MAXIMUM_TEXT_LENGTH - separator_count) // len(profiles)

        return "+".join([profile.name[0:characters_per_profile] for profile in profiles])

    async def execute(self):
        sorted_profiles = UpdateKingOfTheHillCommand.__sort_profiles__(self._game_stats)
        kings_text = UpdateKingOfTheHillCommand.__get_kings_text__(sorted_profiles)
        avatar_bytes = UpdateKingOfTheHillCommand.__get_avatar_bytes__(sorted_profiles[0])
        bot_profile_name = "PUBG King" + "s" if len(sorted_profiles) > 1 else ""
        await UpdateBotProfileCommand(self._discord_client, avatar_bytes, bot_profile_name, kings_text).execute()
