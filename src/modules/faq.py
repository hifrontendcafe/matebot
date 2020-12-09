# Modulo faq.py v1

#///---- Imports ----///
import re
import os
import logging

from discord.ext import commands
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient

#///---- Log ----///
log = logging.getLogger(__name__)

#///---- Clase ----///
class FAQ(commands.Cog):
    '''
    Consulta y edición de FAQ
    '''
    def __init__(self, bot):
        '''
        __init__ del bot (importa este codigo como modulo al bot)
        '''
        self.bot = bot
        self.db = database(bot)

    #! !faq
    #! Comando faq
    @commands.group()
    async def faq(self, ctx):
        '''
        Comando !faq
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send("Este comando no existe! Tipea `!faq help` para ver los comandos disponibles :D")

    #! Subcomando help
    @faq.command()
    async def help(self, ctx):
        '''
        Descripción: Ayuda de FAQ
        Precondicion: Escribir en un canal !faq help
        Poscondición: El bot escribe lista de comandos con descripción
        '''
        lines = '''
```
!faq help: Ayuda del FAQ
!faq all: Por DM recibís el FAQ completo
!faq general: Preguntas generales sobre el uso de Discord y el servidor
!faq english: Preguntas relacionadas a los eventos sobre Inglés
!faq mentoring: Dudas sobre el sistema de mentorías
!faq coworking: Sobre Coworking en FEC
!faq roles: Que són y como se obtienen los roles
!faq projects: Consulta sobre los proyectos activos
```
                '''
        await ctx.send(lines)

    #! Subcomando all
    @faq.command()
    async def all(self, ctx):
        '''
        Descripción: FAQ completo por DM
        Precondición: Escribir en un canal !faq all
        Poscondición: El bot envía por DM el FAQ
        '''
        dataPrint = ""

        dataFAQ = self.db.load()
        if len(dataFAQ) != 0:
            for i, data in enumerate(dataFAQ):
                dataPrint += f"{i+1}) Pregunta: {data['Question']}\nRespuesta: {data['Answer']}\n{'-'*60}\n"
            message = "FAQ complete:\n```\n" + dataPrint + "```"
            await ctx.author.send(message)
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando general
    @faq.command()
    async def general(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría General
        Precondición: Escribir en un canal !faq general
        Poscondición: El bot envía por DM el FAQ de general
        '''
        dataGen = []
        dataPrint = ""

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'General']
        if len(dataGen) != 0:
            for i, data in enumerate(dataGen):
                dataPrint += f"{i+1}) Pregunta: {data['Question']}\nRespuesta: {data['Answer']}\n{'-'*60}\n"
            message = "General:\n```\n" + dataPrint + "```"
            await ctx.author.send(message)
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando english
    @faq.command()
    async def english(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría English
        Precondición: Escribir en un canal !faq english
        Poscondición: El bot envía por DM el FAQ de english
        '''
        dataGen = []
        dataPrint = ""

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'English']
        if len(dataGen) != 0:
            for i, data in enumerate(dataGen):
                dataPrint += f"{i+1}) Pregunta: {data['Question']}\nRespuesta: {data['Answer']}\n{'-'*60}\n"
            message = "English:\n```\n" + dataPrint + "```"
            await ctx.author.send(message)
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando mentoring
    @faq.command()
    async def mentoring(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría Mentoring
        Precondición: Escribir en un canal !faq mentoring
        Poscondición: El bot envía por DM el FAQ de mentoring
        '''
        dataGen = []
        dataPrint = ""

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'Mentoring']
        if len(dataGen) != 0:
            for i, data in enumerate(dataGen):
                dataPrint += f"{i+1}) Pregunta: {data['Question']}\nRespuesta: {data['Answer']}\n{'-'*60}\n"
            message = "Mentoring:\n```\n" + dataPrint + "```"
            await ctx.author.send(message)
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando coworking
    @faq.command()
    async def coworking(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría Coworking
        Precondición: Escribir en un canal !faq coworking
        Poscondición: El bot envía por DM el FAQ de coworking
        '''
        dataGen = []
        dataPrint = ""

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'Coworking']
        if len(dataGen) != 0:
            for i, data in enumerate(dataGen):
                dataPrint += f"{i+1}) Pregunta: {data['Question']}\nRespuesta: {data['Answer']}\n{'-'*60}\n"
            message = "Coworking:\n```\n" + dataPrint + "```"
            await ctx.author.send(message)
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando roles
    @faq.command()
    async def roles(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría Roles
        Precondición: Escribir en un canal !faq roles
        Poscondición: El bot envía por DM el FAQ de roles
        '''
        dataGen = []
        dataPrint = ""

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'Roles']
        if len(dataGen) != 0:
            for i, data in enumerate(dataGen):
                dataPrint += f"{i+1}) Pregunta: {data['Question']}\nRespuesta: {data['Answer']}\n{'-'*60}\n"
            message = "Roles:\n```\n" + dataPrint + "```"
            await ctx.author.send(message)
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando projects
    @faq.command()
    async def projects(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría Projects
        Precondición: Escribir en un canal !faq projects
        Poscondición: El bot envía por DM el FAQ de projects
        '''
        dataGen = []
        dataPrint = ""

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'Projects']
        if len(dataGen) != 0:
            for i, data in enumerate(dataGen):
                dataPrint += f"{i+1}) Pregunta: {data['Question']}\nRespuesta: {data['Answer']}\n{'-'*60}\n"
            message = "Projects:\n```\n" + dataPrint + "```"
            await ctx.author.send(message)
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

class database:
    '''
    Clase database: Realizo la consulta a FaunaDB por todos los datos que existen
    '''
    def __init__(self, bot):
        '''
        __init__
        '''
        self.bot = bot

        DB_KEY = os.getenv("FAUNADB_SECRET_KEY")
        self.client = FaunaClient(secret = DB_KEY)

    def load(self):
        '''
        Descripción: Cargo todos los datos de tipo diccionario a una lista
        '''
        listFAQ = []

        # Indezacion de datos
        allfaqs = self.client.query(
            q.paginate(
                q.match(q.index('all_faqs'))
            )
        )
        allfaqslist = [allfaqs['data']]
        result = re.findall('\\d+', str(allfaqslist))

        # Creación de lista de diccionarios
        for i in range(0, len(result), 1):
            faqdetails = self.client.query(q.get(q.ref(q.collection('FAQs'), result[i])))
            listFAQ += [faqdetails['data']]
        return listFAQ
