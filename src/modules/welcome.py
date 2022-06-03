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
        await member.send('''Hola, te damos la bienvenida a FrontendCafé!!
        \nSomos una comunidad de personas interesadas en tecnología y ciencias informáticas. Conversamos sobre lenguajes de programación, diseño web, infraestructura, compartimos dudas y tratamos de resolverlas en conjunto.\nAdemás, nos organizamos en grupos para estudiar, hacer proyectos en equipo y practicar en inglés para perfeccionarnos.\nTenemos un espacio de coworking, también nos vamos de after office y jugamos jueguitos!
        \nAquí abajo dejamos información que **es necesaria que revises antes de comenzar a participar**, ya que es muy importante que contribuyamos a mantener este server como un espacio seguro, amigable y divertido para cualquier persona que participe.
        \n* Código de conducta <#748183026244255824>\n* Manual de uso <#747925827265495111>
        \nPor favor, al hacer una consulta dentro del server, intenta incluir la mayor cantidad de datos posibles sobre qué estás intentando, qué errores encuentras y qué quieres lograr para que podamos ayudarte de la mejor manera posible. Si tienes dudas de dónde publicar la pregunta puedes consultar en <#594935077637718027> y te orientarán. Asimismo, puedes usar el buscador, situado arriba a la derecha, para verificar que tu pregunta no haya sido respondida anteriormente.
        \nNos encantaría que pases por <#748547143157022871> y nos cuentes algo de ti :slight_smile:
        \nSaludos!
        \n*El Staff de FrontendCafé*''')
