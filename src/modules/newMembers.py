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
        self.channel_test = 776196097131413534
        self.channel_cafe = 594935077637718027


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


    def update_list(self, listUsers: list, users: int, time_zero: float, delta: float):
        '''
        Descripción: Actualiza la lista de usuarios nuevos, la condición de usuarios nuevos y el tiempo de espera
        Precondición: Debe existir la colección con el documento
        Poscondición: La lista de usuarios nuevos, la condición de usuarios nuevos y el tiempo de espera se actualizan
        '''
        try:
            self.db.update('Users', '292960205647380995', {
                "new_users_id": listUsers,
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
        newMember = member.mention
        package = self.get_list()
        listUsers, users, time_zero, delta = package["new_users_id"], package["user_condition"], package["time_sec"], package["time_delta"]
        newUsers = ''
        impostor = '<:fecimpostor:755971090471321651>'
        fec_star = '<:fecstar:755451362950512660>'
        messages = [
            '<#747925827265495111> para ver más información sobre la comunidad!',
            '<#748183026244255824> para ver las normas de convivencia!',
            '<#762660432380821525> y podrán recibir noticias de los grupos de estudio!',
            '<#748547143157022871> si no se presentaron. Queremos conocerles!'
        ]

        listUsers.append(newMember)
        if (len(listUsers) == users):
            time_final = time()
            new_delta = time_final - time_zero

            if (delta < new_delta) and (users >= 20):
                users -= 1
            else:
                users += 1

            cafe = self.bot.get_channel(self.channel_cafe)
            
            for user in listUsers:
                newUsers += f'{user} '
            
            listUsers = []
            self.update_list(listUsers, users, time_final, new_delta)
            await cafe.send(f'''{fec_star} Welcome {newUsers}!\nPueden visitar el canal {random.choice(messages)} {impostor}''', delete_after=3600)
            newUsers = ''
        else:
            self.update_list(listUsers, users, time_zero, delta)
