import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from bot.env import *
from bot.functions import *


class DisplayingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="show", description="Show the content of a specified file.")
    @app_commands.describe(name="File name to display the content of.")
    async def show(self, interaction: discord.Interaction, name: str):
        phrase = special_phrase(catch_phrase, interaction.user.id)
        try:
            item = await get_item_data(name, interaction.user.id)
            if item['message_id'] is None:
                await interaction.response.send_message(f"Can't show a folder. {phrase}")
            else:
                result = await fetch_message(item, self.bot)
                await interaction.response.defer()
                await send_message_and_embed_images(interaction, result, self.bot)
        except ValueError as ve:
            await interaction.response.send_message(str(ve) + f"\n{phrase}")
        except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
            if isinstance(e, discord.NotFound):
                await interaction.response.send_message(f"Message has been deleted. {phrase}")
            elif isinstance(e, discord.Forbidden):
                await interaction.response.send_message(f"Access forbidden to the message. {phrase}")
            else:
                await interaction.response.send_message(f"HTTP error occurred: {str(e)}\n{phrase}")

    @app_commands.command(name="repeat", description="Show the content of a specified file.")
    @app_commands.describe(name="File name to display the content of.", times="Times the message should display")
    async def repeat(self, interaction: discord.Interaction, name: str, times: int):
        phrase = special_phrase(catch_phrase, interaction.user.id)
        try:
            item = await get_item_data(name, interaction.user.id)
            if item['message_id'] is None:
                await interaction.response.send_message(f"Can't show a folder. {phrase}")
            else:
                result = await fetch_message(item, self.bot)
                await interaction.response.defer()
                for _ in range(times):
                    await send_message_and_embed_images(interaction, result, self.bot)
        except ValueError as ve:
            await interaction.response.send_message(str(ve) + f"\n{phrase}")
        except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
            if isinstance(e, discord.NotFound):
                await interaction.response.send_message(f"Message has been deleted. {phrase}")
            elif isinstance(e, discord.Forbidden):
                await interaction.response.send_message(f"Access forbidden to the message. {phrase}")
            else:
                await interaction.response.send_message(f"HTTP error occurred: {str(e)}\n{phrase}")

    @app_commands.command(name="random", description="Get a random line or message from a file or folder.")
    @app_commands.describe(name="File or folder name to retrieve a random item from.")
    async def random(self, interaction: discord.Interaction, name: str):
        import random
        phrase = special_phrase(catch_phrase, interaction.user.id)
        try:
            item = await get_item_data(name, interaction.user.id)
            if item['message_id'] is None:
                children = get_children(name, interaction.user.id)
                random_child = random.choice(children)

                result = await fetch_message(random_child, self.bot)
                await interaction.response.defer()
                await send_message_and_embed_images(interaction, result, self.bot)
            else:
                result = await fetch_message(item, self.bot)
                lines = result["message"].content.split("\n")

                random_line = random.choice(lines)
                random_image = random.choice(result["images"]) if result["images"] else None

                result["message"].content = random_line if random_line else ""
                result["images"] = [random_image] if random_image else []

                await interaction.response.defer()
                await send_message_and_embed_images(interaction, result, self.bot)
        except ValueError as ve:
            await interaction.response.send_message(str(ve) + f"\n{phrase}")
        except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
            if isinstance(e, discord.NotFound):
                await interaction.response.send_message(f"Message has been deleted. {phrase}")
            elif isinstance(e, discord.Forbidden):
                await interaction.response.send_message(f"Access forbidden to the message. {phrase}")
            else:
                await interaction.response.send_message(f"HTTP error occurred: {str(e)}\n{phrase}")

    @app_commands.command(name="get", description="Get a link to a specified file.")
    @app_commands.describe(name="File name to get the link for.")
    async def get(self, interaction: discord.Interaction, name: str):
        phrase = special_phrase(catch_phrase, interaction.user.id)
        try:
            item = await get_item_data(name, interaction.user.id)
            if item['message_id'] is None:
                await interaction.response.send_message(f"Can't get a folder. {phrase}")
                return

            channel = self.bot.get_channel(item["channel_id"])
            original_message = await channel.fetch_message(item["message_id"])
            message_link = original_message.jump_url
            await interaction.response.send_message(f"[{name}]({message_link})")
        except discord.NotFound:
            await interaction.response.send_message(f"Message or channel not found. {phrase}")
        except discord.Forbidden:
            await interaction.response.send_message(f"I don't have permission to forward the message. {phrase}")
        except discord.HTTPException as e:
            await interaction.response.send_message(f"An error occurred: {e}. {phrase}")

    @app_commands.command(name="set", description="Set a channel for messages to be sent to")
    @app_commands.describe(channel="The channel to show stored messages in")
    async def set(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        phrase = special_phrase(catch_phrase, interaction.user.id)

        owner_id = interaction.user.id
        channel_id = channel.id if channel else None

        if not check_user(owner_id):
            create_user(owner_id, interaction.user.name, channel_id)
            check = check_user(owner_id)
        else:
            check = update_set_channel(channel_id, owner_id)

        if not check:
            await interaction.response.send_message(f"Failed to set channel. {phrase}")
        else:
            await interaction.response.send_message(f"Successfully set channel. {phrase}")


async def setup(bot):
    await bot.add_cog(DisplayingCog(bot))
