# Proyecto Frontend Cafe Bot

Funciones del bot:

- [ ] Bienvenida:
    - Da la bienvenida a los usuarios que entrar al server por primera vez.
- [ ] FAQ:
    - Muestra una serie de preguntas y respuestas habituales para conocer el funcionamiento del server FrontEndCafe.
- [ ] Publicación de anuncios:
    - El bot publica los eventos del server (privado para el server).
- [ ] Recordatorios de eventos:
    - El bot envía recordatorios con cierta frecuencia antes del evento (de uso general).

## Instalación

```
git clone https://github.com/hifrontendcafe/matebot
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
TWITTER_FILTER=<twitter_filter> # #FECEvents
```

Inicio el bot:

```
python3 src/bot.py
```


[Licencia MIT](./LICENSE)
