# FrontendCafé's Discord Bot

## Commands

<details>
  <summary>
    This bot currently supports the following commands
  </summary>
  </br>

### Mentorships Command Guide

Information about `/mentee` commands. Subcommands ending with **?** are optional.

- **`/mentee confirm`** `@username`

  Confirm a mentorship and at the same time verify if that user has penalties.

- **`/mentee reminder`** `@username` `<minutes?>` `<channel?>`

  Add Mentees role and optionally send a reminder to the mentee indicating the minutes and/or channel.

- **`/mentee conclude`** `@username`

  Conclude a mentorship by removing Mentees role and sending the feedback form.

- **`/mentee penalty`** `@username` `<reason?>`

  Give a penalty to a mentee with the reason "Ausencia a la mentoría", you can additionally add a custom reason

- **`/remove penalty`** `@username` `<reason?>`

  Remove a penalty from a mentee, additionally you can add a custom reason.

- **`/mentee help`**

### Info Command Guide

- **`/info help`**
- **`/info q`**
- **`/info b`**

### Help Command Guide

- **`/help`**

  Displays a list of available commands

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

```bash
pnpm run dev
```

The development server should reload on every file change.

> [!NOTE]
> The first time running may require re-launch the command.

<details>
  <summary><h4>Creating New Commands</h4></summary></br>

To create a new command, create a new file in the **[commands](src/commands)** directory. The file name should match the name of the command. For example, to create a command called _hello_, create a file called _`hello.js`_.

The command file should export both `data` and `execute` [as seem here](src/commands/testing/_ping.ts).

> [!WARNING]
> Make sure you put every command file inside the **[`src/commands`](src/commands)** folder or in it's subfolders.

---

</details>

#### Registering/Deploying Commands

After creating new commands or making changes on any of the commands structure _(not the `execute` function logic)_, you will need to run:

```bash
pnpm run register
```

> [!WARNING]
> If the `NODE_ENV` variable is set to `"production"`, it will deploy the commands **globally** to all servers were the bot is already invited.

<details>
  <summary><h4>Handle Discord Events</h4></summary>

To handle an event, create a new file in the **[events](src/events)** directory. The file name should match the name of the event. For example, to handle the _messageCreate_ event, create a file called _`message-create.js`_.

The event file should export both `data` and `execute` from each event file, [as seem here](src/events/ready.ts).

> [!WARNING]
> Make sure you put every event file inside the **[`src/events`](src/events)** folder or in it's subfolders.

---

</details>

### Deployment

```bash
pnpm run build
```

```bash
pnpm run start
```

## License

This project is licensed under the [MIT License](./LICENSE).
