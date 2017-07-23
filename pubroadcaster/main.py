import time
import discord
import asyncio
import traceback
import logging as log
from pubg import GameContext, GameFacts, GameStats, Profile, PubgTracker
from message_builder import MessageBuilder
from command_handler import CommandHandler

class Main(object):
    def __init__(self, tracking_interval, pubg_tracker_api_key, discord_bot_token, discord_channel_id, profile_names):
        self.tracking_interval = tracking_interval
        self.tracker = PubgTracker(pubg_tracker_api_key)
        self.discord_bot_token = discord_bot_token
        self.discord_channel_id = discord_channel_id
        self.profile_names = profile_names
        self.snapshots = {}

    def run(self):
        """Runs the bot"""
        discord_client = discord.Client()

        async def broadcast_incremented_stats(incremented_stats: GameStats, game_context: GameContext, header: str, discord_client: discord.Client, broadcast_channel: discord.Channel):
            for game_context in incremented_stats.keys():
                contextualized_incremented_stats = incremented_stats[game_context]
                message = MessageBuilder().build_result_message(header, contextualized_incremented_stats, game_context)
                await discord_client.send_message(broadcast_channel, message)

        @discord_client.event
        async def on_message(message):
            await CommandHandler(discord_client, self.tracker, MessageBuilder()).handle(message)
        
        async def check_stats_task():
            await discord_client.wait_until_ready()
            log.info("ready to send messages to the discord channel with id: " + self.discord_channel_id)
            broadcast_channel = discord_client.get_channel(id=self.discord_channel_id)

            while not discord_client.is_closed:
                log.info("scaning players: " + ",".join(self.profile_names) + " (interval: " + str(self.tracking_interval) + "s)...")

                incremented_stats_wins = {}
                incremented_stats_toptens = {}
                temp_snapshots = {}

                for profile_name in self.profile_names:
                    log.debug("tracking " + profile_name + "...")

                    profile = None

                    try:
                        profile = self.tracker.retreive_profile(profile_name)
                    except:
                        log.error(profile_name + "'s profile could not be retreived")
                        log.error(traceback.format_exc())
                        break

                    known_snapshot = profile_name in self.snapshots
                    snapshot = self.snapshots[profile_name] if known_snapshot else profile

                    profile_stats = profile.Stats if hasattr(profile, "Stats") else []

                    for stats in profile_stats:
                        game_context = GameContext(stats["Season"], stats["Region"], stats["Match"])

                        if game_context.region == "agg":
                            continue

                        new_win = profile.has_won(snapshot, game_context)
                        new_topten = profile.has_topten(snapshot, game_context)

                        relevant_incremented_stats = None

                        if new_win:
                            log.info(profile_name + " registered a new win")
                            relevant_incremented_stats = incremented_stats_wins
                        elif new_topten:
                            log.info(profile_name + " registered a new top 10")
                            relevant_incremented_stats = incremented_stats_toptens

                        if relevant_incremented_stats is not None:
                            incremented_stats = profile.get_game_stats(snapshot, game_context)

                            if game_context in relevant_incremented_stats:
                                relevant_incremented_stats[game_context].append(incremented_stats)
                            else:
                                relevant_incremented_stats[game_context] = [incremented_stats]

                    temp_snapshots[profile_name] = profile
                    await asyncio.sleep(1)  # the pubgtracker api does not allow more than 1 query per second

                # We save the retreived stats only if every profile has been successfully retreived
                for profile_name in temp_snapshots.keys():
                    self.snapshots[profile_name] = temp_snapshots[profile_name]

                await broadcast_incremented_stats(incremented_stats_wins, game_context, "WIN", discord_client, broadcast_channel)
                await broadcast_incremented_stats(incremented_stats_toptens, game_context, "TOP 10", discord_client, broadcast_channel)

                await asyncio.sleep(self.tracking_interval)

        discord_client.loop.create_task(check_stats_task())
        discord_client.run(self.discord_bot_token)
