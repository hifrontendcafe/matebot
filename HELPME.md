# FrontEndCafe Bot

## Indice

- [Organización y estructura](#organización-y-estructura)
- [Módulos](#organización-y-estructura)
  - [Bienvenida](#bienvenida)
  - [FAQs](#faqs)
  - [Roles](#roles)
  - [Notificaciones del server](#notificaciones-del-server)
  - [Recordatorio de eventos](#recordatorio-de-eventos)

## Organización y estructura

## Usando módulos locales

La app está dividida para usar una carpeta llamada `modules`.
Esta carpeta `modules` contienen archivos con `clases`, donde cada una de estas clases puede representar una funcionalidad:

```bash
frontend-cafe-bot
├── HELPME.md
├── libs
│   ├── database.py
│   └── __init__.py
├── main.py
├── modules
│   ├── general.py
│   ├── help.py
│   └── __init__.py
├── README.md
└── requirements.txt
```

Ejemplo base para activar la funcionalidad de un cierto módulo:

```python
import discord
from discord.ext import commands
# modules es el nombre de la carpeta donde
# alojamos nuestros módulos
import modules

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    help_command=None
)

# Lista de módulos activa
# Activo el módulo `General`
bot.add_cog(modules.General(bot))
...
```

## Composición de un módulo

Un `module` es simplemente una subclase que hereda la clase [discord.ext.commands.Cog](https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html).
Dentro de esta clase, y haciendo uso de los decoradores, se pueden definir:

- Comandos con el decorador `@commands.command()`.
- Subcomandos, definiendo el command principal con el decorador `@commands.group()`.
- Eventos de escucha con el decorador `@commands.Cog.listener()`. (Los nombres de estos eventos están predefinidos por la api)
- Los módulos se registran con `Bot.add_cog()`.
- Los módulos ya registrados se pueden eliminar con `Bot.remove_cog()`.

Ejemplo de un módulo

```python
# __init__.py

# Esto se ejecuta de forma automática al hacer `import modules`
# (`modules` es el nombre de la carpeta)
# El nombre del archivo dentro de la carpeta `modules` es `general.py`
# y la clase dentro de este acrchivo se llama `General`
from .general import General
```

```python
# general.py

import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Evento de escucha
    # El nombre de la función ya está definida en la API
    # Puede ser opcional
    # Se puede definir el mismo evento en diferentes clases
    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    # Defino un comando principal
    # Puede ser cualquier nombre
    # No puede repetirse un comando principal entre diferentes clases
    # Se pueden definir los parametros que va aceptar el comando
    # !add 2 3
    @commands.command()
    async def add(self, ctx, left: int, right: int):
        # Suma 2 números
        await ctx.send(left + right)

    # Defino un comando principal con la posibilidad de definir subcomandos
    @commands.group()
    async def main_faq(self, ctx):
        # Si no invoco un subcomando envía un aviso
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid command passed...')

    # De manera `mágica` puedo usar este decorador para definir el subcomando
    # Los subcomandos pueden repetirse entre diferentes clases
    # !main_faq sub_faq
    @main_faq.command()
    async def sub_faq(self, ctx):
        pass
```

## Módulos

### Bienvenida

TODO

### Roles

TODO

### FAQs

TODO

## Notificaciones del server

TODO

## Recordatorio de eventos

TODO
