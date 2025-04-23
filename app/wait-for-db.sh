#!/bin/bash
set -e

host="db-master"
port="3306"

echo "Esperando a que la base de datos ($host) esté disponible..."

until nc -z $host $port; do
  sleep 1
done

echo "Base de datos disponible. Arrancando Django..."

exec "$@"
