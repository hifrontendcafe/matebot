import { Client, Collection, GatewayIntentBits } from "discord.js";
import { globSync } from "glob";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { DISCORD_TOKEN } from "./libs/environment.js";
import { resolveCommands } from "./libs/helpers.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Create a new client instance
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildMessageReactions,
    GatewayIntentBits.GuildMembers,
  ],
});

// Load command files
client.commands = new Collection();
const commands = await resolveCommands();
commands.forEach((command) => {
  client.commands.set(command.data.name, command);
});

// Load events files
const eventFiles = globSync(`${__dirname}/events/**/*.{js,ts}`, {
  ignore: {
    ignored: (file) => file.name.startsWith("_"),
  },
});

// Receiving command interactions
eventFiles.map(async (file) => {
  const { default: event } = await import(path.resolve(file));

  if (event.once) {
    client.once(event.name, (...args) => event.execute(...args));
  } else {
    client.on(event.name, (...args) => event.execute(...args));
  }
});

// Log in to Discord with your client's token
client.login(DISCORD_TOKEN);
