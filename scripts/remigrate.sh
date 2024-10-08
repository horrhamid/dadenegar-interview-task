#!/bin/bash

psql postgres://postgres:$POSTGRES_ROOT_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '$POSTGRES_DATABASE' -- ← change this to your DB AND pid <> pg_backend_pid();"
psql postgres://postgres:$POSTGRES_ROOT_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/postgres -c "DROP DATABASE IF EXISTS $POSTGRES_DATABASE;"
psql postgres://postgres:$POSTGRES_ROOT_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/postgres -c "DROP ROLE IF EXISTS $POSTGRES_USER;"
psql postgres://postgres:$POSTGRES_ROOT_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/postgres -c "CREATE ROLE $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
psql postgres://postgres:$POSTGRES_ROOT_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/postgres -c "ALTER ROLE $POSTGRES_USER CREATEDB;"
psql postgres://postgres:$POSTGRES_ROOT_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/postgres -c "ALTER ROLE $POSTGRES_USER LOGIN;"
psql postgres://postgres:$POSTGRES_ROOT_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/postgres -c "CREATE DATABASE $POSTGRES_DATABASE WITH ENCODING='UTF8' OWNER=$POSTGRES_USER TEMPLATE template1"
psql postgres://postgres:$POSTGRES_ROOT_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/postgres -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DATABASE TO $POSTGRES_USER;"



python manage.py migrate
python shell.py actions
#python shell.py instruments
python shell.py superuser  $SUPERUSER_USERNAME $SUPERUSER_PASSWORD
# python shell.py brokers
# python shell.py accounting temp_accounting.xlsx
