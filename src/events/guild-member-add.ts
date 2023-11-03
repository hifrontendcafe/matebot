import {
  Events,
  GuildMember,
  User,
  channelMention,
  formatEmoji,
} from "discord.js";
import { DiscordEvent } from "../types/index.js";

const CHANNEL = {
  TEST: channelMention("861980330201841686"),
  GENERAL: channelMention("594935077637718027"),
  USER_GUIDE: channelMention("747925827265495111"),
  CODE_OF_CONDUCT: channelMention("748183026244255824"),
// FIXME: This channel does not exists.
  UNKNOWN: channelMention("748547143157022871"),
} as const;

const EMOJI = {
  // '<:fecimpostor:755971090471321651>'
  impostor: formatEmoji("755971090471321651"),
  // '<:fecstar:755451362950512660>'
  fec_star: formatEmoji("755451362950512660"),
} as const;

export default {
  name: Events.GuildMemberAdd,
  async execute(member: GuildMember) {
    // Direct messages new members with a welcome message.
    await member.send(
      `Hola, te damos la bienvenida a FrontendCafé!!
      
      Somos una comunidad de personas interesadas en tecnología y ciencias informáticas. Conversamos sobre lenguajes de programación, diseño web, infraestructura, compartimos dudas y tratamos de resolverlas en conjunto.  
      Además, nos organizamos en grupos para estudiar, hacer proyectos en equipo y practicar en inglés para perfeccionarnos. Tenemos un espacio de coworking, también nos vamos de after office y jugamos jueguitos!  
  
      Aquí abajo dejamos información que **es necesaria que revises antes de comenzar a participar**, yaque es muy importante que contribuyamos a mantener este server como un espacio seguro, amigable y divertido para cualquier persona que participe.  
  
      - Código de conducta ${CHANNEL.CODE_OF_CONDUCT}
      - Manual de uso ${CHANNEL.USER_GUIDE}
  
      Por favor, al hacer una consulta dentro del server, intenta incluir la mayor cantidad de datos posibles sobre qué estás intentando, qué errores encuentras y qué quieres lograr para que podamos ayudarte de la mejor manera posible.  
      
      Si tienes dudas de dónde publicar la pregunta puedes consultar en ${CHANNEL.GENERAL} y te orientarán. Asimismo, puedes usar el buscador, situado arriba a la derecha, para verificar que tu pregunta no haya sido respondida anteriormente.
      
      Nos encantaría que pases por ${CHANNEL.UNKNOWN} y nos cuentes algo de ti :slight_smile:
      
      Saludos!
      *El Staff de FrontendCafé*`.replace(/  +/g, "")
    );

    const storedUsers = getList();
    if (!storedUsers) {
      console.error(
        "No se pudo encontrar lista de usuarios en la base de datos."
      );
      return;
    }

    let dbUserIds = storedUsers.newUsersId;
    let dbUserCount = storedUsers.userCondition;
    const time_zero = storedUsers.timeSec;
    const delta = storedUsers.timeDelta;

    dbUserIds.push(member.id);

    if (dbUserIds.length === dbUserCount) {
      const time_final = Date.now() || +new Date();
      const new_delta = time_final - time_zero;

      if (delta < new_delta && dbUserCount >= 20) {
        dbUserCount -= 1;
      } else {
        dbUserCount += 1;
      }

      // Find a specific channel by the ID.
      const channel = member.client.channels.cache.get(CHANNEL.GENERAL);
      if (!channel || !channel.isTextBased()) {
        const reason =
          channel && !channel.isTextBased()
            ? "No es un canal de texto."
            : "El canal no existe.";

        console.error(
          `No se ha podido enviar el mensaje al canal con ID: ${CHANNEL.GENERAL}. ${reason}`
        );
        return;
      }

      const newMembers = dbUserIds
        // Finds users on the server from IDs stored in the database
        .map((userId) => member.client.users.cache.get(userId))
        // Filter users who are not in the server
        .filter((newUser): newUser is User => Boolean(newUser))
        // Returns a comma-separated list of mentionable usernames.
        .join(", ");

      dbUserIds = [];
      updateList(dbUserIds, dbUserCount, time_final, new_delta);

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
            description: `Pueden presentarse en este canal, ${CHANNEL.GENERAL} y leer el ${CHANNEL.USER_GUIDE} para conocer cómo participar en nuestra comunidad ${EMOJI.impostor}`,
          },
        ],
      });

      //
    } else {
      updateList(dbUserIds, dbUserCount, time_zero, delta);
      }
  },
} satisfies DiscordEvent;

/**
 * - Descripción: Obtiene la lista de usuarios nuevos y otros parámetros para análisis
 * - Precondición: Debe existir la colección con el documento
 * - Poscondición: Se obtiene la lista de usuarios nuevos, la condición de usuarios nuevos, el tiempo de inicio y el tiempo de espera
 * @returns
 */
function getList() {
  try {
    // const doc = db.get('Users', '292960205647380995')["data"]

    return {
      newUsersId: ["0"], // doc["new_users_id"],
      userCondition: 0, // doc["user_condition"],
      timeSec: 0, // doc["time_sec"],
      timeDelta: 0, // doc["time_delta"],
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
function updateList(
  list_users: string[],
  users: number,
  time_zero: number,
  delta: number
) {
  try {
    // const doc = db.db.update('Users', '292960205647380995', {
    //   "new_users_id": list_users,
    //   "user_condition": users,
    //   "time_sec": time_zero,
    //   "time_delta": delta
    // })
    // return (doc)
  } catch (error) {
    console.error(`Hubo un error en updateList: ${error}`);
  }
}
