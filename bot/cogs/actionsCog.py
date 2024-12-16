import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from bot.env import *
from bot.functions import *


class ActionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rename", description="Rename a file to a new name.")
    @app_commands.describe(file_name="Current file name.", new_name="New file name.")
    async def rename(self, interaction: discord.Interaction, file_name: str, new_name: str):
        phrase = special_phrase(catch_phrase, interaction.user.id)

        if "," in new_name:
            await interaction.response.send_message(f"Can't include ',' in file names. {phrase}")
            return

        check = rename_file(file_name, new_name, interaction.user.id)

        if not check:
            await interaction.response.send_message(f"{file_name} not stored or {new_name} already exists. {phrase}")
        else:
            await interaction.response.send_message(f"Renamed file {file_name} to {new_name}. {phrase}")

    @app_commands.command(name="move", description="Move files to a specified folder.")
    @app_commands.describe(files="Files to move.", folder_name="Destination folder if provided")
    async def move(self, interaction: discord.Interaction, files: str, folder_name: Optional[str] = None):
        phrase = special_phrase(catch_phrase, interaction.user.id)

        files = files.split(",")

        fail = "Failed to move: "
        count_fail = 0
        for file in files:
            check = update_parent(file.strip(), folder_name, interaction.user.id)
            if not check:
                fail += file + " "
                count_fail += 1

        if count_fail > 0:
            await interaction.response.send_message(fail + f"\n{phrase}")
        else:
            await interaction.response.send_message(f"Successfully moved all files. {phrase}")

    @app_commands.command(name="delete", description="Delete specified files.")
    @app_commands.describe(files="Files to delete.")
    async def delete(self, interaction: discord.Interaction, files: str):
        phrase = special_phrase(catch_phrase, interaction.user.id)

        files = files.split(",")

        fail = "Failed to delete: "
        count_fail = 0
        for file in files:
            check = delete_node(file.strip(), interaction.user.id)
            if check is not None:
                fail += file + " "
                count_fail += 1

        if count_fail > 0:
            await interaction.response.send_message(fail + f". {phrase}")
        else:
            await interaction.response.send_message(f"Successfully deleted. {phrase}")

    @app_commands.command(name="offer", description="Offer a file or files to a user")
    @app_commands.describe(name="User to send file to", file_name="File name to offer")
    async def offer(self, interaction: discord.Interaction, name: discord.User, file_name: str):
        phrase = special_phrase(catch_phrase, interaction.user.id)

        offer_user = interaction.user

        item = get_item(file_name, offer_user.id)
        if not item:
            await interaction.response.send_message(f"No such file. {phrase}")
            return

        trade_cache[name.id] = {"file_name": file_name, "offerer_id": offer_user.id}
        await interaction.response.send_message(f"{offer_user} has offered {name} the file '{file_name}'. {phrase}")

    @app_commands.command(name="accept", description="Accept an offer made by another user")
    @app_commands.describe(name="User who offered the file", append_name="Append to the file name")
    async def accept(self, interaction: discord.Interaction, name: discord.User, append_name: str):
        phrase = special_phrase(catch_phrase, interaction.user.id)

        if "," in append_name:
            await interaction.response.send_message(f"Can't include ',' in file names. {phrase}")
            return

        accept_user = interaction.user
        offer_data = trade_cache.get(accept_user.id)

        if not search_node(offer_data["file_name"], offer_data["offerer_id"], accept_user.id, append_name):
            await interaction.response.send_message(
                f"Some files already exist, please use a unique append name. {phrase}")
        elif offer_data and offer_data["offerer_id"] == name.id:
            set_nodes(offer_data["file_name"], name.id, accept_user.id, message_append=append_name)

            await interaction.response.send_message(
                f"You have accepted the offer of {offer_data['file_name']} from {name}. {phrase}")
            del trade_cache[accept_user.id]
        else:
            await interaction.response.send_message(f"No offer found for {accept_user} by {name}. {phrase}")


async def setup(bot):
    await bot.add_cog(ActionsCog(bot))
