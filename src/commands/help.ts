import { CacheType, Interaction, SlashCommandBuilder } from "discord.js";

export const data = new SlashCommandBuilder()
  .setName("help")
  .setDescription(
    "Ofrece información completa sobre todos los comandos disponibles."
  );

export async function execute(interaction: Interaction<CacheType>) {
  if (!interaction.isChatInputCommand()) return;

  await interaction.reply({
    ephemeral: true,
    embeds: [
      {
        color: 0x00c29d,
        title: "Ayuda General",
        thumbnail: {
          url: "https://res.cloudinary.com/sebasec/image/upload/v1614807768/Fec_with_Shadow_jq8ll8.png",
        },
        description:
          "Lista de comandos disponibles.\nPara mas ayuda escriba: `/help <comando>`",
        fields: [
          // {
          //   name: `/reminder`,
          //   value:
          //     "Genera un recordatorio que se emite de forma automática con las siguientes frecuencias:  \n\
          //     - 1 día antes del evento.  \n\
          //     - 1 hora antes del evento.  \n\
          //     - 10 minutos antes del evento.",
          // },
          {
            name: `/info`,
            value: "Comandos para enviar información a los miembros.",
            // inline: true,
          },
          {
            name: `/poll`,
            value:
              "Crear una encuesta básica Si/No, o con multiples opciones (10 max).",
            // inline: true,
          },

          // {
          //   name: `/search`,
          //   value: "Hace busquedas en la web y muestra los resultados.",
          //   inline: true,
          // },
        ],
      },
    ],
  });
}
