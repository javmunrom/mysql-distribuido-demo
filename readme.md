# MySQL Distribuido 🚀

Demo completa de replicación **Master ⇢ Slaves** con **MySQL 8** y un panel en **Django 5.2** que permite:

- Crear tareas (escritura en _master_).
- Leer tareas (lectura balanceada en _slaves_).
- Arrancar / detener contenedores directamente desde la interfaz.
- Ver un log en tiempo real y un diagrama dinámico de los flujos.

> Todo corre en **Docker Compose**; no necesitas instalar MySQL ni Python en tu máquina.

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

_Cada slave autoconfigura la replicación con **GTID** en su script `init.sh` al detectar que el master está listo._

La app Django aplica automáticamente las migraciones al arrancar gracias a un `entrypoint.sh` personalizado.

---

## 2 · Variables relevantes

> Todas están definidas en `docker-compose.yml`. Modifícalas sólo si es necesario.

| Variable              | Valor por defecto               | Uso                                    |
| --------------------- | ------------------------------- | -------------------------------------- |
| `MYSQL_ROOT_PASSWORD` | `rootpass`                      | Contraseña root en todos los MySQL     |
| `MYSQL_DATABASE`      | `tasks_db`                      | Base de datos a replicar               |
| **Usuario réplica**   | `replica_user` / `replica_pass` | Creado en _master_, usado por _slaves_ |

---

## ⚙️ Prerrequisitos

Antes de desplegar el entorno, asegúrate de tener instalado en tu sistema:

- **Docker** ≥ 20.x
- **Docker Compose** ≥ 1.29
- Navegador web actualizado (para acceder al panel de control)

> 💡 _No es necesario instalar MySQL ni Python localmente, ya que todo el entorno se ejecuta en contenedores._

Opcional:

- **Git** (para clonar el repositorio cómodamente).

---

## 3 · Puesta en marcha rápida

```bash
# 1) Clonar el repositorio
$ git clone https://github.com/javmunrom/mysql-distribuido-demo.git
$ cd mysql-distribuido-demo

# 2) Levantar el entorno (construcción de imágenes incluida)
$ docker-compose up --build -d

# 3) Esperar unos 30 segundos:
# - Los slaves mostrarán "✅ Slave configurado con GTID".
# - Django aplicará las migraciones automáticamente sobre el master.

# 4) Acceder al panel web
→ http://localhost:8000
```
