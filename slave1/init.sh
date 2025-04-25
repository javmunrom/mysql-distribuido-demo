#!/bin/bash
echo "Esperando a que el master esté listo..."

until mysql -h db-master -uroot -prootpass -e "SHOW DATABASES;" > /dev/null 2>&1; do
  sleep 1
done

echo "Conectado al master. Configurando replicación con GTID..."

mysql -uroot -prootpass <<EOF
STOP REPLICA;
RESET REPLICA ALL;
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='db-master',
  SOURCE_USER='replica_user',
  SOURCE_PASSWORD='replica_pass',
  SOURCE_AUTO_POSITION = 1;
START REPLICA;
EOF

echo "✅ Slave configurado con GTID"
