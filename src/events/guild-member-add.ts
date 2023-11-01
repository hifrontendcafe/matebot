import { Events, GuildMember, channelMention } from "discord.js";
import { DiscordEvent } from "../types/index.js";

const CODE_OF_CONDUCT_CHANNEL = channelMention("748183026244255824");
const USER_GUIDE_CHANNEL = channelMention("747925827265495111");
const GENERAL_CHANNEL = channelMention("594935077637718027");
// FIXME: This channel does not exists.
const UNKNOWN_CHANNEL = channelMention("748547143157022871");

export default {
  name: Events.GuildMemberAdd,
  async execute(member: GuildMember) {
    await member.send(
      `Hola, te damos la bienvenida a FrontendCafé!!
      
      Somos una comunidad de personas interesadas en tecnología y ciencias informáticas. Conversamos sobre lenguajes de programación, diseño web, infraestructura, compartimos dudas y tratamos de resolverlas en conjunto.  
      Además, nos organizamos en grupos para estudiar, hacer proyectos en equipo y practicar en inglés para perfeccionarnos. Tenemos un espacio de coworking, también nos vamos de after office y jugamos jueguitos!  
  
      Aquí abajo dejamos información que **es necesaria que revises antes de comenzar a participar**, yaque es muy importante que contribuyamos a mantener este server como un espacio seguro, amigable y divertido para cualquier persona que participe.  
  
      - Código de conducta ${CODE_OF_CONDUCT_CHANNEL}
      - Manual de uso ${USER_GUIDE_CHANNEL}
  
      Por favor, al hacer una consulta dentro del server, intenta incluir la mayor cantidad de datos posibles sobre qué estás intentando, qué errores encuentras y qué quieres lograr para que podamos ayudarte de la mejor manera posible.  
      
      Si tienes dudas de dónde publicar la pregunta puedes consultar en ${GENERAL_CHANNEL} y te orientarán. Asimismo, puedes usar el buscador, situado arriba a la derecha, para verificar que tu pregunta no haya sido respondida anteriormente.  
      
      Nos encantaría que pases por ${UNKNOWN_CHANNEL} y nos cuentes algo de ti :slight_smile:
      
      Saludos!
      *El Staff de FrontendCafé*`.replace(/  +/g, "")
    );
  },
} satisfies DiscordEvent;
