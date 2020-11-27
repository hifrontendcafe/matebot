# Modulo welcome.py

from discord.ext import commands

class Welcome(commands.Cog):
    '''
    Saludo de bienvenida al server
    '''
    def __init__(self, bot):
        '''
        __init__ del bot (importa este codigo como modulo al bot)
        '''
        self.bot = bot

    #! Comando
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.send('''Hola, bienvenidx a FrontendCafé!
        \nTe cuento, somos una comunidad de personas interesadas en tecnología y ciencias informáticas.\nCharlamos sobre lenguajes de programación, diseño web, infraestructura, compartimos dudas y tratamos de resolverlas juntxs.\nAdemás, nos organizamos en grupos para estudiar, hacer proyectos juntos y charlar en inglés para perfeccionarnos.\nTenemos un espacio de coworking, también nos vamos de after office y jugamos jueguitos!
        \nAcá te dejamos información que **es necesario que revises antes de comenzar a participar**, ya que es muy importante que todxs contribuyamos a mantener este server como un espacio seguro, amigable y divertido para cualquier persona que participe.
        \n* Código de conducta <#748183026244255824>\n* Manual de uso <#747925827265495111>
        \nNos encantaría que pases por <#748547143157022871> y nos cuentes algo de vos :slight_smile:
        \nSaludos!
        \n*El Staff de FrontendCafé*''')
