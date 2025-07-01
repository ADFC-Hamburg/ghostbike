#!/bin/bash

echo "Warte auf PostgreSQL..."
until pg_isready -h db -p 5432; do
  sleep 1
done

echo "Starte Migrationen..."
piccolo migrations check
piccolo migrations forwards all
echo "Create user"
ADMIN_PASSWORD=$(cat /run/secrets/admin_password || pwgen -s 16)
piccolo user create --username=admin --email=admin@example.org --is_admin=True --is_superuser=True --is_active=True --password=$ADMIN_PASSWORD
echo "Starte API-Server..."
uvicorn ghostbike.main:app --host ${WEBSERVER_IP} --port ${WEBSERVER_PORT}
