import { CacheType, Interaction, SlashCommandBuilder } from "discord.js";
import { EMOJI_NUMBERS } from "../libs/constants.js";

const data = new SlashCommandBuilder()
  .setName("poll")
  .setDescription(
    "Crear una encuesta básica de Sí/No. O cree uno con múltiples opciones (10 como máximo)."
  )
  .setDefaultMemberPermissions(0)
  .setDMPermission(false)
  .addStringOption((option) =>
    option
      .setName("question")
      .setDescription("Pregunta de la encuesta")
      .setRequired(true)
  )
  .addStringOption((option) =>
    option
      .setName("option-1")
      .setDescription("Opción numero 1")
      .setRequired(true)
  )
  .addStringOption((option) =>
    option
      .setName("option-2")
      .setDescription("Opción numero 2")
      .setRequired(true)
  );
const targetOptions = EMOJI_NUMBERS.map((emoji, i) => ({
  name: `option-${i + 1}`,
  description: `Opción numero ${i + 1}`,
  emoji,
}));
targetOptions.slice(2).forEach(({ name, description }) => {
  return data.addStringOption((option) =>
    option.setName(name).setDescription(description)
  );
});
export { data };

export async function execute(interaction: Interaction<CacheType>) {
  if (!interaction.isChatInputCommand() || !interaction.channel) return;

  const question = interaction.options.getString("question", true);
  const options = targetOptions
    .map((option) => interaction.options.getString(option.name))
    .filter(Boolean);

  const simplePoll = options.length === 2;

  await interaction.deferReply();

  const message = await interaction.channel.send({
    embeds: [
      {
        color: 0x00c29d,
        author: {
          name: "Encuestas - FrontendCafé",
        },
        thumbnail: {
          url: "https://res.cloudinary.com/sebasec/image/upload/v1614807768/Fec_with_Shadow_jq8ll8.png",
        },
        title: question,
        fields: options.map((option, i) => {
          return {
            name:
              simplePoll && i === 0
                ? `✅ ${option || "Si"}`
                : simplePoll && i === 1
                ? `❎ ${option || "No"}`
                : `${targetOptions[i]?.emoji} ${option}`,
            value: "",
            inline: simplePoll,
          };
        }),
      },
    ],
  });

  try {
    const reactions = options.map(async (_, i) =>
      message.react(
        simplePoll && i === 0
          ? "✅"
          : simplePoll && i === 1
          ? "❎"
          : targetOptions[i]?.emoji!
      )
    );
    await Promise.all(reactions);
  } catch (error) {
    console.error(error);
  }

  const collector = message.createReactionCollector({
    filter: (reaction, user) =>
      (reaction.emoji.name === "✅" && user.id !== message.author.id) ||
      (reaction.emoji.name === "❎" && user.id !== message.author.id),
    time: 15000,
  });

  collector.on("collect", (reaction, user) => {
    console.log(`Collected ${reaction.emoji.name} from ${user.tag}`);
  });

  collector.on("end", (collected) => {
    console.log(`Collected ${collected.size} items`);
  });

  interaction.deleteReply();
}
