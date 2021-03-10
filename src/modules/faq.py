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
        __init__ del bot
        '''
        self.bot = bot
        self.db = database(bot)

    #! Comando faq
    @commands.group()
    async def faq(self, ctx):
        '''
        Comando faq
        '''
        PREFIX = os.getenv("DISCORD_PREFIX")
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Este comando no existe! Tipea `{PREFIX}faq help` para ver los comandos disponibles :D")

    #! Subcomando help
    @faq.command()
    async def help(self, ctx):
        '''
        Descripción: Ayuda de FAQ
        Precondicion: Escribir en un canal {PREFIX}faq help
        Poscondición: El bot escribe lista de comandos con descripción
        '''
        PREFIX = os.getenv("DISCORD_PREFIX")
        lines = f'''
```
{PREFIX}faq help: Ayuda del FAQ
{PREFIX}faq all: Por DM recibís el FAQ completo
{PREFIX}faq general: Preguntas generales sobre el uso de Discord y el servidor
{PREFIX}faq english: Preguntas relacionadas a los eventos para charlar en inglés
{PREFIX}faq mentoring: Dudas sobre el sistema de mentorías
{PREFIX}faq coworking: ¿Qué es el Coworking en FEC?
{PREFIX}faq roles: Que són y cómo se obtienen los roles
{PREFIX}faq projects: Consulta sobre los proyectos grupales de desarrollo
{PREFIX}faq studygroup: Consulta sobre los grupos de estudio
```
                '''
        await ctx.send(lines)

    #! Subcomando all
    @faq.command()
    async def all(self, ctx):
        '''
        Descripción: FAQ completo por DM
        Precondición: Escribir en un canal {PREFIX}faq all
        Poscondición: El bot envía por DM el FAQ
        '''
        dataPrint = [""] * 4

        dataFAQ = self.db.load()
        if len(dataFAQ) != 0:
            for data in dataFAQ:
                if len(dataPrint[0]) < 1500:
                    dataPrint[0] = dataPrint[0] + f"+{data['Question']}\n{data['Answer']}\n\n"
                elif len(dataPrint[1]) < 1500:
                    dataPrint[1] = dataPrint[1] + f"+{data['Question']}\n{data['Answer']}\n\n"
                elif len(dataPrint[2]) < 1500:
                    dataPrint[2] = dataPrint[2] + f"+{data['Question']}\n{data['Answer']}\n\n"
                else:
                    dataPrint[3] = dataPrint[3] + f"+{data['Question']}\n{data['Answer']}\n\n"
            message =   ["FAQ completo:\n```diff\n" + dataPrint[0] + "```",
                         "```diff\n" + dataPrint[1] + "```", 
                         "```diff\n" + dataPrint[2] + "```", 
                         "```diff\n" + dataPrint[3] + "```"] 
            await ctx.author.send(message[0])
            if len(dataPrint[1]) != 0:
                await ctx.author.send(message[1])
            if len(dataPrint[2]) != 0:
                await ctx.author.send(message[2])
            if len(dataPrint[3]) != 0:
                await ctx.author.send(message[3])
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando general
    @faq.command()
    async def general(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría General
        Precondición: Escribir en un canal {PREFIX}faq general
        Poscondición: El bot envía por DM el FAQ de general
        '''
        dataGen = []
        dataPrint = [""] * 2

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'General']
        if len(dataGen) != 0:
            for data in dataGen:
                if len(dataPrint[0]) < 1500:
                    dataPrint[0] = dataPrint[0] + f"+{data['Question']}\n{data['Answer']}\n\n"
                else:
                    dataPrint[1] = dataPrint[1] + f"+{data['Question']}\n{data['Answer']}\n\n"
            message = ["General:\n```diff\n" + dataPrint[0] + "```", "General (continuación):\n```diff\n" + dataPrint[1] + "```"] 
            await ctx.author.send(message[0])
            if len(dataPrint[1]) != 0:
                await ctx.author.send(message[1])
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando english
    @faq.command()
    async def english(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría English
        Precondición: Escribir en un canal {PREFIX}faq english
        Poscondición: El bot envía por DM el FAQ de english
        '''
        dataGen = []
        dataPrint = [""] * 2

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'English']
        if len(dataGen) != 0:
            for data in dataGen:
                if len(dataPrint[0]) < 1500:
                    dataPrint[0] = dataPrint[0] + f"+{data['Question']}\n{data['Answer']}\n\n"
                else:
                    dataPrint[1] = dataPrint[1] + f"+{data['Question']}\n{data['Answer']}\n\n"
            message = ["English:\n```diff\n" + dataPrint[0] + "```", "English (continuación):\n```diff\n" + dataPrint[1] + "```"] 
            await ctx.author.send(message[0])
            if len(dataPrint[1]) != 0:
                await ctx.author.send(message[1])
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando mentoring
    @faq.command()
    async def mentoring(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría Mentoring
        Precondición: Escribir en un canal {PREFIX}faq mentoring
        Poscondición: El bot envía por DM el FAQ de mentoring
        '''
        dataGen = []
        dataPrint = [""] * 2

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'Mentoring']
        if len(dataGen) != 0:
            for data in dataGen:
                if len(dataPrint[0]) < 1500:
                    dataPrint[0] = dataPrint[0] + f"+{data['Question']}\n{data['Answer']}\n\n"
                else:
                    dataPrint[1] = dataPrint[1] + f"+{data['Question']}\n{data['Answer']}\n\n"
            message = ["Mentoring:\n```diff\n" + dataPrint[0] + "```", "Mentoring (continuación):\n```diff\n" + dataPrint[1] + "```"] 
            await ctx.author.send(message[0])
            if len(dataPrint[1]) != 0:
                await ctx.author.send(message[1])
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando coworking
    @faq.command()
    async def coworking(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría Coworking
        Precondición: Escribir en un canal {PREFIX}faq coworking
        Poscondición: El bot envía por DM el FAQ de coworking
        '''
        dataGen = []
        dataPrint = [""] * 2

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'Coworking']
        if len(dataGen) != 0:
            for data in dataGen:
                if len(dataPrint[0]) < 1500:
                    dataPrint[0] = dataPrint[0] + f"+{data['Question']}\n{data['Answer']}\n\n"
                else:
                    dataPrint[1] = dataPrint[1] + f"+{data['Question']}\n{data['Answer']}\n\n"
            message = ["Coworking:\n```diff\n" + dataPrint[0] + "```", "Coworking (continuación):\n```diff\n" + dataPrint[1] + "```"] 
            await ctx.author.send(message[0])
            if len(dataPrint[1]) != 0:
                await ctx.author.send(message[1])
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando roles
    @faq.command()
    async def roles(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría Roles
        Precondición: Escribir en un canal {PREFIX}faq roles
        Poscondición: El bot envía por DM el FAQ de roles
        '''
        dataGen = []
        dataPrint = [""] * 2

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'Roles']
        if len(dataGen) != 0:
            for data in dataGen:
                if len(dataPrint[0]) < 1500:
                    dataPrint[0] = dataPrint[0] + f"+{data['Question']}\n{data['Answer']}\n\n"
                else:
                    dataPrint[1] = dataPrint[1] + f"+{data['Question']}\n{data['Answer']}\n\n"
            message = ["Roles:\n```diff\n" + dataPrint[0] + "```", "Roles (continuación):\n```diff\n" + dataPrint[1] + "```"] 
            await ctx.author.send(message[0])
            if len(dataPrint[1]) != 0:
                await ctx.author.send(message[1])
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando projects
    @faq.command()
    async def projects(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría Projects
        Precondición: Escribir en un canal {PREFIX}faq projects
        Poscondición: El bot envía por DM el FAQ de projects
        '''
        dataGen = []
        dataPrint = [""] * 2

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'Projects']
        if len(dataGen) != 0:
            for data in dataGen:
                if len(dataPrint[0]) < 1500:
                    dataPrint[0] = dataPrint[0] + f"+{data['Question']}\n{data['Answer']}\n\n"
                else:
                    dataPrint[1] = dataPrint[1] + f"+{data['Question']}\n{data['Answer']}\n\n"
            message = ["Projects:\n```diff\n" + dataPrint[0] + "```", "Projects (continuación):\n```diff\n" + dataPrint[1] + "```"] 
            await ctx.author.send(message[0])
            if len(dataPrint[1]) != 0:
                await ctx.author.send(message[1])
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')

    #! Subcomando study-group
    @faq.command()
    async def studygroup(self, ctx):
        '''
        Descripción: Consulta de DB sobre categoría English
        Precondición: Escribir en un canal {PREFIX}faq english
        Poscondición: El bot envía por DM el FAQ de english
        '''
        dataGen = []
        dataPrint = [""] * 2

        dataFAQ = self.db.load()
        dataGen = [data for data in dataFAQ if data['Category'] == 'Study-Group']
        if len(dataGen) != 0:
            for data in dataGen:
                if len(dataPrint[0]) < 1500:
                    dataPrint[0] = dataPrint[0] + f"+{data['Question']}\n{data['Answer']}\n\n"
                else:
                    dataPrint[1] = dataPrint[1] + f"+{data['Question']}\n{data['Answer']}\n\n"
            message = ["Study Group:\n```diff\n" + dataPrint[0] + "```", "Study Group (continuación):\n```diff\n" + dataPrint[1] + "```"] 
            await ctx.author.send(message[0])
            if len(dataPrint[1]) != 0:
                await ctx.author.send(message[1])
        else:
            await ctx.author.send('No hay datos para esta consulta. Contactar con los administradores!')
    


class database:
    '''
    Clase database: Realizo la consulta a FaunaDB por todos los datos que existen en la collection FAQs
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
