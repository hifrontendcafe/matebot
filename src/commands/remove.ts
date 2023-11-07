import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  CacheType,
  Interaction,
  SlashCommandBuilder,
  roleMention,
} from "discord.js";
import { ROLES, TARGET_OPTIONS } from "../libs/constants.js";
import { userToMention } from "../libs/helpers.js";
import { patchWarning } from "../libs/services.js";

const COMMANDS = {
  REMOVE: "remove",
  PENALTY: "penalty",
} as const;

const ADMIN_MENTORS = roleMention(ROLES.ADMIN_MENTORS);

export const data = new SlashCommandBuilder()
  .setName(COMMANDS.REMOVE)
  .setDescription("Comando para remover penalizaciones")
  .setDefaultMemberPermissions(0)
  .setDMPermission(false)
  .addSubcommand((subcommand) =>
    subcommand
      .setName(COMMANDS.PENALTY)
      .setDescription("Remueve una penalización a un mentee")
      .addUserOption(userToMention)
  );

const ACTION_CONFIRM = "confirm";
const ACTION_CANCEL = "cancel";
const confirm = new ButtonBuilder()
  .setCustomId(ACTION_CONFIRM)
  .setLabel("Confirmar")
  .setStyle(ButtonStyle.Danger);
const cancel = new ButtonBuilder()
  .setCustomId(ACTION_CANCEL)
  .setLabel("Cancelar")
  .setStyle(ButtonStyle.Secondary);
const confirmationButtons = new ActionRowBuilder<ButtonBuilder>().setComponents(
  cancel,
  confirm
);

export async function execute(interaction: Interaction<CacheType>) {
  if (!interaction.isChatInputCommand()) return;

  const subcommand = interaction.options.getSubcommand();
  if (COMMANDS.REMOVE === subcommand) return;

  // Options from commands, the username option is required.
  const user = interaction.options.getUser(TARGET_OPTIONS.USERNAME, true);
  const reason = interaction.options.getString(TARGET_OPTIONS.REASON);

  const member = await interaction.guild?.members
    .fetch(user.id)
    .catch(console.error);
  if (!member) {
    const message = `> No se pudo encontrar a ${user}.`;
    await interaction.reply({ ephemeral: true, content: message });
    return console.log(message);
  }

  const response = await interaction.reply({
    ephemeral: true,
    content: `Confirma si deseas remover la penalización de ${member}${
      reason ? `, con motivo: "${reason}"?` : ""
    }`,
    components: [confirmationButtons],
  });

  try {
    const confirmation = await response.awaitMessageComponent({
      filter: (i) => i.user.id === interaction.user.id,
      time: 60000,
    });

    if (ACTION_CONFIRM === confirmation.customId) {
      try {
        const data = await patchWarning({
          authorId: interaction.user.id,
          authorUsername: interaction.user.displayName,
          forgiveCause: reason,
          menteeId: member.id,
        });

        if (data["code"] === "303") {
          await interaction.channel?.send(`
            > :point_right:  **Se ha removido la penalización de ${member}**
            > 
            > _ID del usuario: ${member.id}_
            > 
            > \`${interaction.user}\`
          `);

          return await interaction.deleteReply();
        }
        else if (data["code"] === "301") {
          await confirmation.update({
            content: `
              > :ballot_box_with_check:  **${member} no tiene penalizaciones**
              > 
              > _ID del usuario: ${member.id}_
              > 
              > ${interaction.user}
            `,
            components: [],
          });

          return;
          //
        } else {
          throw data;
        }
      } catch (err) {
        await confirmation.update({
          content: `
            > :warning:  **Error**
            > ¡Hola! Ocurrió un problema al intentar remover la penalización por favor, comunícate con ${ADMIN_MENTORS}.
            > 
            > _ID del usuario: ${member.id}_
          `,
          components: [],
        });

        return console.error(err);
      }
    } else if (ACTION_CANCEL === confirmation.customId) {
      await confirmation.update({
        content: `Acción cancelada, no se ha removido la penalización de ${member}.`,
        components: [],
      });

      return;
    }

    // Confirmation timeouts.
  } catch (err) {
    await interaction.editReply({
      content: "No se ha recibido una confirmación en 1 minuto.",
      components: [],
    });

    return console.log(err);
  }
}
