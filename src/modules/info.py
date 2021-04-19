# Modulo Info.py

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

    # >info
    #! Comando info
    @group()
    async def info(self, ctx, user):
        '''
        Comando info
        '''
        PREFIX = os.getenv("DISCORD_PREFIX")
        regex = re.compile(r"\<\@\!\d+\>")
        await ctx.message.delete()
        if (user == "help"):
            lines = f"""
            ```md
### COMANDO {PREFIX}info ###

Uso:
{PREFIX}info @usuario```
                """
            await ctx.channel.send(lines, delete_after=15)
        elif re.fullmatch(regex, user):
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
        
    @info.error
    async def on_command_error(self, ctx, error):
        PREFIX = os.getenv("DISCORD_PREFIX")
        if isinstance(error, MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.channel.send(f"Falta etiquetar al usuario. Para más información usar ```{PREFIX}info help```", delete_after=15)