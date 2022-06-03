# Modulo Info.py

# Disabled module

# ///---- Imports ----///
import re
import os
import logging

import discord
from discord.ext.commands import Cog, group, MissingRequiredArgument

# ///---- Log ----///
log = logging.getLogger(__name__)


# ///---- Clase ----///
class Info(Cog):
    '''
    Spamear info a los usuarios que no leen
    '''

    def __init__(self, bot):
        '''
        __init__ del bot (importa este codigo como modulo al bot)
        '''
        self.bot = bot
        self.PREFIX = os.getenv("DISCORD_PREFIX")

    def validateDiscordUser(self, user):
        regex = re.compile(r"\<\@(\!|.)\d+\>")
        valid = re.fullmatch(regex, user)
        return valid

    # >info
    #! Comando info
    @group()
    async def info(self, ctx):
        '''
        Comando info
        '''
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            lines = f"""
    Para más información usar ```{self.PREFIX}info help```
                    """
            await ctx.send(lines, delete_after=15)
        
    #! Subcomando help 
    @info.command()
    async def help(self, ctx):
        lines = f"""
            ```md
### COMANDO {self.PREFIX}info ###

Uso:
{self.PREFIX}info q @usuario -> Información sobre como realizar consultas
{self.PREFIX}info m @usuario -> Información sobre bots de música```
                """
        await ctx.send(lines, delete_after=15)
    #! Subcomando question
    @info.command()
    async def q(self, ctx, user):
        if self.validateDiscordUser(user):
            lines = f"""Hola {user}, te dejamos algunos tips para realizar tu pregunta```md
1. No pidas ayuda consultando si alguien puede ayudarte, simplemente inicia tu consulta.
2. Danos contexto, contanos que estas tratando de hacer en mensaje corto (280 caracteres).
3. Si es un error, decinos el detalle del error. 
4. Un screenshot o el código en un editor online como Codepen (https://codepen.io/) es ideal.
5. Si deseas compartir el código en el mensaje envuélvelo siempre en triple comilla invertida (`).
6. Contanos qué has intentado y qué no te funcionó.
```Para más información pasate por <#747925827265495111>
                    """
            await ctx.channel.send(lines)
        else:
            await ctx.channel.send(f"Usuario no válido, por favor etiquetar a un usuario de discord con '@'", delete_after=15)

    @q.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.channel.send(f"Falta etiquetar al usuario. Para más información usar ```{self.PREFIX}info help```", delete_after=15)

    #! Subcomando music
    @info.command()
    async def m(self, ctx, user):
        if self.validateDiscordUser(user):
            lines = f"""Hola {user} los comandos de los bots de música se tipean en <#831126698006937620> para evitar el spam en el resto de los canales."""
            await ctx.channel.send(lines)
        else:
            await ctx.channel.send(f"Usuario no válido, por favor etiquetar a un usuario de discord con '@'", delete_after=15)

    @m.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.channel.send(f"Falta etiquetar al usuario. Para más información usar ```{self.PREFIX}info help```", delete_after=15)
        