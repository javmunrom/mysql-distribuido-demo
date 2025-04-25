#!/bin/bash
set -e

# Esperar a que la base de datos esté disponible
/wait-for-db.sh

# Aplicar migraciones
echo "Aplicando migraciones en el master..."
python manage.py migrate

# Crear superusuario si quieres (opcional)
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')" | python manage.py shell

# Arrancar el servidor de Django
echo "Arrancando servidor Django..."
exec python manage.py runserver 0.0.0.0:8000
