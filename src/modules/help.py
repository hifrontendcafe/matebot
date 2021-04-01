# -*- coding: utf-8 -*-

import os
import logging

import discord
from discord.ext import commands

log = logging.getLogger(__name__)

class Help(commands.Cog):
    def __init__(self, bot):
        pass

    @commands.group()
    async def help(self, ctx):
        """Imprimo la ayuda general"""

        if ctx.invoked_subcommand is not None:
            return

        log.info('General Help')

        PREFIX = os.getenv("DISCORD_PREFIX")

        author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
        title = f"Ayuda General"
        description = f"Lista de comandos disponibles.\nPara mas ayuda escriba: `{PREFIX}help <comando>`"
        thumbnail_url = "https://res.cloudinary.com/sebasec/image/upload/v1614807768/Fec_with_Shadow_jq8ll8.png"
        fields = [
            (f"{PREFIX}faq", "Información sobre FAQs."),
            (f"{PREFIX}sched", "Genera un recordatorio que se emite de forma automática con las siguientes frecuencias:\n\
            - 1 día antes del evento.\n\
            - 1 hora antes del evento.\n\
            - 10 minutos antes del evento."),
            (f"{PREFIX}poll", "Genera una interfase con botones para poder realizar encuestas y votaciones."),
            (f"{PREFIX}search", "Hace busquedas en la web y muestra los resultados.")
        ]

        embed = embed_generator(author, title, description, thumbnail_url, fields)
        await ctx.send(embed=embed, delete_after=60)

    @help.command()
    async def faq(self, ctx):
        """Imprimo la ayuda del comando faq"""

        log.info("FAQ Help")
        PREFIX = os.getenv("DISCORD_PREFIX")

        author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
        title = f"Ayuda del comando: `faq`"
        description = "Preguntas más frecuentes sobre el uso de FrontEndCafe Discord Server."
        thumbnail_url = "https://res.cloudinary.com/sebasec/image/upload/v1614807768/Fec_with_Shadow_jq8ll8.png"
        fields = [
            (f"{PREFIX}faq all", "Por DM se recibe el FAQ completo."),
            (f"{PREFIX}faq general", "Preguntas generales sobre el uso de Discord y el servidor."),
            (f"{PREFIX}faq english", "Preguntas relacionadas a los eventos para charlar en inglés."),
            (f"{PREFIX}faq mentoring", "Dudas sobre el sistema de mentorías."),
            (f"{PREFIX}faq coworking", "¿Qué es el Coworking en FEC?"),
            (f"{PREFIX}faq roles", "Que són y cómo se obtienen los roles."),
            (f"{PREFIX}faq projects", "Consulta sobre los proyectos grupales de desarrollo."),
            (f"{PREFIX}faq studygroup", "Consulta sobre los grupos de estudio.")
        ]

        embed = embed_generator(author, title, description, thumbnail_url, fields)
        await ctx.send(embed=embed, delete_after=60)


def embed_generator(author, title, description, thumbnail_url, fields):
        embed = discord.Embed(title=title, description=description, color=0x00c29d)
        embed.set_author(name=author[0], icon_url=author[1])
        embed.set_thumbnail(url=thumbnail_url)
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=False)

        return embed
