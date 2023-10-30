import { Client, Collection, Events, GatewayIntentBits } from "discord.js";
import { DISCORD_TOKEN } from "./libs/environment.js";
import { resolveCommands } from "./libs/helpers.js";

// Create a new client instance
const client = new Client({ intents: [GatewayIntentBits.Guilds] });

// Load command files
client.commands = new Collection();
const commands = await resolveCommands();
commands.forEach((command) => {
  client.commands.set(command.data.name, command);
});

// When the client is ready, run this code (only once)
client.once(Events.ClientReady, (c) => {
  console.log(`Ready! Logged in as ${c.user.tag}`);
});

// Receiving command interactions
client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  const command = interaction.client.commands.get(interaction.commandName);

  if (!command) {
    console.error(`No command matching ${interaction.commandName} was found.`);
    return;
  }

  try {
    await command.execute(interaction);
  } catch (error) {
    console.error(error);
    if (interaction.replied || interaction.deferred) {
      await interaction.followUp({
        content: "There was an error while executing this command!",
        ephemeral: true,
      });
    } else {
      await interaction.reply({
        content: "There was an error while executing this command!",
        ephemeral: true,
      });
    }
  }
});

// Log in to Discord with your client's token
client.login(DISCORD_TOKEN);
