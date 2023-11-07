import "dotenv/config";

export const {
  DISCORD_TOKEN,
  CLIENT_ID,
  GUILD_ID,
  DISCORD_PREFIX,
  AWS_URL,
  AWS_API_KEY,
} = process.env;
export const isDev = process.env.NODE_ENV !== "production";
export const isProd = !isDev;
