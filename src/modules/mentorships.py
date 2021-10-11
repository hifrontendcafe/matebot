# Modulo Mentorships.py
# This module is for adding/removing the Mentee role for FrontendCafé's mentorings

# ///---- Imports ----///
import re
import os
import logging

import discord
from discord.embeds import Embed
from discord.ext.commands import Cog, group, MissingRequiredArgument
from discord.ext.commands.core import has_any_role
from discord.ext.commands.errors import MissingAnyRole
import faunadb
from datetime import datetime
# Database
from libs.database import Database as DB

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
        secret = os.getenv("FAUNADB_SECRET_KEY")
        self.db = DB(secret)
        self.PREFIX = os.getenv("DISCORD_PREFIX")

    def validateDiscordUser(self, user):
        regex = re.compile(r"\<\@(\!|.)\d+\>")
        valid = re.fullmatch(regex, user)
        return valid

    # >mentee
    #! Comando mentee
    @group(invoke_without_command=True)
    @has_any_role('admin-mentors', 'Mentors')
    async def mentee(self, ctx, user, time=None, channel=None):
        '''
        Comando mentee
        '''
        await ctx.message.delete()
        if self.validateDiscordUser(user):
            userId = int(user[3:-1])
            member = await ctx.guild.fetch_member(userId)
            menteeRole = discord.utils.get(ctx.guild.roles, name="Mentees")
            if menteeRole in member.roles:
                await member.remove_roles(menteeRole)
                await ctx.channel.send(f"Rol Mentee removido a {user}", delete_after=30)
            else:
                await member.add_roles(menteeRole)
                if time is None and channel is None:
                    await ctx.channel.send(f"Rol Mentee agregado a {user}", delete_after=30)
                if time and channel is None:
                    if time == "1":
                        embed = Embed(title=f"Recordatorio",
                                      description=f"Hola {user}, {ctx.message.author.mention} te espera en {time} minuto <:fecfan:756224742771654696>", color=0x298AFF)
                        await ctx.send(embed=embed)
                    else:
                        embed = Embed(title=f"Recordatorio",
                                      description=f"Hola {user}, {ctx.message.author.mention} te espera en {time} minutos <:fecfan:756224742771654696>", color=0x298AFF)
                        await ctx.send(embed=embed)
                if time and channel:
                    if time == "1":
                        embed = Embed(title=f"Recordatorio",
                                      description=f"Hola {user}, en {time} minuto {ctx.message.author.mention} te espera en la sala de voz de {channel} <:fecfan:756224742771654696>", color=0x298AFF)
                        await ctx.send(embed=embed)
                    else:
                        embed = Embed(title=f"Recordatorio",
                                      description=f"Hola {user}, en {time} minutos {ctx.message.author.mention} te espera en la sala de voz de {channel} <:fecfan:756224742771654696>", color=0x298AFF)
                        await ctx.send(embed=embed)
        else:
            await ctx.channel.send(f"Usuario no válido, por favor etiquetar a un usuario de discord con '@'", delete_after=30)

    @mentee.error
    async def mentee_error(self, ctx, error):
        if isinstance(error, MissingAnyRole):
            await ctx.message.delete()
            await ctx.channel.send("No tienes el rol Mentors", delete_after=30)
        elif isinstance(error, MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.channel.send("Por favor, etiquetar al usuario al que desea agregar/quitar el rol Mentee", delete_after=30)
        else:
            raise error

    @mentee.command()
    @has_any_role('Mentors', 'admin-mentors')
    async def help(self, ctx):
        lines = f"""
        ```md
# COMANDO {self.PREFIX}mentee
Uso:
{self.PREFIX}mentee @usuario -> Agregar/quitar rol de Mentee.
{self.PREFIX}mentee add @usuario -> Registra una mentoría y a la vez verifica si ese usuario tiene warnings.
{self.PREFIX}mentee check @usuario -> Verifica si el usuario tiene warnings.
{self.PREFIX}mentee warn @usuario -> Dar warning a un usuario.
{self.PREFIX}mentee warn_rm @usuario -> Remover 1 warning al usuario.
{self.PREFIX}mentee warn_ls -> Exportar lista de warnings.
            ``` """
        await ctx.send(lines, delete_after=30)

    @help.error
    async def mentee_error(self, ctx, error):
        if isinstance(error, MissingAnyRole):
            await ctx.message.delete()
            await ctx.channel.send("No tienes el rol Mentors/admin-mentors", delete_after=30)
        else:
            raise error

    @mentee.command()
    @has_any_role('admin-mentors', 'Mentors')
    async def warn(self, ctx, user):
        def db_add(self, id, warned_user, warns_quantity):
            self.db.create('Mentorship_Warns', {
                "id": id,
                "warned_user": str(warned_user),
                "warns_quantity": warns_quantity
            })
        '''
        Comando mentee warn
        '''
        try:
            await ctx.message.delete()
            userId = user[3:-1]
            member = await ctx.guild.fetch_member(userId)
            mentee = self.db.get_mentee_by_discord_id(userId)
            self.db.update_with_ref(
                mentee['ref'],
                {
                    "warns_quantity": mentee['data']['warns_quantity'] + 1,
                }
            )

            # Send warn message
            embed = Embed(title=f"{member.display_name} ha sido penalizado/a",
                          description=f"Cantidad de penalizaciones: {mentee['data']['warns_quantity'] + 1}", color=0xFF6B00)
            embed.add_field(name="ID del usuario",
                            value=userId, inline=True)
            embed.set_footer(
                text=ctx.author, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

        except Exception as e:
            if type(e) is faunadb.errors.NotFound:
                db_add(self, str(member.id),
                       member.display_name, 1)
                # Send warn message
                embed = discord.Embed(title=f"{member.display_name} ha sido penalizado/a",
                                      description="Cantidad de penalizaciones: 1", color=0xFF6B00)
                embed.add_field(name="ID del usuario",
                                value=userId, inline=True)
                embed.set_footer(
                    text=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                print(e)

    @warn.error
    async def mentee_error(self, ctx, error):
        if isinstance(error, MissingAnyRole):
            await ctx.message.delete()
            await ctx.channel.send("No tienes el rol Mentors/admin-mentors", delete_after=30)
        elif isinstance(error, MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.channel.send("Por favor, etiquetar al usuario al que desea dar una advertencia.", delete_after=30)
        else:
            raise error

    @mentee.command()
    @has_any_role('Staff', 'admin-mentors')
    async def warn_rm(self, ctx, user):
        '''
        Comando mentee warn remove
        '''
        try:
            await ctx.message.delete()
            userId = user[3:-1]
            member = await ctx.guild.fetch_member(userId)
            mentee = self.db.get_mentee_by_discord_id(userId)
            if mentee['data']['warns_quantity'] > 0:
                self.db.update_with_ref(
                    mentee['ref'],
                    {
                        "warns_quantity": mentee['data']['warns_quantity'] - 1,
                    }
                )
                # Send warn message
                embed = Embed(title=f"Se ha removido una penalización a {member.display_name}",
                              description=f"Cantidad de penalizaciones: {mentee['data']['warns_quantity']-1}", color=0x00ebbc)
                embed.add_field(name="ID del usuario",
                                value=userId, inline=True)
                embed.set_footer(
                    text=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=f"{member.display_name} no tiene penalizaciones",
                                      description="Cantidad de penalizaciones: 0", color=0x00ebbc)
                embed.add_field(name="ID del usuario",
                                value=userId, inline=True)
                embed.set_footer(
                    text=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

        except Exception as e:
            if type(e) is faunadb.errors.NotFound:
                # Send warn message
                embed = discord.Embed(title=f"{member.display_name} no tiene penalizaciones",
                                      description="Cantidad de penalizaciones: 0", color=0x00ebbc)
                embed.add_field(name="ID del usuario",
                                value=userId, inline=True)
                embed.set_footer(
                    text=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                print(e)

    @warn_rm.error
    async def mentee_error(self, ctx, error):
        if isinstance(error, MissingAnyRole):
            await ctx.message.delete()
            await ctx.channel.send("No tienes el rol Staff/admin-mentors", delete_after=30)
        elif isinstance(error, MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.channel.send("Por favor, etiquetar al usuario al que desea quitar una penalización.", delete_after=30)
        else:
            raise error

    @mentee.command()
    @has_any_role('Staff', 'admin-mentors')
    async def warn_ls(self, ctx):
        '''
        Comando mentee warn list
        '''
        try:
            await ctx.message.delete()
            warned_mentees = self.db.get_all('all_warned_mentees')
            # Write file
            with open("Warnings.txt", "w") as file:
                for x in range(len(warned_mentees['data'])):
                    menteeData = warned_mentees['data'][x]
                    file.write(
                        f"ID: {menteeData['data']['id']}, Warned mentee: {menteeData['data']['warned_user']}, Warns quantity: {menteeData['data']['warns_quantity']}\n")
            # Send file
            with open("Warnings.txt", "rb") as file:
                await ctx.send("Lista:", file=discord.File(file, "Warnings.txt"))
        except Exception as e:
            print(e)

    @warn_ls.error
    async def mentee_error(self, ctx, error):
        if isinstance(error, MissingAnyRole):
            await ctx.message.delete()
            await ctx.channel.send("No tienes el rol Staff/admin-mentors", delete_after=30)
        else:
            raise error

    @mentee.command()
    @has_any_role('admin-mentors', 'Mentors')
    async def check(self, ctx, user):
        '''
        Comando mentee check
        '''
        try:
            await ctx.message.delete()
            userId = user[3:-1]
            member = await ctx.guild.fetch_member(userId)
            mentee = self.db.get_mentee_by_discord_id(userId)
            # Send message
            embed = Embed(title=f"Información de {member.display_name}",
                          description=f"Cantidad de penalizaciones: {mentee['data']['warns_quantity']}", color=0xBD00FF)
            embed.add_field(name="ID del usuario",
                            value=userId, inline=True)
            embed.set_footer(
                text=ctx.author, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

        except Exception as e:
            if type(e) is faunadb.errors.NotFound:
                # Send message
                embed = discord.Embed(title=f"Información de {member.display_name}",
                                      description="No hay datos registrados.", color=0xBD00FF)
                embed.add_field(name="ID del usuario",
                                value=userId, inline=True)
                embed.set_footer(
                    text=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                print(e)

    @check.error
    async def mentee_error(self, ctx, error):
        if isinstance(error, MissingAnyRole):
            await ctx.message.delete()
            await ctx.channel.send("No tienes el rol Mentors/admin-mentors", delete_after=30)
        elif isinstance(error, MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.channel.send("Por favor, etiquetar el usuario que desea consultar.", delete_after=30)
        else:
            raise error

    @mentee.command()
    @has_any_role('admin-mentors', 'Mentors')
    async def add(self, ctx, user):
        '''
        Comando mentee add
        '''

        def mentorship_register(self, id, author_id, author, mentee_id, mentee):
            now = datetime.now()
            self.db.create('Mentorships', {
                "id": id,
                "timestamp": now.strftime("%d/%m/%Y %H:%M:%S"),
                "author_id": author_id,
                "author": author,
                "mentee_id": mentee_id,
                "mentee": mentee,
            })

        async def success_message(self, ctx, member, userId):
            # Send message
            embed = Embed(title=f"Solicitud de mentoria exitosa",
                          description=f"¡Hola! La mentoría de {member.mention} ha sido registrada satisfactoriamente.", color=0x00ebbc)
            embed.add_field(name="ID del usuario",
                            value=userId, inline=True)
            embed.set_footer(
                text=ctx.author, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

        try:
            await ctx.message.delete()
            userId = user[3:-1]
            member = await ctx.guild.fetch_member(userId)
            mentee = self.db.get_mentee_by_discord_id(userId)

            if mentee['data']['warns_quantity'] > 0:
                staffRole = discord.utils.get(ctx.guild.roles, name="Staff")
                # Send message
                embed = Embed(title=f"Solicitud de mentoría rechazada",
                              description=f"¡Hola! {member.mention} la mentoría no se llevara a cabo ya que anteriormente has sido penalizado por no cumplir el código de conducta. Si crees que fue un error, comunícate con {staffRole.mention}.", color=0xFF006B)
                embed.add_field(name="ID del usuario",
                                value=userId, inline=True)
                embed.set_footer(
                    text=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
                await ctx.send(f"{ctx.author.mention} recordá que debes cancelar la mentoría via Calendly.", delete_after=30)
            else:
                mentorship_register(
                    self, userId, ctx.message.author.id, ctx.message.author.display_name, userId, member.display_name)
                # Send message
                await success_message(self, ctx, member, userId)

        except Exception as e:
            if type(e) is faunadb.errors.NotFound:
                # Send message
                mentorship_register(
                    self, userId, ctx.message.author.id, ctx.message.author.display_name, userId, member.display_name)
                # Send message
                await success_message(self, ctx, member, userId)
            else:
                print(e)

    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, MissingAnyRole):
            await ctx.message.delete()
            await ctx.channel.send("No tienes el rol Mentors/admin-mentors", delete_after=30)
        elif isinstance(error, MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.channel.send("Por favor, etiquetar el usuario al que desea registrar para una mentoría.", delete_after=30)
        else:
            raise error
