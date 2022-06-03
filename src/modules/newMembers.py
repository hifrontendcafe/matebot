'''
Módulo para darle la bienvenida a los nuevos miembros de FrontendCafé
Los mensajes de bienvenida se eliminan luego de una hora
'''

# ///---- Imports ----///
import logging
import random
import os
from time import time
from discord.ext import commands
from libs.database import Database as DB

#///---- Log ----///
log = logging.getLogger(__name__)


class NewMembers(commands.Cog):
    '''
    Saludo de bienvenida al server
    '''
    def __init__(self, bot):
        '''
        __init__ del bots
        '''
        secret = os.getenv("FAUNADB_SECRET_KEY")
        self.bot = bot
        self.db = DB(secret)
        self.get_list()
        self.channel_test = 861980330201841686
        self.channel_cafe = 594935077637718027
        self.channel_manual = 747925827265495111
        self.guild_id = 594363964499165194


    def get_list(self):
        '''
        Descripción: Obtiene la lista de usuarios nuevos y otros parámetros para análisis
        Precondición: Debe existir la colección con el documento
        Poscondición: Se obtiene la lista de usuarios nuevos, la condición de usuarios nuevos, el tiempo de inicio y el tiempo de espera
        '''
        try:
            doc = self.db.get('Users', '292960205647380995')["data"]
            return (doc)
        except Exception as error:
            print(f'Hubo un error en get_list: {error}')


    def update_list(self, list_users: list, users: int, time_zero: float, delta: float):
        '''
        Descripción: Actualiza la lista de usuarios nuevos, la condición de usuarios nuevos y el tiempo de espera
        Precondición: Debe existir la colección con el documento
        Poscondición: La lista de usuarios nuevos, la condición de usuarios nuevos y el tiempo de espera se actualizan
        '''
        try:
            self.db.update('Users', '292960205647380995', {
                "new_users_id": list_users,
                "user_condition": users,
                "time_sec": time_zero,
                "time_delta": delta
            })
        except Exception as error:
            print(f'Hubo un error en update_list: {error}')


    @commands.Cog.listener()
    async def on_member_join(self, member):
        '''
        Descripción: Se activa cuando un nuevo usuario entra al servidor y se guarda su id en la base de datos
        Precondición: Debe existir la colección con el documento
        Poscondición: Se activa el mensaje de bienvenida a los nuevos miembros de FrontendCafé al alcanzar el número de usuarios necesarios
        '''
        new_member = member.mention
        package = self.get_list()
        list_users, users, time_zero, delta = package["new_users_id"], package["user_condition"], package["time_sec"], package["time_delta"]
        new_users = []
        impostor = '<:fecimpostor:755971090471321651>'
        fec_star = '<:fecstar:755451362950512660>'

        list_users.append(new_member)
        
        if (len(list_users) == users):
            guild = self.bot.get_guild(self.guild_id)
            time_final = time()
            new_delta = time_final - time_zero

            if (delta < new_delta) and (users >= 20):
                users -= 1
            else:
                users += 1

            cafe = self.bot.get_channel(self.channel_cafe)
            
            for user in list_users:
                parse_user = int(user[2:-1])
                if guild.get_member(parse_user) is not None:
                    new_users.append(user)
            
            list_users = []
            self.update_list(list_users, users, time_final, new_delta)
            await cafe.send(
                f'''{fec_star} Welcome {" ".join(set(new_users))}!
Pueden presentarse en este canal, <#{self.channel_cafe}> y leer el <#{self.channel_manual}> para conocer cómo participar en nuestra comunidad {impostor}''')
            new_users = []
        else:
            self.update_list(list_users, users, time_zero, delta)