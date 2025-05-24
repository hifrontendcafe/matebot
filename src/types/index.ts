import { Events } from "discord.js";

/**
 * @public
 * TODO: This interface is not used anywhere, maybe we should remove it
 */
export interface DiscordCommand {
  data: unknown;
  execute: (arg: unknown) => Promise<void> | void;
}

export interface DiscordEvent<InteractionType> {
  name: (typeof Events)[keyof typeof Events];
  once?: true;
  execute: (arg: InteractionType) => Promise<void> | void;
}
