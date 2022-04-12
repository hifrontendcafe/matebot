from datetime import datetime
from discord import Embed
import zoneinfo

from libs.embed import EmbedGenerator

async def create_reminder_embed(ctx, bot):
    """
    Create the embed for the reminder
    """
    def check_reaction(reaction, user):
        return ctx.author == user

    e = EmbedGenerator()
    e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
    e.title = "[ADD] Agregar recordatorio"
    e.description = """
Hola! A continuación, te pediré los datos necesarios para crear uno o varios recordatorios. Sigue los pasos con atención!

Antes de terminar, te mostraré el resultado final a modo de vista previa.
"""
    e.fields= [("Reacciones", """
✅ Ok, empecemos!
❌ Nop, lo haré en otro momento
""")]
    embed = e.generate_embed()
    msg = await ctx.send(embed=embed)
    await msg.add_reaction(emoji="✅")
    await msg.add_reaction(emoji="❌")
    reaction, user = await bot.wait_for('reaction_add', check=check_reaction)
    await msg.delete()

    return reaction.emoji


async def addressee_reminder(ctx, bot):
    """
    Addressee of the reminder
    """
    def check(msg):
        if ctx.author == msg.author:
            return msg
        else:
            return None

    e = EmbedGenerator()
    e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
    e.title = "[ADD] Agregar recordatorio"
    e.description = ""
    e.fields= [("¿Destinatarios del recordatorio?", """
Puedes colocar menciones a users y/o roles del FrontendCafé. **No se verán dentro del embed!**
Escribe el mensaje y aprieta <Enter>
""")]
    embed = e.generate_embed()
    msg_bot = await ctx.send(embed=embed)
    msg = await bot.wait_for('message', check=check)
    if msg:
        text = msg.content
        await msg_bot.delete()
        await msg.delete()

        return text, ctx.author.id
    else:
        await msg_bot.delete()
        return None, None


async def title_reminder(ctx, bot):
    """
    Title of the reminder
    """
    def check(msg):
        if ctx.author == msg.author:
            return msg
        else:
            return None

    e = EmbedGenerator()
    e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
    e.title = "[ADD] Agregar recordatorio"
    e.description = ""
    e.fields= [("¿Nombre del recordatorio?", """
En lo posible, debe ser corto y descriptivo.
Escribe el mensaje y aprieta <Enter>
""")]
    embed = e.generate_embed()
    msg_bot = await ctx.send(embed=embed)
    msg = await bot.wait_for('message', check=check)
    title = msg.content
    await msg_bot.delete()
    await msg.delete()

    return title


async def description_reminder(ctx, bot):
    """
    Description of the reminder
    """
    def check(msg):
        if ctx.author == msg.author:
            return msg
        else:
            return None

    e = EmbedGenerator()
    e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
    e.title = "[ADD] Agregar recordatorio"
    e.description = ""
    e.fields= [("¿Descripción del recordatorio?", """
Puede ser más largo, hasta 256 caractéres.
Escribe el mensaje y aprieta <Enter>
""")]
    embed = e.generate_embed()
    msg_bot = await ctx.send(embed=embed)
    msg = await bot.wait_for('message', check=check)
    description = msg.content
    await msg_bot.delete()
    await msg.delete()

    return description


async def channel_reminder(ctx, bot, process_channel, colour):
    """
    Channel of the reminder
    """
    def check(msg):
        if ctx.author == msg.author:
            return msg
        else:
            return None

    e = EmbedGenerator()
    e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
    e.title = "[ADD] Agregar recordatorio"
    e.description = ""
    e.fields= [("¿En cuál canal publicar el recordatorio?", """
Presiona # y acontinuación el nombre del canal.
Escribe el mensaje y aprieta <Enter>
""")]
    embed = e.generate_embed()
    msg_bot = await ctx.send(embed=embed)
    msg = await bot.wait_for('message', check=check)
    channel_check = process_channel(msg.content)
    # if channel_check is Error.CHANNEL:
    if channel_check == 4:
        embed = Embed(
            title="🟥 Error",
            description="Por favor, elija un canal válido.\nTipee `#nombre-del-canal`.",
            color=colour(colour_type='ERROR')
        )
        return await ctx.send(embed=embed, delete_after=60)
    channel = msg.content
    await msg_bot.delete()
    await msg.delete()

    return channel


async def type_reminder(ctx, bot):
    """
    Type of the reminder
    """
    def check_reaction(reaction, user):
        return ctx.author == user
    e = EmbedGenerator()
    e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
    e.title = "[ADD] Agregar recordatorio"
    e.description = ""
    e.fields= [
        ("¿El recordatorio es único?", "Elije una opción"),
        ("Reacciones", """
1️⃣ Debe publicarse en una fecha exacta (será único)
2️⃣ Se repite un día en específico cada semana
3️⃣ Se repite un día en específico cada mes
""")
    ]
    embed = e.generate_embed()
    msg_bot = await ctx.send(embed=embed)
    emojis = ["1️⃣", "2️⃣", "3️⃣"]
    for emoji in emojis:
        await msg_bot.add_reaction(emoji=emoji)
    reaction, user = await bot.wait_for('reaction_add', check=check_reaction)
    is_cron_weekly = emojis.index(reaction.emoji) == 1
    type = "date" if emojis.index(reaction.emoji) == 0 else "cron"
    await msg_bot.delete()

    return type, is_cron_weekly


async def date_reminder(ctx, bot, process_date_time, colour):
    """
    Date of the reminder
    """
    def check(msg):
        if ctx.author == msg.author:
            return msg
        else:
            return None

    tz = zoneinfo.ZoneInfo('America/Buenos_Aires')
    e = EmbedGenerator()
    e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
    e.title = "[ADD] Agregar recordatorio"
    e.description = ""
    e.fields= [("¿Día y hora del recordatorio?", f"""
El formato a seguir es: dd/mm/yyyy HH:MM
Ejemplo: {datetime.now(tz).strftime('%d/%m/%Y %H:%M')}
Escribe el mensaje y aprieta <Enter>
""")]
    try:
        embed = e.generate_embed()
        msg_bot = await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check)
        rem_date, rem_time = msg.content.split(" ")
        date_time = process_date_time(date=rem_date, time=rem_time)
        if date_time == 1: # Error.DATETIME
            embed = Embed(
                title="🟥 Error: Formato inválido",
                description="""Por favor, expecifique con mas detalles la fecha del recordatorio.
Ejemplo: `07/02/2022 21:19`""",
                color=colour(colour_type='ERROR')
            )
            await ctx.send(embed=embed, delete_after=60)
            return None, None
        elif date_time == 3: # Error.DATE_HAS_PASSED
            embed = Embed(
                title="🟥 Error: Fecha pasada",
                description="""Por favor, defina una fecha y hora posterior a la actual.
Recuerde que la hora está en GMT-3 (Zona horaria de Argentina)""",
                color=colour(colour_type='ERROR')
            )
            await ctx.send(embed=embed, delete_after=60)
            return None, None
        await msg_bot.delete()
        await msg.delete()
        return rem_date, rem_time
    except ValueError:
        embed = Embed(
            title="🟥 Error: Formato inválido",
            description="""Por favor, expecifique con mas detalles la fecha del recordatorio.
Ejemplo: `07/02/2022 21:19`""",
            color=colour(colour_type='ERROR')
        )
        await ctx.send(embed=embed, delete_after=60)
        return None, None


async def end_reminder(ctx, bot, process_date_time, colour):
    """
    Date of reminder's end
    """
    def check(msg):
        if ctx.author == msg.author:
            return msg
        else:
            return None

    tz = zoneinfo.ZoneInfo('America/Buenos_Aires')
    e = EmbedGenerator()
    e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
    e.title = "[ADD] Agregar recordatorio"
    e.description = ""
    e.fields= [("¿Cuándo terminará el recordatorio?", f"""
El formato a seguir es: dd/mm/yyyy
Ejemplo: {datetime.now(tz).strftime('%d/%m/%Y')}
Escribe el mensaje y aprieta <Enter>
""")]
    try:
        embed = e.generate_embed()
        msg_bot = await ctx.send(embed=embed)
        end_date = await bot.wait_for('message', check=check)
        date_time = process_date_time(date=end_date.content, time='00:00')
        if date_time == 1: # Error.DATETIME
            embed = Embed(
                title="🟥 Error: Formato inválido",
                description="""Por favor, expecifique con mas detalles la fecha de fin del recordatorio.
Ejemplo: `07/02/2022`""",
                color=colour(colour_type='ERROR')
            )
            await ctx.send(embed=embed, delete_after=60)
            return None
        elif date_time == 3: # Error.DATE_HAS_PASSED
            embed = Embed(
                title="🟥 Error: Fecha pasada",
                description="""Por favor, defina una fecha posterior a la actual.
Recuerde que la hora está en GMT-3 (Zona horaria de Argentina)""",
                color=colour(colour_type='ERROR')
            )
            await ctx.send(embed=embed, delete_after=60)
            return None
        await msg_bot.delete()
        await end_date.delete()
        return end_date
    except ValueError:
        embed = Embed(
            title="🟥 Error: Formato inválido",
            description="""Por favor, expecifique con mas detalles la fecha de fin del recordatorio.
Ejemplo: `07/02/2022`""",
            color=colour(colour_type='ERROR')
        )
        await ctx.send(embed=embed, delete_after=60)
        return None


async def get_day(ctx, bot, colour):
    """
    Day of month of the reminder (1-31)
    """
    def check(msg):
        if ctx.author == msg.author:
            return msg
        else:
            return None

    e = EmbedGenerator()
    e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
    e.title = "[ADD] Agregar recordatorio"
    e.description = ""
    e.fields= [("¿Qué día del mes aparecerá el recordatorio?", f"""
Ten en cuenta que si escribes `23`, el recordatorio aparecerá el 23 de cada mes.
Otro punto a tener en cuenta: si escribes `31`, el recordatorio aparecerá solo el 31 de cada mes. Por lo tanto, no aparecería en Febrero!
Escribe el mensaje y aprieta <Enter>
""")]
    try:
        embed = e.generate_embed()
        msg_bot = await ctx.send(embed=embed)
        day_rem = await bot.wait_for('message', check=check)
        day = int(day_rem.content)
        
        if day < 1 or day > 31:
            embed = Embed(
                title="🟥 Error: Día inválido",
                description="Por favor, elige un día entre 1 y 31.",
                color=colour(colour_type='ERROR')
            )
            await ctx.send(embed=embed, delete_after=60)
            return None

        await msg_bot.delete()
        await day_rem.delete()
        return day
    except ValueError:
        embed = Embed(
            title="🟥 Error: Formato inválido",
            description="""Por favor, ingrese un número entero entre 1 y 31.""",
            color=colour(colour_type='ERROR')
        )
        await ctx.send(embed=embed, delete_after=60)
        return None


async def get_day_week(ctx, bot):
    """
    Day of week of the reminder (1-31)
    """
    def check_reaction(reaction, user):
        return ctx.author == user

    e = EmbedGenerator()
    e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
    e.title = "[ADD] Agregar recordatorio"
    e.description = ""
    e.fields= [("¿Qué día de la semana aparecerá el recordatorio?", f"""
Reacciona con una de los siguientes emojis para elegir el día de la semana del recordatorio:
1️⃣: Lunes
2️⃣: Martes
3️⃣: Miércoles
4️⃣: Jueves
5️⃣: Viernes
6️⃣: Sábado
7️⃣: Domingo
Escribe el mensaje y aprieta <Enter>
""")]
    embed = e.generate_embed()
    msg_bot = await ctx.send(embed=embed)
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]
    for emoji in emojis:
        await msg_bot.add_reaction(emoji=emoji)
    reaction, user = await bot.wait_for('reaction_add', check=check_reaction)
    day = emojis.index(reaction.emoji)

    await msg_bot.delete()
    return day


async def get_time(ctx, bot, colour):
    """
    Time of the reminder (HH:MM)
    """
    def check(msg):
        if ctx.author == msg.author:
            return msg
        else:
            return None

    e = EmbedGenerator()
    e.author = (f"{ctx.me.name}", f"{ctx.me.avatar_url}")
    e.title = "[ADD] Agregar recordatorio"
    e.description = ""
    e.fields= [("¿En qué horario aparecerá el recordatorio?", f"""
Ejemplos: `12:00`, `23:29`, `14:40`
Escribe el mensaje y aprieta <Enter>
""")]
    try:
        embed = e.generate_embed()
        msg_bot = await ctx.send(embed=embed)
        time_rem = await bot.wait_for('message', check=check)
        hour, minute = time_rem.content.split(":")
        HH = int(hour)
        MM = int(minute)
        
        if (HH < 0 or HH > 23) or (MM < 0 or MM > 59):
            embed = Embed(
                title="🟥 Error: Horario inválido",
                description="Por favor, elige un horario. Ejemplos: `12:00`, `23:29`, `14:40`",
                color=colour(colour_type='ERROR')
            )
            await ctx.send(embed=embed, delete_after=60)
            return None, None

        await msg_bot.delete()
        await time_rem.delete()
        return hour, minute
    except ValueError:
        embed = Embed(
            title="🟥 Error: Formato inválido",
            description="""Por favor, elige un horario. Ejemplos: `12:00`, `23:29`, `14:40`
            Chequea haber escrito el separador de horas y minutos con dos puntos (:) y sin espacios.""",
            color=colour(colour_type='ERROR')
        )
        await ctx.send(embed=embed, delete_after=60)
        return None, None