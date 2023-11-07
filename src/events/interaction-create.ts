import { CacheType, Events, Interaction } from "discord.js";
import { DiscordEvent } from "../types/index.js";

export default {
  name: Events.InteractionCreate,
  async execute(interaction: Interaction<CacheType>) {
    if (!interaction.isChatInputCommand()) return;

    const command = interaction.client.commands.get(interaction.commandName);

    if (!command) {
      console.error(
        `No command matching "${interaction.commandName}" was found.`
      );
      return;
    }

    try {
      await command.execute(interaction);
    } catch (error) {
      console.error(error);
      if (interaction.replied || interaction.deferred) {
        await interaction.followUp({
          content: "¡Hubo un error al ejecutar este comando!",
          ephemeral: true,
        });
      } else {
        await interaction.reply({
          content: "¡Hubo un error al ejecutar este comando!",
          ephemeral: true,
        });
      }
    }
  },
} satisfies DiscordEvent;
