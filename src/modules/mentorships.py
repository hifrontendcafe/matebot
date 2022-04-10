# Modulo Mentorships.py
# This module is for adding/removing the Mentee role for FrontendCafé's mentorings

# ///---- Imports ----///
import re
import os
import logging
import requests

import discord
from discord.embeds import Embed
from discord.ext.commands import Cog, group, MissingRequiredArgument
from discord.ext.commands.core import has_any_role
from discord.ext.commands.errors import MissingAnyRole
import faunadb
from datetime import datetime
# Database
from libs.database import Database as DB
from modules.help import EmbedGenerator

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
        self.AWS_URL = os.getenv("AWS_URL")
        self.AWS_HEADERS = {'x-api-key': os.getenv("AWS_API_KEY")}

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
            userId = re.search(r'\d+', user).group()
            member = await ctx.guild.fetch_member(userId)
            menteeRole = discord.utils.get(ctx.guild.roles, name="Mentees")

            if menteeRole in member.roles and time is None and channel is None:
                await member.remove_roles(menteeRole)
                message = f"""
> :pray: {user} esperamos que hayas tenido una buena experiencia, recuerda darnos feedback para continuar mejorando!
> https://go.frontend.cafe/feedback
"""
                await ctx.channel.send(message)

            else:
                await member.add_roles(menteeRole)
                if time is None and channel is None:
                    await ctx.channel.send(f"Rol Mentee agregado a {user}", delete_after=30)
                if time and channel is None:
                    message = f"""
> :alarm_clock:  **Recordatorio**
> Hola {user}, {ctx.message.author.mention} te espera en {time} minuto{"" if time == "1" else "s"} <:fecfan:756224742771654696>
"""
                    await ctx.channel.send(message)
                if time and channel:
                    message = f"""
> :alarm_clock:  **Recordatorio**
> Hola {user}, en {time} minuto{"" if time == "1" else "s"} {ctx.message.author.mention} te espera en la sala de voz de {channel} <:fecfan:756224742771654696>
"""
                    await ctx.channel.send(message)
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
        """Imprimo embed con los comandos de `mentee`"""
        PREFIX = self.PREFIX

        await ctx.message.delete()

        log.info('Mentee Help')

        h = EmbedGenerator(ctx)
        h.title = f"Mentee: comandos"
        h.description = f"Lista de comandos para {PREFIX}mentee"
        h.fields = [
            (f"{PREFIX}mentee @usuario", "Agregar/quitar rol de Mentee."),
            (f"{PREFIX}mentee add @usuario",
             "Registra una mentoría y a la vez verifica si ese usuario tiene warnings."),
            (f"{PREFIX}mentee check @usuario",
             "Verifica si el usuario tiene warnings."),
            (f"{PREFIX}mentee warn @usuario",
             'Dar warning a un usuario con motivo "Ausencia a la mentoría"'),
            (f"{PREFIX}mentee warn @usuario <motivo>",
             f'Dar warning a un usuario con motivo personalizado. Ejemplo:\n`{PREFIX}mentee warn @usuario Llegada tarde y falta de respeto`'),
            (f"{PREFIX}mentee warn_rm @usuario",
             "Remover 1 warning al usuario."),
            (f"{PREFIX}mentee warn_ls", "Exportar lista de warnings.")
        ]

        embed = h.generate_embed()

        await ctx.send(embed=embed, delete_after=60)

    @help.error
    async def mentee_error(self, ctx, error):
        if isinstance(error, MissingAnyRole):
            await ctx.message.delete()
            await ctx.channel.send("No tienes el rol Mentors/admin-mentors", delete_after=30)
        else:
            raise error

    @mentee.command()
    @has_any_role('admin-mentors', 'Mentors')
    async def warn(self, ctx, user, *reason):
        if self.validateDiscordUser(user):
            userId = int(re.search(r'\d+', user).group())
            member = await ctx.guild.fetch_member(userId)
            menteeRole = discord.utils.get(ctx.guild.roles, name="Mentees")
            await member.remove_roles(menteeRole)

            def db_add(self, id, warned_user, warns_quantity, history):
                self.db.create('Mentorship_Warns', {
                    "id": id,
                    "warned_user": str(warned_user),
                    "warns_quantity": warns_quantity,
                    "history": history,
                })
            '''
            Comando mentee warn
            '''

            reason = " ".join(reason)
            now = datetime.now()
            history_content = {
                "timestamp": now.strftime("%d/%m/%Y %H:%M:%S"),
                "reason": reason
            }

            try:
                await ctx.message.delete()
                userId = int(re.search(r'\d+', user).group())
                member = await ctx.guild.fetch_member(userId)
                mentee = self.db.get_mentee_by_discord_id(userId)
                history = mentee['data']['history']

                # if the field doesn't exist, I add it
                if history is None:
                    history = [history_content]
                else:
                    history.append(history_content)

                self.db.update_with_ref(
                    mentee['ref'],
                    {
                        "warns_quantity": mentee['data']['warns_quantity'] + 1,
                        "history": history,
                    }
                )

                # Send warn message
                message = f"""
> :triangular_flag_on_post:  **{member.mention} ha sido penalizado/a**
> Cantidad de penalizaciones: **{mentee['data']['warns_quantity'] + 1}**
> ⠀
> _**Motivo**: {"Ausencia a la mentoria" if not reason else reason}_
> _**Fecha**: {now.strftime("%d/%m/%Y")}_
> ⠀
> _ID del usuario: {userId}_
> ⠀
> `{ctx.author}`
"""
                await ctx.channel.send(message)

                # embed = Embed(title=f"{member.display_name} ha sido penalizado/a",
                #               description=f"Cantidad de penalizaciones: {mentee['data']['warns_quantity'] + 1}", color=0xFF6B00)
                # embed.add_field(name="ID del usuario",
                #                 value=userId, inline=True)
                # embed.set_footer(
                #     text=ctx.author, icon_url=ctx.author.avatar_url)
                # await ctx.send(embed=embed)

            except Exception as e:
                if type(e) is faunadb.errors.NotFound:
                    history = [history_content]
                    db_add(self, str(member.id),
                           member.display_name, 1, history)

                    # Send warn message
                    message = f"""
> :triangular_flag_on_post:  **{member.mention} ha sido penalizado/a**
> Cantidad de penalizaciones: **1**
> ⠀
> _**Motivo**: {"Ausencia a la mentoria" if not reason else reason}_
> _**Fecha**: {now.strftime("%d/%m/%Y")}_
> ⠀
> _ID del usuario: {userId}_
> ⠀
> `{ctx.author}`
"""

                    await ctx.channel.send(message)

                    # embed = discord.Embed(title=f"{member.display_name} ha sido penalizado/a",
                    #                       description="Cantidad de penalizaciones: 1", color=0xFF6B00)
                    # embed.add_field(name="ID del usuario",
                    #                 value=userId, inline=True)
                    # embed.set_footer(
                    #     text=ctx.author, icon_url=ctx.author.avatar_url)
                    # await ctx.send(embed=embed)
                else:
                    print(e)
        else:
            await ctx.channel.send(f"Usuario no válido, por favor etiquetar a un usuario de discord con '@'", delete_after=30)

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
    async def warn_rm(self, ctx, user, *forgive_cause):
        '''
        Comando mentee warn remove
        '''
        AWS_URL = self.AWS_URL
        AWS_HEADERS = self.AWS_HEADERS

        async def success_message(ctx, member, userId):
            message = f"""
    > :point_right:  **Se ha removido la penalización a {member.mention}**
    > ⠀
    > _ID del usuario: {userId}_
    > ⠀
    > `{ctx.author}`
    """
            await ctx.channel.send(message)

        async def no_warnings_message(ctx, member, userId):
            message = f"""
> :ballot_box_with_check:  **{member.mention} no tiene penalizaciones**
> ⠀
> _ID del usuario: {userId}_
> ⠀
> `{ctx.author}`
"""
            await ctx.channel.send(message)

        async def error_message(ctx, userId):
            adminMentorsRole = discord.utils.get(
                ctx.guild.roles, name="admin-mentors")
            message = f"""
> :warning:  **Error**
> ¡Hola! Ocurrió un problema al intentar remover la penalización por favor, comunícate con {adminMentorsRole.mention}.
> ⠀
> _ID del usuario: {userId}_
"""
            await ctx.channel.send(message)

        try:
            await ctx.message.delete()
            userId = int(re.search(r'\d+', user).group())
            member = await ctx.guild.fetch_member(userId)
            request = requests.patch(f'{AWS_URL}/warning/mentee/{str(userId)}', headers=AWS_HEADERS, json={
                "forgive_cause": ' '.join(forgive_cause) if forgive_cause else 'Sin motivo',
                "forgive_author_id": ctx.message.author.id,
                "forgive_author_username_discord": ctx.message.author.display_name
            })
            response = request.json()

            if response['code'] == "303":
                await success_message(ctx, member, userId)
            elif response['code'] == "301":
                await no_warnings_message(ctx, member, userId)
            else:
                await error_message(ctx, userId)
        except Exception as e:
            print(e)
            await error_message(ctx, userId)

    @warn_rm.error
    async def mentee_error(self, ctx, error):
        if isinstance(error, MissingAnyRole):
            await ctx.message.delete()
            await ctx.channel.send("No tienes el rol Staff/admin-mentors", delete_after=30)
        elif isinstance(error, MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.channel.send("Por favor, etiquetar al usuario al que desea quitar una penalización y el motivo.", delete_after=30)
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
            userId = int(re.search(r'\d+', user).group())
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
        AWS_URL = self.AWS_URL
        AWS_HEADERS = self.AWS_HEADERS
        '''
        Comando mentee add
        '''
        async def rejected_message(ctx, member, userId):
            adminMentorsRole = discord.utils.get(
                ctx.guild.roles, name="admin-mentors")
            message = f"""
> :no_entry:  **Solicitud de mentoría rechazada**
> ¡Hola! {member.mention} la mentoría no se llevara a cabo ya que anteriormente has sido penalizado por no cumplir el código de conducta. Si crees que fue un error, comunícate con {adminMentorsRole.mention}.
> ⠀
> _ID del usuario: {userId}_
"""
            await ctx.channel.send(message)

        async def success_message(ctx, member, userId):
            message = f"""
> :white_check_mark:  **Solicitud de mentoría exitosa**
> ¡Hola! La mentoría de {member.mention} ha sido registrada satisfactoriamente.
> Tu mentor asignado es {ctx.message.author.mention}
> ⠀
> _ID del usuario: {userId}_
"""
            await ctx.channel.send(message)

        async def error_message(ctx, userId):
            adminMentorsRole = discord.utils.get(
                ctx.guild.roles, name="admin-mentors")
            message = f"""
> :warning:  **Error**
> ¡Hola! Ocurrió un problema al registrar al mentoría por favor, comunícate con {adminMentorsRole.mention}.
> ⠀
> _ID del usuario: {userId}_
"""
            await ctx.channel.send(message)

        try:
            await ctx.message.delete()
            userId = int(re.search(r'\d+', user).group())
            member = await ctx.guild.fetch_member(userId)
            request = requests.post(f'{AWS_URL}/matebot/mentorship', headers=AWS_HEADERS, json={
                "mentor_id": str(ctx.message.author.id),
                "mentor_username_discord": ctx.message.author.display_name,
                "mentee_id": str(userId),
                "mentee_username_discord": member.display_name})
            response = request.json()

            if response['code'] == "-118":
                await rejected_message(ctx, member, userId)
            elif response['code'] == "100":
                await success_message(ctx, member, userId)
            else:
                await error_message(ctx, member, userId)
        except Exception as e:
            print('error', e)
            await error_message(ctx, member, userId)

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
