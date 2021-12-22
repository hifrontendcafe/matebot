from discord import ActionRow, Button, ButtonStyle

def btns_confirm():
    """
    Botones de confirmación
    """
    return [
        ActionRow(
            Button(
                label='Continuar',
                emoji='✅',
                custom_id='continue',
                style=ButtonStyle.Success
            ),
            Button(
                label='Abortar',
                emoji='🛑',
                custom_id='martes',
                style=ButtonStyle.Danger
            ),
        )
    ]