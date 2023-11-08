import { REST, Routes } from "discord.js";
import {
  CLIENT_ID,
  DISCORD_TOKEN,
  GUILD_ID,
  isProd,
} from "./libs/environment.js";
import { resolveCommands } from "./libs/helpers.js";

const commands = await resolveCommands();

const rest = new REST().setToken(DISCORD_TOKEN);

(async () => {
  try {
    console.log(
      `Started refreshing ${commands.length} application (/) commands.`
    );

    // The put method is used to fully refresh all commands in the guild (in dev), or globally.
    const data = await rest.put(
      isProd
        ? Routes.applicationCommands(CLIENT_ID)
        : Routes.applicationGuildCommands(CLIENT_ID, GUILD_ID),

      { body: commands.map((command) => command.data.toJSON()) }
    );

    console.log(
      /* @ts-expect-error unknown type */
      `Successfully reloaded ${data.length} application (/) commands.`
    );
  } catch (error) {
    console.error(error);
  }
})();
