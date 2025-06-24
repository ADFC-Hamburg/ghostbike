#!/bin/bash

echo "Warte auf PostgreSQL..."
until pg_isready -h db -p 5432; do
  sleep 1
done

echo "Starte Migrationen..."
piccolo migrations forwards all
echo "Create user"
piccolo user create --username=admin --email=admin@example.org --is_admin=True --is_superuser=True --is_active=True --password=123456
echo "Starte API-Server..."
uvicorn ghostbike.main:app --host 0.0.0.0 --port 8000
