import {
  CommandInteraction,
  SlashCommandBuilder,
  SlashCommandUserOption,
} from "discord.js";
import { globSync } from "glob";
import path from "node:path";
import { fileURLToPath } from "url";
import { TARGET_OPTIONS } from "./constants.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

interface Command {
  data: SlashCommandBuilder;
  execute: (interaction: CommandInteraction) => void;
}
/**
 * Resolves the directory `commands` and returns the slash command definitions.
 */
export async function resolveCommands() {
  // Get all files in `commands` dir, except those starting with undercore "_".
  const cmdFiles = globSync(`${__dirname}/../commands/**/*.{js,ts}`, {
    ignore: {
      ignored: (file) => file.name.startsWith("_"),
    },
  });

  const commands = cmdFiles.map(async (file) => {
    const cmd = await import(path.resolve(file));

    if ("data" in cmd && "execute" in cmd) {
      return cmd;
    } else {
      console.log(
        `[WARNING] The command at ${file} is missing a required "data" or "execute" property.`
      );
    }
  });

  return (await Promise.all(commands)).filter(Boolean) as Command[];
}

export function userToMention(option: SlashCommandUserOption) {
  return option
    .setName(TARGET_OPTIONS.USERNAME)
    .setDescription("Mencionar a un usuario")
    .setRequired(true);
}
