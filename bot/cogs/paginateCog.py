import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from bot.env import *
from bot.functions import *


class PaginateView(View):
    def __init__(self, user_id, bot):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.bot = bot  # Add bot instance to the view
        self.page = 0
        self.selected = 0
        self.list_names = []
        self.len_names = 0

    async def initialize(self):
        self.page, self.selected, self.list_names, self.len_names = await cache_list(self.user_id)

    async def update_embed(self, interaction):
        embed = await create_embed(self.list_names, self.len_names, self.page, self.selected, per_page=5)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="←", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't interact with this!", ephemeral=True)
            return

        if self.page > 0:
            self.page -= 1
            self.selected = 0
            await self.update_embed(interaction)

    @discord.ui.button(label="→", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't interact with this!", ephemeral=True)
            return

        if self.page < (self.len_names - 1) // 5:
            self.page += 1
            self.selected = 0
            await self.update_embed(interaction)

    @discord.ui.button(label="⊙", style=discord.ButtonStyle.success)
    async def select(self, interaction: discord.Interaction, button: Button):
        phrase = special_phrase(catch_phrase, interaction.user.id)

        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't interact with this!", ephemeral=True)
            return

        name = self.list_names[(self.page * 5) + self.selected][2:]
        folder_name = None
        try:
            item = await get_item_data(name, interaction.user.id)
            if item["message_id"] is not None:
                result = await fetch_message(item, self.bot)
                await send_message_and_embed_images(interaction, result, self.bot)
            else:
                folder_name = name
        except ValueError as ve:
            await interaction.channel.send(str(ve))
        except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
            if isinstance(e, discord.NotFound):
                await interaction.response.send_message(f"Message has been deleted. {phrase}")
            elif isinstance(e, discord.Forbidden):
                await interaction.response.send_message(f"Access forbidden to the message. {phrase}")
            else:
                await interaction.response.send_message(f"HTTP error occurred: {str(e)}\n{phrase}")

        if folder_name is not None:
            await delete_cache(self.user_id)
            self.page, self.selected, self.list_names, self.len_names = await cache_list(self.user_id, folder_name)
            await self.update_embed(interaction)

    @discord.ui.button(label="↑", style=discord.ButtonStyle.secondary)
    async def move_up(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't interact with this!", ephemeral=True)
            return

        if self.selected > 0:
            self.selected -= 1
            await self.update_embed(interaction)

    @discord.ui.button(label="↓", style=discord.ButtonStyle.secondary)
    async def move_down(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't interact with this!", ephemeral=True)
            return

        if self.selected < min(9, self.len_names - 1 - (self.page * 5)):
            self.selected += 1
            await self.update_embed(interaction)

    @discord.ui.button(label="🏠︎", style=discord.ButtonStyle.danger)
    async def reset(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't interact with this!", ephemeral=True)
            return

        await delete_cache(self.user_id)
        self.page, self.selected, self.list_names, self.len_names = await cache_list(self.user_id)
        await self.update_embed(interaction)


class PaginateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="paginate", description="Paginate through stored items.")
    async def paginate(self, interaction: discord.Interaction):
        await delete_cache(interaction.user.id)
        view = PaginateView(interaction.user.id, self.bot)
        await view.initialize()
        embed = await create_embed(view.list_names, view.len_names, view.page, view.selected, per_page=5)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(PaginateCog(bot))
