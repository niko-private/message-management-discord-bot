import discord
from discord.ext import commands
from bot.env import discord_token
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

    for filename in os.listdir("./bot/cogs"):
        if filename.endswith("Cog.py"):
            try:
                await bot.load_extension(f"bot.cogs.{filename[:-3]}")
                print(f"Loaded {filename[:-3]}")
            except Exception as e:
                print(f"Error loading {filename[:-3]}: {e}")


@bot.command(name="sync")
async def sync(ctx):
    await ctx.send("Synchronizing")
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s).")


if __name__ == "__main__":
    bot.run(discord_token)
