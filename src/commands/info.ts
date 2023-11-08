import {
  CacheType,
  Interaction,
  SlashCommandBuilder,
  channelMention,
  hyperlink,
} from "discord.js";
import { CHANNELS, TARGET_OPTIONS } from "../libs/constants.js";
import { userToMention } from "../libs/helpers.js";

const CODEPEN_LINK = hyperlink("CodePen", "https://codepen.io/");

const COMMAND = {
  INFO: "info",
  Q: "q",
  M: "m",
} as const;

const USER_GUIDE = channelMention(CHANNELS.USER_GUIDE);
const MUSIC = channelMention(CHANNELS.MUSIC);

export const data = new SlashCommandBuilder()
  .setName(COMMAND.INFO)
  .setDescription("Comandos para enviar información a los miembros")
  .addSubcommand((subcommand) =>
    subcommand
      .setName(COMMAND.Q)
      .setDescription("Enviar tips para realizar preguntas")
      .addUserOption(userToMention)
  )
  .addSubcommand((subcommand) =>
    subcommand
      .setName(COMMAND.M)
      .setDescription("Enviar aviso sobre comandos de bots de música")
      .addUserOption(userToMention)
  );

export async function execute(interaction: Interaction<CacheType>) {
  if (!interaction.isChatInputCommand() || !interaction.channel) return;

  const subcommand = interaction.options.getSubcommand();
  const user = interaction.options.getUser(TARGET_OPTIONS.USERNAME);
  if (!user) {
    return await interaction.reply({
      ephemeral: true,
      content: `Usuario no válido, por favor etiquetar a un usuario de discord con '@'.`,
    });
  }

  if (COMMAND.Q === subcommand) {
    await interaction.channel.send({
      target: user,
      content: `Hola ${user}, te dejamos algunos tips para realizar tu pregunta`,
      embeds: [
        {
          color: 0x00c29d,
          description: `
1. No pidas ayuda consultando si alguien puede ayudarte, simplemente inicia tu consulta.
2. Danos contexto, contanos que estas tratando de hacer en mensaje corto (280 caracteres).
3. Si es un error, decinos el detalle del error.
4. Un screenshot o el código en un editor online como ${CODEPEN_LINK} es ideal.
5. Si deseas compartir el código en el mensaje envuélvelo siempre en triple comilla invertida (\`\`\`).
6. Contanos qué has intentado y qué no te funcionó.

**Para más información pasate por ${USER_GUIDE}**`,
        },
      ],
    });

    //
  } else if (COMMAND.M === subcommand) {
    await interaction.channel.send({
      target: user,
      content: `¡Hola ${user}!`,
      embeds: [
        {
          color: 0x00c29d,
          description: `Los comandos de los bots de música se tipean en ${MUSIC} para evitar el spam en el resto de los canales.`,
        },
      ],
    });
  }

  await interaction.deferReply();
  await interaction.deleteReply();
}
