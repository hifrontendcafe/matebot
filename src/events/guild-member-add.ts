import { Events, GuildMember, User, channelMention } from "discord.js";
import { CHANNELS, EMOJIS } from "../libs/constants.js";
import { DiscordEvent } from "../types/index.js";
import { getUserList, updateUserList } from "../database/queries.js";

const GENERAL = channelMention(CHANNELS.GENERAL);
const USER_GUIDE = channelMention(CHANNELS.USER_GUIDE);
const CODE_OF_CONDUCT = channelMention(CHANNELS.CODE_OF_CONDUCT);

export default {
  name: Events.GuildMemberAdd,
  async execute(member: GuildMember) {
    // Direct messages new members with a welcome message.
    try {
      await member.send(
        `Hola, te damos la bienvenida a FrontendCafé!!
  
        Somos una comunidad de personas interesadas en tecnología y ciencias informáticas. Conversamos sobre lenguajes de programación, diseño web, infraestructura, compartimos dudas y tratamos de resolverlas en conjunto.
        Además, nos organizamos en grupos para estudiar, hacer proyectos en equipo y practicar en inglés para perfeccionarnos. Tenemos un espacio de coworking, también nos vamos de after office y jugamos jueguitos!
  
        Aquí abajo dejamos información que **es necesaria que revises antes de comenzar a participar**, yaque es muy importante que contribuyamos a mantener este server como un espacio seguro, amigable y divertido para cualquier persona que participe.
  
        - ${CODE_OF_CONDUCT}
        - ${USER_GUIDE}
  
        Por favor, al hacer una consulta dentro del server, intenta incluir la mayor cantidad de datos posibles sobre qué estás intentando, qué errores encuentras y qué quieres lograr para que podamos ayudarte de la mejor manera posible.
  
        Si tienes dudas de dónde publicar la pregunta puedes consultar en ${GENERAL} y te orientarán. Asimismo, puedes usar el buscador, situado arriba a la derecha, para verificar que tu pregunta no haya sido respondida anteriormente.
  
        Saludos!
        *El Staff de FrontendCafé*`.replace(/  +/g, "")
      );
    } catch {
      console.log(`Cannot send DMs to this user.`);
    }

    const storedUsers = await getList();
    if (!storedUsers) {
      console.error(
        "No se pudo encontrar lista de usuarios en la base de datos."
      );
      return;
    }

    const dbUserIds = new Set(storedUsers.newUsersId);
    let dbUserCount = storedUsers.userCondition;
    const timeZero = storedUsers.timeSec;
    const delta = storedUsers.timeDelta;

    dbUserIds.add(member.id);

    if (dbUserIds.size !== dbUserCount) {
      // Update the list of user IDs, and leave the rest as it was.
      await updateList(Array.from(dbUserIds), dbUserCount, timeZero, delta);
      return;
    }

    const timeFinal = Date.now() || +new Date();
    const newDelta = timeFinal - timeZero;

    if (delta < newDelta && dbUserCount >= 20) {
      dbUserCount -= 1;
    } else {
      dbUserCount += 1;
    }

    // Clear the list of user IDs and saves the new times.
    await updateList([], dbUserCount, timeFinal, newDelta);

    // Find a specific channel by the ID.
    const channel = member.client.channels.cache.get(CHANNELS.GENERAL);
    if (!channel || !channel.isTextBased()) {
      const reason =
        channel && !channel.isTextBased()
          ? "No es un canal de texto."
          : "El canal no existe.";

      console.error(
        `No se ha podido enviar el mensaje de bienvenida al canal con ID: ${GENERAL}. ${reason}`
      );
      return;
    }

    // Finds members on the server from IDs stored in the database.
    const guildMembers = Array.from(dbUserIds).map((userId) =>
      member.guild.members.fetch(userId)
    );

    // Filters existing members from a set of guild member promises
    const existingMembers = (await Promise.allSettled(guildMembers)).filter(
      <T>(p: PromiseSettledResult<T>): p is PromiseFulfilledResult<T> =>
        p.status === "fulfilled"
    );

    // Returns a comma-separated list of mentionable usernames.
    const newMembers = existingMembers.map((r) => r.value).join(", ");

    // Sends a message after X number of members have joined the server.
    await channel.send({
      content: `Welcome ${newMembers}!`,
      embeds: [
        {
          color: 0x00c29d,
          title: "",
          thumbnail: {
            url: "https://res.cloudinary.com/sebasec/image/upload/v1614807768/Fec_with_Shadow_jq8ll8.png",
          },
          description: `Pueden presentarse en este canal, ${GENERAL} y leer el ${USER_GUIDE} para conocer cómo participar en nuestra comunidad ${EMOJIS.impostor}`,
        },
      ],
    });
  },
} satisfies DiscordEvent;

/**
 * - Descripción: Obtiene la lista de usuarios nuevos y otros parámetros para análisis
 * - Precondición: Debe existir la colección con el documento
 * - Poscondición: Se obtiene la lista de usuarios nuevos, la condición de usuarios nuevos, el tiempo de inicio y el tiempo de espera
 * @returns
 */
async function getList() {
  try {
    const { data } = await getUserList();

    return {
      newUsersId: data["new_users_id"],
      userCondition: data["user_condition"],
      timeSec: data["time_sec"],
      timeDelta: data["time_delta"],
    };
  } catch (error) {
    console.error(`Hubo un error en getList: ${error}`);
  }
}

/**
 * - Descripción: Actualiza la lista de usuarios nuevos, la condición de usuarios nuevos y el tiempo de espera
 * - Precondición: Debe existir la colección con el documento
 * - Poscondición: La lista de usuarios nuevos, la condición de usuarios nuevos y el tiempo de espera se actualizan
 * @param list_users
 * @param users
 * @param time_zero
 * @param delta
 * @returns
 */
async function updateList(
  list_users: string[],
  users: number,
  time_zero: number,
  delta: number
) {
  try {
    const doc = await updateUserList({
      new_users_id: list_users,
      user_condition: users,
      time_sec: time_zero,
      time_delta: delta,
    });
    return doc;
  } catch (error) {
    console.error(`Hubo un error en updateList: ${error}`);
  }
}
