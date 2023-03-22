import discord
import os
import logging
import argparse
from discord.ext import commands, tasks



token = "MTA4NTEwOTA1NTIyMTEzNzQ0OA.GaccWA._mb0VjxMeE9ZaQVFVLqFIk2OeFdIV_Wrrr0UEE"
class Bot(commands.Bot):
    def __init__(self, debug = False):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(
            command_prefix=commands.when_mentioned_or('!'),
            intents=intents,
            description='Jack_bot_test',
            status = discord.Status.online
        )
        self.debug = debug
    async def on_ready(self):
        logging.info(f'bot is ready')
        print('bot is ready')
        await load_extensions()
        await self.tree.sync()



async def load_extensions():
    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
	        await bot.load_extension("cogs." + f[:-3])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Enable debug mode. (Default: False)')
    args = parser.parse_args()

    bot = Bot(args.debug)
    bot.run(token)


