#!/bin/bash
echo "Esperando a que el master esté listo..."

until mysql -h db-master -uroot -prootpass -e "SHOW DATABASES;" > /dev/null 2>&1; do
  sleep 1
done

echo "Conectado al master. Configurando replicación..."

mysql -uroot -prootpass <<EOF
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='db-master',
  SOURCE_USER='replica_user',
  SOURCE_PASSWORD='replica_pass',
  SOURCE_LOG_FILE='mysql-bin.000001',
  SOURCE_LOG_POS=4;
START REPLICA;
EOF

echo "✅ Slave configurado"
