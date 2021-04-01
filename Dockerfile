FROM python:3.8-alpine

# Elijo esta carpeta como carpeta de trabajo
WORKDIR /bot

# Copio requirements.txt y el contenido de src/ en /bot
COPY requirements.txt .env src/ ./

# Instalo algunas dependencias porque las necesitan algunos paquetes de python
RUN apk update \
    && apk add --no-cache gcc python3-dev musl-dev libc-dev

# Actualizo pip
RUN pip install --upgrade pip

# Instalo los paquetes de python
RUN pip install -r requirements.txt

# Inicio el bot
CMD ["python3", "bot.py"]
