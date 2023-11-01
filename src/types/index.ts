import { Events } from "discord.js";

export interface DiscordEvent {
  name: (typeof Events)[keyof typeof Events];
  once?: true;
  execute: (arg: any) => Promise<void> | void;
}
