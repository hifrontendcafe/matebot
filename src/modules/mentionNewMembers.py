'''
Módulo para darle la bienvenida a los nuevos miembros de FrontendCafé
En esto módulo, el bot almacena los últimos 2 mensajes enviados, el resto los borra
'''

# ///---- Imports ----///
import logging
import random
import os
from time import time
from collections import deque
from libs.database import Database as DB

from discord.ext.commands import Cog

#///---- Log ----///
log = logging.getLogger(__name__)

class MentionNewMembers(Cog):
    '''
    Saludo de bienvenida al server
    '''
    def __init__(self, bot):
        '''
        __init__ del bots
        '''
        self.bot = bot
        secret = os.getenv("FAUNADB_SECRET_KEY")
        self.db = DB(secret)
        self.collection = "Users"
        self.initial_data = {
                "new_users_id": [],
                "user_condition": 20,
                "time_sec": time(),
                "time_delta": 0
            }
        self.create_initial_data() # Crea un documento con los datos iniciales (si no existe)
        self.msg_bot = deque([]) # Mensajes enviados por el bot
        self.channel_test = 776196097131413534
        self.channel_cafe = 594935077637718027
        self.get_list()

    def get_list(self):
        '''
        Descripción: Obtiene la lista de usuarios nuevos y otros parámetros para análisis
        Precondición: Debe existir la colección con el documento
        Poscondición: Se obtiene la lista de usuarios nuevos, la condición de usuarios nuevos, el tiempo de inicio y el tiempo de espera
        '''
        try:
            doc = self.db.get('Users', '1')["data"]
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
            self.db.update('Users', '1', {
                "new_users_id": listUsers,
                "user_condition": users,
                "time_sec": time_zero,
                "time_delta": delta
            })
        except Exception as error:
            print(f'Hubo un error en update_list: {error}')


    def create_initial_data(self):
        '''
        Descripción: Inicializa el documento de la base de datos con los datos iniciales.
        Precondición: No debe existir la colección y el indice con datos iniciales.
        Poscondición: La colección se crea con los datos iniciales (si exite, no se crea). Busco ID de la colección.
        '''

        # TODO: Chequear esta función si crea correctamente una colección con los datos iniciales
        collection_created = self.db.create_collection(name=self.collection)

        if collection_created:
            self.db.create_index(collection=self.collection, id=1, data=self.initial_data)
            log.info(f"Se creó un documento en {self.collection} con id 1")


    @Cog.listener()
    async def on_message(self, message):
        '''
        Descripción:    - El bot escucha mensajes enviados en Café. Almacena 2 mensajes en una cola.
                        Una vez se manda un 3er mensaje, elimina el mensaje más viejo de la cola.
        Precondición:   - El bot manda mensajes de bienvenida a los nuevos usuarios en Café
                        - Solo debe almacenar los últimos dos mensajes de bienvenida
        Poscondición:   - Elimina el mensaje más viejo si ya hay dos mensajes en la cola
        '''
        if message.channel.id == self.channel_test: # ID del canal bot-test
            if (message.author.id == self.bot.user.id) and ('<:fecstar:755451362950512660> Welcome' in message.content):
                if len(self.msg_bot) == 2: # Si ya hay dos mensajes del bot almacenados
                    msg_del = self.msg_bot.pop()
                    await msg_del.delete()
                self.msg_bot.appendleft(message) # Agrego el mensaje recibido a la cola de mensajes

    @Cog.listener()
    async def on_member_join(self, member):
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
            '<#748547143157022871> si no se presentaron. Queremos conocerlos!'
        ]

        listUsers.append(newMember)
        if (len(listUsers) == users):
            time_final = time()
            new_delta = time_final - time_zero

            if (delta < new_delta) and (users >= 20):
                users -= 1
            else:
                users += 1

            cafe = self.bot.get_channel(self.channel_test)

            for user in listUsers:
                newUsers += f'{user} '
            listUsers = []
            self.update_list(listUsers, users, time_final, new_delta)
            await cafe.send(f'''{fec_star} Welcome {newUsers}!\nPueden visitar el canal {random.choice(messages)} {impostor}''')
            newUsers = ''
        else:
            self.update_list(listUsers, users, time_zero, delta)