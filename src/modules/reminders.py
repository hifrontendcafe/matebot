# Módulo Reminders

import os
import re
import logging
import dateparser
import discord
from discord.ext import commands
from discord import Embed, Color, Interaction
import faunadb
from datetime import datetime as dt
from libs.database import Database as DB
from utils.buttons import btns_confirm
from utils.selects import selects_day
from utils.errors import Error

log = logging.getLogger(__name__)


class Reminders(commands.Cog):
    """
    Recordatorios. Los parámetros a pasar serían:\n
\t- Día/Días\n
\t- Horario en gmt-3 (Un mismo horario para todos los días)\n
\t- Canal\n
\t- Mensaje\n
    """
    def __init__(self, bot):
        self.bot = bot
        secret = os.getenv("FAUNADB_SECRET_KEY")
        self.db = DB(secret)
        self.PREFIX = os.getenv("DISCORD_PREFIX")
        self.new_reminder = {
            'days': [],
            'time': '',
            'channel': '',
            'message': '',
        }
        self.step = 0
        self.days = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Sábado': 'Saturday',
            'Sunday': 'Domingo'
        }   

    @staticmethod
    def _process_channel(channel):
        match = re.search(r"\<\#(\d+)\>", channel)
        if match:
            channel_id = int(match.group(1))
            return channel_id
        else:
            return Error.CHANNEL

    @commands.group()
    async def reminder(self, ctx):
        """
        Comando reminder
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Este comando no existe! Tipea `{self.PREFIX}reminder` para ver los comandos disponibles :)")


    @reminder.command()
    async def help(self, ctx):
        """
        Sarasa
        """

        await ctx.send("Ayudín")

    
    @reminder.command()
    async def add(self, ctx):
        async def days(self, ctx):
            def check_selection(i: Interaction, select_menu):
                return i.author == ctx.author and i.message == msg

            msg = await ctx.send(
                'Selecciona los días! Cuando hagas clic afuera de la selección, se tomarán las respuestas',
                components=[[ selects_day() ]],
                delete_after=180 # TODO: Cambiar por eliminación por evento disparado de los botones 
            )

            interaction, select_menu = await self.bot.wait_for('selection_select', check=check_selection)

            embed = Embed(
                title='Días seleccionados:',
                description=f'El recordatorio será para los días '+', '.join([f'{self.days[v]}' for v in select_menu.values]),
                color=Color.random()
            )

            # TODO: Cambiar por eliminación por evento disparado de los botones 
            msg = await interaction.respond(embed=embed, components=btns_confirm(), delete_after=180)
            interaction, button = await self.bot.wait_for('button_click', check=check_selection)
            await interaction.defer()

            if button.custom_id == 'continue':
                self.step = 1
                self.new_reminder['days'] = select_menu.values
    

        async def t_event(self, ctx):
            def check_entry(author):
                def inner_check(message):
                    return message.author == author
                return inner_check

            await ctx.send('¿A qué hora (en GMT-3) se deberá publicar el recordatorio? Presione "Continuar" para avanzar', delete_after=180)
            msg = await self.bot.wait_for('message', check=check_entry(ctx.author))
            dtime = dateparser.parse(msg.content)
            if dtime != None:
                self.step = 2
                self.new_reminder['time'] = dtime.time()


        async def ch_event(self, ctx):
            def check_entry(author):
                def inner_check(message):
                    return message.author == author
                return inner_check
            
            await ctx.send('¿En qué canal quieres publicar el recordatorio?', delete_after=180)
            msg = await self.bot.wait_for('message', check=check_entry(ctx.author))
            channel_id = self._process_channel(msg.content)
            if channel_id is Error.CHANNEL:
                embed = Embed(
                    title="Error",
                    description="Por favor, elija un canal válido.",
                    color=discord.Colour.green().value
                )
                return await ctx.send(embed=embed, delete_after=60)
            else:
                self.step = 3
                self.new_reminder['channel'] = f'<#{channel_id}>'

        await days(self, ctx)
        await ctx.send(str(self.new_reminder['days']))

        await t_event(self, ctx)
        await ctx.send(str(self.new_reminder['time']))

        await ch_event(self, ctx)
        await ctx.send(str(self.new_reminder['channel']))

        embed = Embed(
            title="Nuevo recordatorio",
            description="Sarasa",
            color=discord.Colour.green().value
        )

        for key in self.new_reminder.keys():
            if key != 'message':
                embed.add_field(name=key, value=self.new_reminder[key], inline=True)
        embed.set_footer(text="Los datos son correctos?")

        await ctx.send(embed=embed, delete_after=600)