import { CommandInteraction, SlashCommandBuilder } from "discord.js";
import { DISCORD_PREFIX as PREFIX } from "../libs/environment.js";

export const data = new SlashCommandBuilder()
  .setName("help")
  .setDescription("Lista de comandos disponibles.");

export async function execute(interaction: CommandInteraction) {
  console.info("General Help");

  await interaction.reply({
    ephemeral: true,
    embeds: [
      {
        color: 0x00c29d,
        title: "Ayuda General",
        author: {
          name: interaction.client.user.displayName,
          icon_url: interaction.client.user.avatarURL()!,
          url: "https://frontend.cafe/",
        },
        thumbnail: {
          url: "https://res.cloudinary.com/sebasec/image/upload/v1614807768/Fec_with_Shadow_jq8ll8.png",
        },
        description: `Lista de comandos disponibles.\nPara mas ayuda escriba: \`${PREFIX}help <comando>\``,
        fields: [
          // {
          //   name: `${PREFIX}reminder`,
          //   value:
          //     "Genera un recordatorio que se emite de forma automática con las siguientes frecuencias:  \n\
          //     - 1 día antes del evento.  \n\
          //     - 1 hora antes del evento.  \n\
          //     - 10 minutos antes del evento.",
          // },
          {
            name: `${PREFIX}poll`,
            value:
              "Genera una interfase con botones para poder realizar encuestas y votaciones.",
            // inline: true,
          },
          // {
          //   name: `${PREFIX}search`,
          //   value: "Hace busquedas en la web y muestra los resultados.",
          //   inline: true,
          // },
        ],
      },
    ],
  });
}
