# -*- coding: utf-8 -*-

import os
import logging
import requests

import discord
from discord.ext import commands
from bs4 import BeautifulSoup


log = logging.getLogger(__name__)


class Search(commands.Cog):
    """Módulo para hacer busquedas en la web."""

    def __init__(self, bot):
        pass

    @commands.command()
    async def search(self, ctx, *query):
        """Comando search

        Busca y muestra resultados de la web.
        """

        query = " ".join(query)
        log.info(f"Search: {query}")

        search_engine = DuckDuckGoSearch()
        data = await search_engine.search(query)

        # Mando un aviso si no obtengo resultados
        if data is []:
            await ctx.send("No se encontraron resultados, por favor intente con otra query", delete_after=60)
            return

        embed = discord.Embed(title="Busquedas Web", description=f"Resultados para: `{query}`", color=0x00c29d)
        embed.set_thumbnail(url="https://i.postimg.cc/HWSB3vvv/fec-search-icon-256.png")

        for d in data:
            embed.add_field(name=d[0], value=d[1], inline=False)

        await ctx.send(embed=embed, delete_after=60)


class DuckDuckGoSearch:
    def __init__(self):
        self.url = "https://html.duckduckgo.com/html/?q="

    async def search(self, query, num=5):
        res = requests.get(self.url + "".join(query), headers={'user-agent': 'matebot/0.0.1'})
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        elements = soup.find_all("div", attrs={"class": "result results_links results_links_deep web-result"})

        result = []
        for i, e in enumerate(elements):
            if i > num:
                break

            try:
                title = e.find("a", attrs={"class": "result__a"})
                link = e.find("a", attrs={"class": "result__url"})
                title = title.text.strip()
                link = link.text.strip()

                if title == "" or link == "":
                    continue

                result.append((title, "https://" + link))

            except:
                continue

        return result
