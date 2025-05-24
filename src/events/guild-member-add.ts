import { Events, GuildMember, channelMention } from "discord.js";
import { CHANNELS } from "../libs/constants.js";
import { DiscordEvent } from "../types/index.js";

const GENERAL = channelMention(CHANNELS.GENERAL);
const USER_GUIDE = channelMention(CHANNELS.USER_GUIDE);
const CODE_OF_CONDUCT = channelMention(CHANNELS.CODE_OF_CONDUCT);

async function sendWelcomeMessage(member: GuildMember) {
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
}

export default {
  name: Events.GuildMemberAdd,
  async execute(member: GuildMember) {
    // Direct messages new members with a welcome message.
    await sendWelcomeMessage(member);
  },
} satisfies DiscordEvent;
