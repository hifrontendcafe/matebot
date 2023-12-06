import "dotenv/config";
import { ZodError, z } from "zod";

export const isDev = process.env.NODE_ENV !== "production";
export const isProd = !isDev;

const envVariables = z.object({
  DISCORD_TOKEN: z.string().trim().min(1),
  CLIENT_ID: z.string().trim().min(1),
  GUILD_ID: z
    .string()
    .trim()
    .min(
      1,
      "Required in development to deploy the commands for a specific Discord server"
    ),
  AWS_URL: z.string().trim().url().endsWith("/"),
  AWS_API_KEY: z.string().trim().min(1),
  FAUNADB_SECRET_KEY: z.string().trim().min(1),
  NODE_ENV: z
    .enum(["development", "production", "test"])
    .default("development"),
});

try {
  envVariables.parse(process.env);
} catch (error) {
  if (!(error instanceof ZodError)) console.error("error");
  else {
    throw error.format();
  }
}

declare global {
  namespace NodeJS {
    interface ProcessEnv extends z.infer<typeof envVariables> {}
  }
}

export const {
  DISCORD_TOKEN,
  CLIENT_ID,
  GUILD_ID,
  AWS_URL,
  AWS_API_KEY,
  FAUNADB_SECRET_KEY,
} = process.env;
