#!/bin/bash
source .venv/bin/activate
source .env
export POSTGRES_DATABASE=$POSTGRES_DATABASE
export POSTGRES_ROOT_PASSWORD=$POSTGRES_ROOT_PASSWORD
export POSTGRES_HOST=$POSTGRES_HOST
export POSTGRES_PORT=$POSTGRES_PORT
export POSTGRES_USER=$POSTGRES_USER
export POSTGRES_PASSWORD=$POSTGRES_PASSWORD
export SUPERUSER_USERNAME=$SUPERUSER_USERNAME
export SUPERUSER_PASSWORD=$SUPERUSER_PASSWORD

/bin/bash scripts/remigrate.sh
