import time
import discord
import asyncio
import traceback
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
                    try:
                        await asyncio.sleep(1) # the pubgtracker api does not allow more than 1 query per second
                        log.debug("tracking " + profile_name + "...")
                        profile = self.tracker.get_profile(profile_name)
                        known_snapshot = profile_name in self.snapshots
                        snapshot = self.snapshots[profile_name] if known_snapshot else profile

                        for stats in profile.Stats:
                            region = stats["Region"]
                            season = stats["Season"]
                            mode = stats["Match"]

                            win = profile.has_won(snapshot, region, season, mode)
                            topten = profile.has_topten(snapshot, region, season, mode)

                            message = None

                            if win and region != "agg":
                                message = MessageBuilder().build_win(profile_name, snapshot, profile, region, season, mode)
                            elif topten and region != "agg":
                                message = MessageBuilder().build_topten(profile_name, snapshot, profile, region, season, mode)
                                
                            if message is not None:
                                log.info(message)
                                await discord_client.send_message(broadcast_channel, message)

                        self.snapshots[profile_name] = profile
                    except Exception as e:
                        log.error(traceback.format_exc())
                    

        discord_client.loop.create_task(check_stats_task())
        discord_client.run(self.discord_bot_token)
