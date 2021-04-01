# Proyecto Frontend Cafe Bot

Funciones del bot:

- [x] Bienvenida:
    - Da la bienvenida a los usuarios que entrar al server por primera vez.
- [x] FAQ:
    - Muestra una serie de preguntas y respuestas habituales para conocer el funcionamiento del server FrontEndCafe.
- [x] Publicación de eventos via twitter:
    - El bot publica eventos emitidos en twitter disparados por un hashtag en especifico a un canal del server en particular (privado para el server).
- [x] Recordatorios de eventos:
    - El bot envía recordatorios con cierta frecuencia antes del evento (de uso general).
- [x] Generador de encuestas:
    - Permte genera encuestas, hacer votaciones y finalizarlas.
- [x] Busquedas web:
    - Permite buscar mediante palabras clave y mostrar los resultados encontrados.

## Instalación

```
git clone https://github.com/frontendcafe/matebot
cd matebot
pip3 install -r requirements.txt
```

Variables de entorno:
Estas variables pueden estar colocadas en un archivo `.env` dentro de la carpeta `matebot`.

```bash
DISCORD_PREFIX=<my_discord_prefix> # !
DISCORD_TOKEN=<my_token>
FAUNADB_SECRET_KEY=<my_faunadb_secret_key>
EVENTS_CHANNEL_ID=<my_events_channel_id> # channel id de discord para publicar los tweets
TWITTER_API_KEY=<twitter_api_key>
TWITTER_API_SECRET=<twitter_api_secret>
TWITTER_ACCESS_KEY=<twitter_access_key>
TWITTER_ACCESS_SECRET=<twitter_access_secret>
TWITTER_USER_URL=<twitter_user_url> # https://twitter.com/frontendcafe
TWITTER_FILTER=<twitter_filter> # FECEvents
```

Inicio el bot:

```
python3 src/bot.py
```


[Licencia MIT](./LICENSE)
