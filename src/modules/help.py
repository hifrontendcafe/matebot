# -*- coding: utf-8 -*-

import os
import logging
from typing import Union

from discord import Colour, Embed
from discord.ext import commands

log = logging.getLogger(__name__)

class EmbedGenerator:
    """ Embed base para generar el mensaje de ayuda. """

    def __init__(self, ctx: commands.Context):
        self._author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
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


class Help(commands.Cog):

    @commands.group()
    async def help(self, ctx):
        """Imprimo la ayuda general"""

        await ctx.message.delete()
        if ctx.invoked_subcommand is not None:
            return

        log.info('General Help')

        PREFIX = os.getenv("DISCORD_PREFIX")

        h = EmbedGenerator(ctx)
        h.title = f"Ayuda General"
        h.description = f"Lista de comandos disponibles.\nPara mas ayuda escriba: `{PREFIX}help <comando>`"
        h.fields = [
            (f"{PREFIX}faq", "Información sobre FAQs."),
            (f"{PREFIX}sched", "Genera un recordatorio que se emite de forma automática con las siguientes frecuencias:\n\
            - 1 día antes del evento.\n\
            - 1 hora antes del evento.\n\
            - 10 minutos antes del evento."),
            (f"{PREFIX}poll", "Genera una interfase con botones para poder realizar encuestas y votaciones."),
            (f"{PREFIX}search", "Hace busquedas en la web y muestra los resultados.")
        ]

        embed = h.generate_embed()
        await ctx.send(embed=embed, delete_after=60)

    @help.command()
    async def faq(self, ctx):
        """Imprimo la ayuda del comando faq"""

        log.info("FAQ Help")
        PREFIX = os.getenv("DISCORD_PREFIX")

        h = EmbedGenerator(ctx)
        h.title = f"Ayuda del comando: `faq`"
        h.description = "Preguntas más frecuentes sobre el uso de FrontEndCafe Discord Server."
        h.fields = [
            (f"{PREFIX}faq all", "Por DM se recibe el FAQ completo."),
            (f"{PREFIX}faq general", "Preguntas generales sobre el uso de Discord y el servidor."),
            (f"{PREFIX}faq english", "Preguntas relacionadas a los eventos para charlar en inglés."),
            (f"{PREFIX}faq mentoring", "Dudas sobre el sistema de mentorías."),
            (f"{PREFIX}faq coworking", "¿Qué es el Coworking en FEC?"),
            (f"{PREFIX}faq roles", "Que són y cómo se obtienen los roles."),
            (f"{PREFIX}faq projects", "Consulta sobre los proyectos grupales de desarrollo."),
            (f"{PREFIX}faq studygroup", "Consulta sobre los grupos de estudio.")
        ]

        embed = h.generate_embed()
        await ctx.send(embed=embed, delete_after=60)
