#!/bin/bash

docker compose down
docker volume rm ghostbike_postgres_data
rm ghostbike/piccolo_migrations/ghostbike_*.py
./.venv/bin/piccolo migrations new all --auto
docker compose build

docker compose up
