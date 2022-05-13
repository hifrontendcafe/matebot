# -*- coding: utf-8 -*-

import os
import logging
from typing import Union

from discord import Colour, Embed
from discord.ext import commands

from libs.embed import EmbedGenerator

log = logging.getLogger(__name__)


class Help(commands.Cog):

    @commands.group()
    async def help(self, ctx):
        """Imprimo la ayuda general"""

        await ctx.message.delete()
        if ctx.invoked_subcommand is not None:
            return

        log.info('General Help')

        PREFIX = os.getenv("DISCORD_PREFIX")

        h = EmbedGenerator()
        h.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
        h.title = f"Ayuda General"
        h.description = f"Lista de comandos disponibles.\nPara mas ayuda escriba: `{PREFIX}help <comando>`"
        h.fields = [
            (f"{PREFIX}poll", "Genera una flujo interactivo de mensajes con reacciones para poder realizar encuestas y votaciones."),
            (f"{PREFIX}reminder", "Genera una flujo interactivo de mensajes con reacciones para poder realizar recordatorios."),
            (f"{PREFIX}help", "Imprime esta ayuda."),
        ]

        embed = h.generate_embed()
        await ctx.send(embed=embed, delete_after=60)
