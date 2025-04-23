FROM mysql:8.0

COPY my.cnf /etc/mysql/conf.d/my.cnf
COPY init.sh /docker-entrypoint-initdb.d/init.sh
RUN chmod +x /docker-entrypoint-initdb.d/init.sh
