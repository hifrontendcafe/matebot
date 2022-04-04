from datetime import datetime
from discord import Embed
import pytz

from libs.embed import EmbedGenerator

async def create_reminder_embed(ctx, bot):
    """
    Create the embed for the reminder
    """
    def check_reaction(reaction, user):
        return ctx.author == user
    
    e = EmbedGenerator(ctx)
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
            
    e = EmbedGenerator(ctx)
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

    e = EmbedGenerator(ctx)
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

    e = EmbedGenerator(ctx)
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

    e = EmbedGenerator(ctx)
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
    e = EmbedGenerator(ctx)
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
    type = "date" if emojis.index(reaction.emoji) == 0 else "cron"
    await msg_bot.delete()

    return type


async def date_reminder(ctx, bot, process_date_time, colour):
    """
    Date of the reminder
    """
    def check(msg):
        if ctx.author == msg.author:
            return msg
        else:
            return None

    tz = pytz.timezone('America/Buenos_Aires')
    e = EmbedGenerator(ctx)
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
                description="""Por favor, expecifique con mas detalles la fecha del evento.
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
            description="""Por favor, expecifique con mas detalles la fecha del evento.
Ejemplo: `07/02/2022 21:19`""",
            color=colour(colour_type='ERROR')
        )
        await ctx.send(embed=embed, delete_after=60)
        return None, None
