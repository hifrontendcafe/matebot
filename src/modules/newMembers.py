# Modulo para detección de nuevos miembros y saludo automático en #☕|café
# El id del documento creado en la colección Users es: 292556657925292550 # TODO: Cambiarlo por el de la DB de FEC

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

    def get_list(self):
        try:
            doc = self.db.get('Users', '292960205647380995')["data"]
            return (doc)
        except Exception as error:
            print(f'Hubo un error en get_list: {error}')

    def update_list(self, listUsers: list, users: int, time_zero: float, delta: float):
        try:
            self.db.update('Users', '292960205647380995', {
                "new_users_id": listUsers,
                "user_condition": users,
                "time_sec": time_zero,
                "time_delta": delta
            })
        except Exception as error:
            print(f'Hubo un error en update_list: {error}')

    #! Comando
    @commands.Cog.listener()
    async def on_member_join(self, member):
        newMember = member.mention
        package = self.get_list()
        listUsers, users, time_zero, delta = package["new_users_id"], package["user_condition"], package["time_sec"], package["time_delta"]
        newUsers = ''
        impostor = '<:fecimpostor:755971090471321651>'
        gif = [
            'https://tenor.com/S1Pf.gif',
            'https://tenor.com/sXS8.gif',
            'https://tenor.com/O6pv.gif',
            'https://tenor.com/bkDo3.gif',
            'https://tenor.com/bhJM0.gif',
            'https://tenor.com/LhvI.gif'
            ]
        messages = [
            '<#747925827265495111> para ver más información sobre la comunidad!',
            '<#748183026244255824> para ver las normas de convivencia!',
            '<#762660432380821525> y podrán recibir noticias de los grupos de estudio!',
            '<#748547143157022871> si no se presentaron. Queremos conocerlos!'
        ]

        listUsers.append(newMember)
        if (len(listUsers) == users):
            time_final = time()
            new_delta = time_final - time_zero
            if (delta > new_delta):
                users += 1
            else:
                users -= 1
            cafe = self.bot.get_channel(594935077637718027) # FEC
            for user in listUsers:
                newUsers += f'{user} '
            listUsers = []
            self.update_list(listUsers, users, time_final, new_delta)
            await cafe.send(f'''Welcome {newUsers}!\nPueden visitar el canal {random.choice(messages)} {impostor}''')
            newUsers = ''
            await cafe.send(random.choice(gif))
        else:
            self.update_list(listUsers, users, time_zero, delta)
