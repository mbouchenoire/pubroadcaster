import time
import discord
import asyncio
import logging as log
from pubg_tracker import PubgTracker

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

                        up_to_date_win_count = profile.get_wins_count(region, season, mode)
                        previous_win_count = snapshot.get_wins_count(region, season, mode)

                        up_to_date_topten_count = profile.get_topten_count(region, season, mode)
                        previous_topten_count = snapshot.get_topten_count(region, season, mode)

                        top_one = (up_to_date_win_count > previous_win_count and region != "agg")
                        top_ten = (up_to_date_topten_count > previous_topten_count and region != "agg")

                        top = "?"

                        if top_one:
                            top = "1"
                        elif top_ten:
                            top = "10"

                        if top_one or top_ten:
                            up_to_date_kills_count = profile.get_kills_count(region, season, mode)
                            previous_kills_count = snapshot.get_kills_count(region, season, mode)
                            kills = up_to_date_kills_count - previous_kills_count

                            msg = "TOP {} ({}@{}): {} -> {} kills".format(top, mode, region, profile_name, kills)
                            
                            log.info(msg)
                            await discord_client.send_message(broadcast_channel, msg)

                    self.snapshots[profile_name] = profile

        discord_client.loop.create_task(check_stats_task())
        discord_client.run(self.discord_bot_token)
