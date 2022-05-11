# -*- coding: utf-8 -*-

# DEPRECATED 😭

import os
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

import discord
from discord.ext import commands
from TwitterAPI import TwitterAPI

log = logging.getLogger(__name__)

class Events(commands.Cog):
    """Módulo Events

    Se encarga de emitir en un canal específico de discord los tweets
    publicados de forma automática en real time
    """
    def __init__(self, bot):
        self.bot = bot

        # Defino un canal especifico para publicar los avisos
        self.events_channel_id = int(os.getenv("EVENTS_CHANNEL_ID"))

        # Se obtienen los valores correspondientes para la autenticación
        consumer_key = os.getenv("TWITTER_API_KEY")
        consumer_secret = os.getenv("TWITTER_API_SECRET")
        access_key = os.getenv("TWITTER_ACCESS_KEY")
        access_secret = os.getenv("TWITTER_ACCESS_SECRET")

        self.user_url = os.getenv("TWITTER_USER_URL")
        self.user_id = os.getenv("TWITTER_USER_ID")
        self.search = os.getenv("TWITTER_FILTER")

        self.loop = asyncio.get_event_loop()
        self.twitter = TwitterStream(consumer_key, consumer_secret, access_key,
                                     access_secret, self.discord_post, loop=self.loop)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.twitter.start(self.user_id, self.user_url, self.search)

    async def discord_post(self, url):
        # Publica el tweet con un mesanje @everyone
        log.info("Twitter post")
        msg = "@everyone"
        channel = self.bot.get_channel(self.events_channel_id)
        await channel.send(f"{msg} {url}")

class TwitterStream:
    def __init__(self, consumer_key, consumer_secret, access_key, access_secret, external_func, loop):
        self.api = TwitterAPI(consumer_key, consumer_secret, access_key, access_secret)
        self.external_func = external_func
        self.loop = loop

        self.user_id = ""
        self.user_url = ""
        self.search = ""

    async def start(self, user_id, user_url, search):
        self.user_id = user_id
        self.user_url = user_url
        self.search = search
        await self.loop.run_in_executor(ThreadPoolExecutor(), self.on_message)

    def on_message(self):
        while True:
            try:
                req = self.api.request('statuses/filter', {
                    'follow': [self.user_id],
                    #'track': [self.search]
                })
                for item in req:
                    print("ENTRO A TWITTER")
                    print(item)
                    hashtags = None
                    if item.get('entities', {}).get('hashtags'):
                        hashtags = set(t.get('text', {}) for t in item.get('entities', {}).get('hashtags'))
                    elif item.get('extended_tweet', {}).get('entities', {}).get('hashtags', {}):
                        hashtags = set(t.get('text', {}) for t in item.get('extended_tweet', {}).get('entities', {}).get('hashtags', {}))
                    else:
                        continue
                    if self.search in hashtags:
                        url_tweet = f"{self.user_url}/status/{item['id']}"
                        self.send_message(url_tweet)
            except:
                continue

    def send_message(self, msg):
        asyncio.run_coroutine_threadsafe(
            self.external_func(msg),
            self.loop
        )
