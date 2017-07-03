import os
import logging
from main import Main

def check_environment_variable(key, value):
    if not value: raise ValueError("environment variable '" + key + "' must be set")

logging.basicConfig(level=logging.INFO)

PUBGTRACKER_API_KEY = os.environ["PUBGTRACKER_API_KEY"]
check_environment_variable("PUBGTRACKER_API_KEY", PUBGTRACKER_API_KEY)

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
check_environment_variable("DISCORD_BOT_TOKEN", DISCORD_BOT_TOKEN)

DISCORD_CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]
check_environment_variable("DISCORD_CHANNEL_ID", DISCORD_CHANNEL_ID)

PUBG_PROFILE_NAMES = os.environ["PUBG_PROFILE_NAMES"]
check_environment_variable("PUBG_PROFILE_NAMES", PUBG_PROFILE_NAMES)

Main(2, PUBGTRACKER_API_KEY, DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, PUBG_PROFILE_NAMES.split(",")).run()
