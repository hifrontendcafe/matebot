from discord.components import SelectMenu, SelectOption

def selects_day():
    return SelectMenu(
        custom_id='_select_it',
        options=[
            SelectOption(emoji='1️⃣', label='Lunes', value='Monday'),
            SelectOption(emoji='2️⃣', label='Martes', value='Tuesday'),
            SelectOption(emoji='3️⃣', label='Miércoles', value='Wednesday'),
            SelectOption(emoji='4️⃣', label='Jueves', value='Thursday'),
            SelectOption(emoji='5️⃣', label='Viernes', value='Friday'),
            SelectOption(emoji='6️⃣', label='Sábado', value='Saturday'),
            SelectOption(emoji='7️⃣', label='Domingo', value='Sunday'),
        ],
        placeholder='Elige los días del recordatorio',
        max_values=7
    )