import discord
from discord.ext import commands
from discord import app_commands
from bot.env import *
from bot.functions import *


class CreatingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="store", description="Store a message with a specified file name.")
    @app_commands.describe(name="File name to store the message under.", id="Message id of the stored message.")
    async def store(self, interaction: discord.Interaction, name: str, id: str):
        phrase = special_phrase(catch_phrase, interaction.user.id)
        id = int(id)
        if "," in name:
            await interaction.response.send_message(f"Can't include ',' in file names. {phrase}")
        else:
            channel = interaction.channel
            try:
                original_message = await channel.fetch_message(id)
                message_id = original_message.id
                owner_id = interaction.user.id
                channel_id = interaction.channel.id

                if not check_user(owner_id):
                    create_user(owner_id, interaction.user.name)

                if get_item(name, owner_id) is not None:
                    await interaction.response.send_message(f"Name already taken. {phrase}")
                else:
                    create_item(name, None, owner_id, channel_id, message_id)
                    await interaction.response.send_message(f'Message, {name} stored. {phrase}')
            except discord.NotFound:
                await interaction.response.send_message(f"Message not found. Please check the message ID. {phrase}")

    @app_commands.command(name="make", description="Create a folder with a specified name.")
    @app_commands.describe(name="Folder name to create.")
    async def make(self, interaction: discord.Interaction, name: str):
        phrase = special_phrase(catch_phrase, interaction.user.id)
        if "," in name:
            await interaction.response.send_message(f"Can't include ',' in file names. {phrase}")
            return

        owner_id = interaction.user.id
        if not check_user(owner_id):
            create_user(owner_id, interaction.user.name)

        if get_item(name, owner_id) is not None:
            await interaction.response.send_message(f"Name already taken. {phrase}")
        else:
            create_item(name, None, owner_id, None, None)
            await interaction.response.send_message(f"Folder, {name} stored. {phrase}")

    @app_commands.command(name="save", description="Save a specified number of messages from a channel. (max = 100)")
    @app_commands.describe(channel="Channel to fetch messages from.", limit="Number of messages to save.")
    async def save(self, interaction: discord.Interaction, channel: discord.TextChannel, limit: int):
        phrase = special_phrase(catch_phrase, interaction.user.id)
        owner_id = interaction.user.id
        channel_id = channel.id
        channel_name = channel.name if channel.name else str(channel_id)

        if not check_user(owner_id):
            create_user(owner_id, interaction.user.name)

        if get_item(channel_name, owner_id) is not None:
            await interaction.response.send_message(f"Name already taken. {phrase}")
            return
        else:
            create_item(channel_name, None, owner_id, None, None)

        item = await get_item_data(channel_name, owner_id)
        parent_id = item['_id']

        count, saved, skipped, forbidden = 0, 0, 0, 0
        async for message in channel.history(limit=limit):
            count += 1
            if count > 100:
                break
            name = f"{channel_name}_{count}"

            if get_item(name, owner_id) is not None:
                skipped += 1
                continue

            try:
                create_item(name, parent_id, owner_id, channel_id, message.id)
                saved += 1
            except discord.Forbidden:
                forbidden += 1
            except discord.NotFound:
                skipped += 1

        summary = f"Processed {count} messages in {channel_name}."
        if saved > 0:
            summary += f"\nSaved: {saved} messages."
        if skipped > 0:
            summary += f"\nSkipped (existing name): {skipped} messages."
        if forbidden > 0:
            summary += f"\nForbidden Access: {forbidden} messages."

        await interaction.response.send_message(f"{summary} {phrase}")


async def setup(bot):
    await bot.add_cog(CreatingCog(bot))
