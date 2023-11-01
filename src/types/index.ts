import { Events } from "discord.js";

export interface DiscordCommand {
  data: unknown;
  execute: (arg: any) => Promise<void> | void;
}

export interface DiscordEvent {
  name: (typeof Events)[keyof typeof Events];
  once?: true;
  execute: (arg: any) => Promise<any> | any;
}
