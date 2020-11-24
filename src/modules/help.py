# -*- coding: utf-8 -*-

import logging

from discord.ext import commands

log = logging.getLogger(__name__)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def help(self, ctx):
        """Imprimo la ayuda general"""
        log.info('Show commands list')

    @help.command()
    async def music(self, ctx):
        """Imprimo la ayuda del comando music"""
        log.info("Show subcommand list for `music`")
