import { CacheType, Interaction, SlashCommandBuilder } from "discord.js";

export const data = new SlashCommandBuilder()
  .setName("ping")
  .setDescription("Replies with Pong!");

export async function execute(interaction: Interaction<CacheType>) {
  if (!interaction.isChatInputCommand()) return;
  await interaction.reply("Pong!");
}
