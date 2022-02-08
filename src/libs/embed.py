from typing import Union
from discord import Colour, Embed
from discord.ext import commands

class EmbedGenerator:
    """ Embed base para generar el mensaje de ayuda. """

    def __init__(self, ctx: commands.Context):
        self._author = (f"{ctx.me.name}", f"{ctx.me.avatar}")
        self._colour = 0x00c29d

    @property
    def colour(self):
        return self._fields

    @colour.setter
    def colour(self, value):
        if isinstance(value, Union[Colour, int].__args__):
            self._colour = value
        else:
            print("Please enter a value type of Union[discord.Colour, int]")

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if isinstance(value, str):
            self._title = value
        else:
            print("Please enter a string value")

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if isinstance(value, str):
            self._description = value
        else:
            print("Please enter a string value")

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value):
        if isinstance(value, list) and len(value) > 0:
            self._fields = value
        else:
            print("Please enter a list of tuples with 2 elements")

    def generate_embed(self):
        thumbnail_url = "https://res.cloudinary.com/sebasec/image/upload/v1614807768/Fec_with_Shadow_jq8ll8.png"
        embed = Embed(title=self._title, description=self._description, color=self._colour)
        embed.set_author(name=self._author[0], icon_url=self._author[1])
        embed.set_thumbnail(url=thumbnail_url)
        for field in self._fields:
            embed.add_field(name=field[0], value=field[1], inline=False)
        return embed