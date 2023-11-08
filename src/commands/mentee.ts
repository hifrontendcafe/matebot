import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  CacheType,
  ChannelType,
  Interaction,
  SlashCommandBuilder,
  roleMention,
} from "discord.js";
import { ROLES, TARGET_OPTIONS } from "../libs/constants.js";
import { userToMention } from "../libs/helpers.js";
import { postMentorship, postWarning } from "../libs/services.js";

const COMMANDS = {
  MENTEE: "mentee",
  HELP: "help",
  CONFIRM: "confirm",
  REMINDER: "reminder",
  CONCLUDE: "conclude",
  PENALTY: "penalty",
} as const;

const ADMIN_MENTORS = roleMention(ROLES.ADMIN_MENTORS);
const MENTEES = roleMention(ROLES.MENTEES);

export const data = new SlashCommandBuilder()
  .setName(COMMANDS.MENTEE)
  .setDescription("Comandos para las mentorías")
  .setDefaultMemberPermissions(0)
  .setDMPermission(false)
  .addSubcommand((subcommand) =>
    subcommand
      .setName(COMMANDS.HELP)
      .setDescription("Obtén información sobre los comandos `/mentee`")
  )
  .addSubcommand((subcommand) =>
    subcommand
      .setName(COMMANDS.CONFIRM)
      .setDescription(
        "Confirma una mentoría y a la vez verifica si ese usuario tiene penalizaciones."
      )
      .addUserOption(userToMention)
  )
  .addSubcommand((subcommand) =>
    subcommand
      .setName(COMMANDS.REMINDER)
      .setDescription(
        "Agrega rol Mentees y opcionalmente envía un recordatorio al usuario."
      )
      .addUserOption(userToMention)
      .addIntegerOption((option) =>
        option
          .setName(TARGET_OPTIONS.MINUTES)
          .setDescription("Cantidad de minutos")
      )
      .addChannelOption((option) =>
        option
          .setName(TARGET_OPTIONS.CHANNEL)
          .setDescription("Mencionar un canal")
          .addChannelTypes(ChannelType.GuildVoice)
      )
  )
  .addSubcommand((subcommand) =>
    subcommand
      .setName(COMMANDS.CONCLUDE)
      .setDescription(
        "Concluye una mentoría removiendo rol Mentees y enviando el formulario de feedback."
      )
      .addUserOption(userToMention)
  )
  .addSubcommand((subcommand) =>
    subcommand
      .setName(COMMANDS.PENALTY)
      .setDescription(
        "Da una penalización a un mentee por ausencia, adicionalmente puedes agregar un motivo"
      )
      .addUserOption(userToMention)
      .addStringOption((option) =>
        option
          .setName(TARGET_OPTIONS.REASON)
          .setDescription("Motivo de la penalización")
          .setMinLength(10)
      )
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

  if (COMMANDS.HELP === subcommand) {
    return await interaction.reply({
      ephemeral: true,
      embeds: [
        {
          color: 0x00c29d,
          title: "Mentee Command Guide",
          description:
            "Información sobre comandos `/mentee`\nLos comandos que terminan con un **?** son opcionales.",
          thumbnail: {
            url: "https://res.cloudinary.com/sebasec/image/upload/v1614807768/Fec_with_Shadow_jq8ll8.png",
          },
          fields: [
            {
              name: "/mentee confirm `@usuario`",
              value:
                "Confirma una mentoría y a la vez verifica si ese usuario tiene penalizaciones.",
            },
            {
              name: "/mentee reminder `@usuario` `<minutes?>` `<channel?>`",
              value:
                "Agrega rol Mentees y opcionalmente envía un recordatorio al mentee indicando le los minutos y/o el canal.",
            },
            {
              name: "/mentee conclude `@usuario`",
              value:
                "Concluye una mentoría removiendo rol Mentees y enviando el formulario de feedback.",
            },
            {
              name: "/mentee penalty `@usuario` `<motivo?>`",
              value:
                'Da una penalización a un mentee con motivo "Ausencia a la mentoría", adicionalmente puedes agregar un motivo personalizado.',
            },
          ],
        },
      ],
    });
  }

  // Options from commands, the username option is required.
  const user = interaction.options.getUser(TARGET_OPTIONS.USERNAME, true);
  const reason = interaction.options.getString(TARGET_OPTIONS.REASON);
  const time = interaction.options.getInteger(TARGET_OPTIONS.MINUTES);
  const channel = interaction.options.getChannel(
    TARGET_OPTIONS.CHANNEL,
    false,
    [ChannelType.GuildVoice]
  );

  const role = interaction.guild?.roles.cache.get(ROLES.MENTEES);
  if (!role) {
    const message = `> No se pudo encontrar el rol con ID: ${ROLES.MENTEES}`;
    await interaction.reply({ ephemeral: true, content: message });
    return console.log(message);
  }

  const member = await interaction.guild?.members
    .fetch(user.id)
    .catch(console.error);
  if (!member) {
    const message = `> No se pudo encontrar a ${user}.`;
    await interaction.reply({ ephemeral: true, content: message });
    return console.log(message);
  }

  const memberHasRole = member.roles.cache.has(role.id);

  // Confirms a mentorship appointment.
  if (COMMANDS.CONFIRM === subcommand) {
    try {
      await interaction.deferReply({ ephemeral: true });

      const data = await postMentorship({
        authorId: interaction.user.id,
        authorUsername: interaction.user.displayName,
        menteeId: member.id,
        menteeUsername: member.displayName,
      });

      if (data["code"] === "-118") {
        await interaction.channel?.send(`
          > :no_entry:  **Solicitud de mentoría rechazada**
          > ¡Hola! ${member} la mentoría no se llevara a cabo ya que anteriormente has sido penalizado por no cumplir el código de conducta. Si crees que fue un error, comunícate con ${ADMIN_MENTORS}.
          > 
          > _ID del usuario: ${member.id}_
        `);
      } else if (data["code"] === "100") {
        await interaction.channel?.send(`
          > :white_check_mark:  **Solicitud de mentoría exitosa**
          > ¡Hola! La mentoría de ${member} ha sido registrada satisfactoriamente.
          > Tu mentor asignado es ${interaction.user}
          > 
          > _ID del usuario: ${member.id}_
        `);
      } else {
        throw data;
      }
    } catch (err) {
      await interaction.editReply(`
        > :warning:  **Error**
        > ¡Hola! Ocurrió un problema al registrar la mentoría, por favor comunícate con ${ADMIN_MENTORS}.
        > 
        > _ID del usuario: ${member.id}_
      `);

      return console.error(err);
    }

    return await interaction.deleteReply();
  }

  // Adds the 'Mentees' role and sends a reminder.
  if (COMMANDS.REMINDER === subcommand) {
    await member.roles.add(role);

    // Inform the author that the role has been added.
    if (!memberHasRole) {
      await interaction.reply({
        ephemeral: true,
        content: `> Se ha agregado el rol ${MENTEES} a ${member}.`,
      });
    } else if (memberHasRole && !time && !channel) {
      await interaction.reply({
        ephemeral: true,
        content: `> El rol ${MENTEES} ya ha sido asignado a ${member} previamente.`,
      });
    } else {
      await interaction.deferReply();
      await interaction.deleteReply();
    }

    const minutes = `minuto${time === 1 ? "" : "s"}`;

    // Sends a remainder with the estimated time and assigned channel.
    if (time && channel) {
      return await interaction.channel?.send(`
        > :alarm_clock:  **Recordatorio**
        > Hola ${member}, en ${time} ${minutes} ${interaction.user} te espera en la sala de voz ${channel} <:fecfan:756224742771654696>
      `);
    }
    // Sends a remainder with the estimated time.
    if (time && !channel) {
      return await interaction.channel?.send(`
        > :alarm_clock:  **Recordatorio**
        > Hola ${member}, ${interaction.user} te espera en ${time} ${minutes}  <:fecfan:756224742771654696>
      `);
    }
    // Sends a remainder with the assigned channel.
    if (!time && channel) {
      return await interaction.channel?.send(`
        > :alarm_clock:  **Recordatorio**
        > Hola ${member}, ${interaction.user} te espera en la sala de voz ${channel} <:fecfan:756224742771654696>
      `);
    }
  }

  // Conclude a mentorship by removing the 'Mentees' role and sending the feedback form.
  if (COMMANDS.CONCLUDE === subcommand) {
    if (!memberHasRole) {
      await interaction.reply({
        ephemeral: true,
        content: `> No se ha encontrado el rol ${MENTEES} en ${member}.`,
      });
      return;
    }

    await member.roles.remove(role);

    await interaction.reply({
      ephemeral: true,
      content: `> Se ha removido el rol ${MENTEES} de ${member}.`,
    });

    await interaction.channel?.send(`
      > :pray: ${member} esperamos que hayas tenido una buena experiencia, recuerda darnos feedback para continuar mejorando!
      > https://go.frontend.cafe/feedback
    `);

    return;
  }

  // Adds a penalty to a mentee
  if (COMMANDS.PENALTY === subcommand) {
    const date = new Date().toLocaleDateString("es");

    const response = await interaction.reply({
      ephemeral: true,
      content: `Confirma si deseas aplicar una penalización a ${member}${
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
          const [data] = await Promise.all([
            postWarning({
              authorId: interaction.user.id,
              authorUsername: interaction.user.displayName,
              menteeId: member.id,
              menteeUsername: member.displayName,
              warnCause: reason,
            }),
            member.roles.remove(role),
          ]);

          if (data["code"] === "300") {
            await interaction.channel?.send(`
              > :triangular_flag_on_post:  **${member} ha sido penalizado/a**
              > 
              > _**Motivo**: ${reason || "Ausencia a la mentoría"}_
              > _**Fecha**: ${date}_
              > 
              > _ID del usuario: ${member.id}_
              > 
              > \`${interaction.user}\`
            `);

            return await interaction.deleteReply();
            //
          } else {
            throw data;
          }
        } catch (error) {
          await confirmation.update({
            content: `
              > :warning:  **Error**
              > ¡Hola! Ocurrió un problema al registrar la penalización, por favor comunícate con ${ADMIN_MENTORS}.
              > 
              > _ID del usuario: ${member.id}_
            `,
            components: [],
          });

          return console.log(error);
        }
      } else if (ACTION_CANCEL === confirmation.customId) {
        await confirmation.update({
          content: `Acción cancelada, no se ha aplicado una penalización a ${member}`,
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
}
