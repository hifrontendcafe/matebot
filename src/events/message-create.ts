import { Events, Message } from "discord.js";
import { DISCORD_PREFIX } from "../libs/environment.js";
import { DiscordEvent } from "../types/index.js";

export default {
  name: Events.MessageCreate,
  async execute(message: Message<boolean>) {
    if (message.author.bot || !DISCORD_PREFIX) return;

    let args: string[];

    //  Handle messages in a guild
    if (message.guild) {
      if (!message.content.startsWith(DISCORD_PREFIX)) return;

      args = message.content.slice(DISCORD_PREFIX.length).trim().split(/\s+/);
    } else {
      // handle DMs
      const slice = message.content.startsWith(DISCORD_PREFIX)
        ? DISCORD_PREFIX?.length
        : 0;

      args = message.content.slice(slice).split(/\s+/);
    }

    // Get the first space-delimited argument after the prefix as the command
    const commandName = args.shift()?.toLowerCase();

    const command = message.client.commands.get(commandName);

    if (!command) {
      const errorMsg = `No command matching "${commandName}" was found.`;

      console.error(errorMsg);
      return message.reply(errorMsg);
    }

    // Calls the slash command, if exists.
    await command.execute(message);
  },
} satisfies DiscordEvent;
