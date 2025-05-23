# FrontendCafé's Discord Bot

## Commands

<details>
  <summary>
    This bot currently supports the following commands
  </summary>
  </br>

> [!note]
> Subcommands ending with a question mark (?) are optional.

### Mentorships Command Guide

- **`/mentee confirm`** `@username`

  Confirm a mentorship while also verifying whether the user has any penalties.

- **`/mentee reminder`** `@username` `<minutes?>` `<channel?>`

  Assign the "Mentees" role and, optionally, send a reminder to the mentee about the minutes and/or channel.

- **`/mentee conclude`** `@username`

  Conclude the mentorship and submit the feedback form. This will also remove the "Mentees" role.

- **`/mentee penalty`** `@username` `<reason?>`

  Penalize a mentee for absence. You can also add a custom reason if needed.

- **`/mentee help`**

  Provides information about the mentorship commands.

- **`/remove penalty`**

  Remove a penalty from a mentee

### Poll Command Guide

- **`/poll`** `<question>` `<"yes" option>` `<"no" option>` `<options?>`

  Create a basic Yes/No poll. Or, create one with multiple options (10 max).

  > [!note]
  > For the basic (two options) poll, the first option should be "positive" and the second "negative".
  > Adding more than two options will add numbers instead.

### Info Command Guide

- **`/info q`** `@username`

  Provide a specific user with tips for asking questions.

- **`/info m`** `@username`

  Alert a specific user about the music bot commands.

### Help Command Guide

- **`/help`**

  Offers comprehensive information on all available commands.

---

</details>

## Getting Started

These instructions will help you install and run the project on your local machine for development.

### Installation

To install the project locally, follow these steps:

1. Create an `.env` file and add the environment variables needed, you can find the environment variables you'll need in the [`.env.example`](.env.example) file.
2. Install project dependencies by running the command:

   ```bash
   pnpm install
   ```

### Development

To run the project locally, execute:

> [!NOTE]
> The first time running may require re-execute the command.

```bash
pnpm run dev
```

The development server should reload on every file change.

> [!IMPORTANT]
> After creating new commands or making changes on any of the commands structure you'll need to [redeploy them](#deployingregistering-commands).

<details>
  <summary><h4>Creating New Commands</h4></summary></br>

To create a new command, create a new file in the **[commands](src/commands)** directory. The file name should match the name of the command. For example, to create a command called _hello_, create a file called _`hello.js`_.

The command file should export both `data` and `execute` [as seem here](src/commands/testing/_ping.ts).

> [!WARNING]
> Make sure you put every command file inside the **[`src/commands`](src/commands)** folder or in it's subfolders.

---

</details>

<details>
  <summary><h4>Handle Discord Events</h4></summary>

To handle an event, create a new file in the **[events](src/events)** directory. The file name should match the name of the event. For example, to handle the _messageCreate_ event, create a file called _`message-create.js`_.

The event file should export both `data` and `execute` from each event file, [as seem here](src/events/ready.ts).

> [!WARNING]
> Make sure you put every event file inside the **[`src/events`](src/events)** folder or in it's subfolders.

---

</details>

### Deployment

Deployment is done automatically with GitHub Actions; If you need to redeploy it manually, follow these steps:

1. Install the Fly.io CLI [from their website](https://fly.io/docs/hands-on/install-flyctl/)
2. Authenticate with FrontendCafe's Fly.io account.

   ```bash
   flyctl auth login
   ```

3. Execute the deploy command

   ```bash
   flyctl deploy --ha=false
   ```

#### Deploying/Registering Commands

After creating new commands or making changes on any of the commands structure _(not the `execute` function logic)_, you will need to run:

```bash
pnpm run register
```

> [!WARNING]
> If the `NODE_ENV` variable is set to `"production"`, it will deploy the commands **globally** to all servers were the bot is already invited.

#### Update the environment variables

To modify environment variables on Fly.io, run the following command:

```bash
flyctl secrets import < .env
```

> [!important]
> This will read your local `.env` file and update all of the environment variables.

## License

This project is licensed under the [MIT License](./LICENSE).
