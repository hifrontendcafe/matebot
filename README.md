# Proyecto: Matebot 🧉🤖

Bot de Discord hecho en Python para la comunidad de FrontendCafé

## Funciones del bot

🟦 **Bienvenida**

Da la bienvenida a los usuarios que entrar al server por primera vez.

🟦 **FAQ**

Muestra una serie de preguntas y respuestas habituales para conocer el funcionamiento del server FrontEndCafe.

🟦 **Recordatorios**

El bot envía recordatorios con cierta frecuencia antes del evento (de uso general).

🟦 **Encuestas**

Permte generar encuestas, hacer votaciones y finalizarlas.

🟦 **Búsquedas web**

Permite buscar mediante palabras clave y mostrar los resultados encontrados.


## Instalación

```
git clone https://github.com/frontendcafe/matebot
cd matebot
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Variables de entorno

Variables necesarias para que Matebot funcione correctamente.

```bash
DISCORD_PREFIX=<my_discord_prefix>
DISCORD_TOKEN=<my_token>
FAUNADB_SECRET_KEY=<my_faunadb_secret_key>
```

## Inicio el bot

```
python3 src/bot.py
```


[Licencia MIT](./LICENSE)
