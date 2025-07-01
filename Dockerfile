FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client pwgen && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd -m appuser
COPY ghostbike ghostbike
COPY piccolo_conf.py .
COPY start.sh .
RUN chmod 0755 start.sh
USER appuser
ENV WEBSERVER_IP=127.0.0.1
ENV WEBSERVER_PORT=8100
CMD ["./start.sh"]


