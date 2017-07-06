import time
import discord
import asyncio
import logging as log
from pubg_tracker import PubgTracker
from message_builder import MessageBuilder

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
        
        async def check_stats_task():
            await discord_client.wait_until_ready()
            log.info("ready to send messages to the discord channel with id: " + self.discord_channel_id)

            broadcast_channel = discord_client.get_channel(id=self.discord_channel_id)

            while not discord_client.is_closed:
                await asyncio.sleep(self.tracking_interval)
                log.info("scaning players: " + ",".join(self.profile_names) + " (interval: " + str(self.tracking_interval) + "s)...")

                for profile_name in self.profile_names:
                    await asyncio.sleep(1) # the pubgtracker api does not allow more than 1 query per second
                    log.debug("tracking " + profile_name + "...")
                    
                    profile = self.tracker.get_profile(profile_name)
                    known_snapshot = profile_name in self.snapshots
                    snapshot = self.snapshots[profile_name] if known_snapshot else profile

                    for stats in profile.Stats:
                        region = stats["Region"]
                        season = stats["Season"]
                        mode = stats["Match"]

                        win = profile.has_incremented_from(snapshot, region, season, mode, u'Wins')
                        topten = profile.has_incremented_from(snapshot, region, season, mode, u'Top10s')

                        message = None

                        if win and region != "agg":
                            message = MessageBuilder().build_win(profile_name, snapshot, profile, region, season, mode)
                        elif topten and region != "agg":
                            message = MessageBuilder().build_topten(snapshot, profile)
                            
                        if message is not None:
                            log.info(message)
                            await discord_client.send_message(broadcast_channel, message)

                    self.snapshots[profile_name] = profile

        discord_client.loop.create_task(check_stats_task())
        discord_client.run(self.discord_bot_token)
