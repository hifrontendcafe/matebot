from discord.ext import commands


class Welcome(commands.Cog):
    """
    El módulo Welcome se encarga de enviar un mensaje privado al usuario cuando se une al servidor.
    """

    def __init__(self, bot):
        """
        __init__ del bot (importa este codigo como modulo al bot)
        """
        self.bot = bot
        self.message = self.get_message()

    def get_message(self):
        """
        Extrae el mensaje de bienvenida del archivo en utils/welcome_message.txt
        """
        with open('src/utils/welcome_message.txt', 'r', encoding="utf-8") as f:
            message = f.read()
        return message

    #! Comando
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Listener que se ejecuta cuando un usuario se une al servidor.
        
        Le envía un mensaje privado al usuario con el mensaje de bienvenida (si es posible).
        """
        try:
            await member.send(self.message)
        except:
            pass # Si no puede enviar el mensaje, no hace nada
