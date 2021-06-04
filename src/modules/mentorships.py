# Modulo Mentorships.py
# This module is for adding/removing the Mentee role for FrontendCafé's mentorings

# ///---- Imports ----///
import re
import os
import logging

import discord
from discord.ext.commands import Cog, group, MissingRequiredArgument, has_role
from discord.ext.commands.errors import MissingRole

# ///---- Log ----///
log = logging.getLogger(__name__)


# ///---- Clase ----///
class Mentorship(Cog):
    '''
    Agregar/quitar rol de mentee
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

    # >mentee
    #! Comando mentee
    @group()
    @has_role('Mentors')
    async def mentee(self, ctx, user):
        '''
        Comando mentee
        '''
        await ctx.message.delete()
        if user == "help":
            lines = f"""
            ```md
# COMANDO {self.PREFIX}mentee
Uso:
{self.PREFIX}mentee @usuario -> Agregar/quitar rol de Mentee
               ``` """
            await ctx.send(lines, delete_after=15)

        elif self.validateDiscordUser(user):
            userId = int(user[3:-1])
            member = await ctx.guild.fetch_member(userId)
            menteeRole = discord.utils.get(ctx.guild.roles, name="Mentee")
            if menteeRole in member.roles:
                await member.remove_roles(menteeRole)
                await ctx.channel.send(f"Rol Mentee removido a {user}", delete_after=15)
            else:
                await member.add_roles(menteeRole)
                await ctx.channel.send(f"Rol Mentee agregado a {user}", delete_after=15)
        else:
            await ctx.channel.send(f"Usuario no válido, por favor etiquetar a un usuario de discord con '@'", delete_after=15)

    @mentee.error
    async def mentee_error(self, ctx, error):
        if isinstance(error, MissingRole):
            await ctx.message.delete()
            await ctx.channel.send("No tienes el rol Mentors", delete_after=15)
        elif isinstance(error, MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.channel.send("Por favor, etiquetar al usuario al que desea agregar/quitar el rol Mentee", delete_after=15)
        else:
            raise error
