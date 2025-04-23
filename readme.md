# MySQL Distribuido 🚀

Demo completa de replicación **Master ⇢ Slaves** con MySQL 8 y un panel en **Django 5.2** que permite:

- Crear tareas (escritura en _master_).
- Leer tareas (lectura balanceada en _slaves_).
- Arrancar / detener contenedores directamente desde la interfaz.
- Ver un log en tiempo real y un diagrama dinámico de los flujos.

> Todo corre en Docker Compose; no necesitas instalar MySQL ni Python en tu máquina.

![Dashboard screenshot](docs/screenshot-dashboard.png)

---

## 1 · Stack de servicios

| Servicio       | Imagen base        | Contexto build | Descripción                                          |
| -------------- | ------------------ | -------------- | ---------------------------------------------------- |
| **db‑master**  | `mysql:8.0`        | `./master`     | Nodo de escritura. Bin‑logs activados.               |
| **db‑slave1**  | `mysql:8.0`        | `./slave1`     | Réplica 1 (read‑only).                               |
| **db‑slave2**  | `mysql:8.0`        | `./slave2`     | Réplica 2 (read‑only).                               |
| **db‑slave3**  | `mysql:8.0`        | `./slave3`     | Réplica 3 (read‑only).                               |
| **django‑app** | `python:3.10-slim` | `./app`        | Panel web + API. Habla con Docker Engine vía socket. |

_Cada slave autoconfigura la replicación en su script `init.sh` al detectar que el master está listo._

---

## 2 · Variables relevantes

> Todas están fijas en `docker‑compose.yml`; sólo cámbialas si lo necesitas.

| Variable              | Valor por defecto               | Dónde se usa                            |
| --------------------- | ------------------------------- | --------------------------------------- |
| `MYSQL_ROOT_PASSWORD` | `rootpass`                      | Todos los contenedores MySQL            |
| `MYSQL_DATABASE`      | `tasks_db`                      | BD a replicar                           |
| **Usuario réplica**   | `replica_user` / `replica_pass` | Creado en _master_ y usado por _slaves_ |

---

## 3 · Puesta en marcha rápida

```bash
# 1) Clonar repo
$ git clone https://github.com/tu‑usuario/mysql-distribuido-demo.git
$ cd mysql-distribuido-demo

# 2) Construir imágenes y levantar todo
$ docker compose up --build -d

# 3) Esperar ~30 s a que los slaves se enganchen (init.sh imprime ✅).

# 4) Abrir el dashboard
→ http://localhost:8000
```

La aplicación se arranca automáticamente dentro de `django-app` gracias a `wait-for-db.sh`, que espera la disponibilidad del _master_.

---

## 5 · Funcionalidades actuales del panel

- **Crear tarea** → aparece instantánea en master, se replica en segundos.
- **Listar tareas** → balanceo simple (aleatorio) entre slaves.
- **On/Off containers** → botones de Parar/Arrancar (Docker API).
- **Log en memoria** con timestamp y mensaje.
- **Esquemas dinámicos** dibujados con `matplotlib` (sin emojis).
