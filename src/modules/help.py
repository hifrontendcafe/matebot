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
            # (f"{PREFIX}reminder", "Genera un recordatorio que se emite de forma automática con las siguientes frecuencias:\n\
            # - 1 día antes del evento.\n\
            # - 1 hora antes del evento.\n\
            # - 10 minutos antes del evento."),
            (f"{PREFIX}poll", "Genera una interfase con botones para poder realizar encuestas y votaciones."),
            # (f"{PREFIX}search", "Hace busquedas en la web y muestra los resultados.")
        ]

        embed = h.generate_embed()
        await ctx.send(embed=embed, delete_after=60)
