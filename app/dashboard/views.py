from django.shortcuts import render, redirect
from .models import Task
import random
from datetime import datetime, timedelta
from django.utils.timezone import now
import docker
from django.shortcuts import redirect
import matplotlib.pyplot as plt
import io
from django.http import HttpResponse
import io
from django.http import HttpResponse
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# Log temporal en memoria
operation_log = []
replication_times = {}

CONTAINER_NAMES = {
    'slave1': 'db-slave1',
    'slave2': 'db-slave2',
    'slave3': 'db-slave3'
}

CONTAINERS = ['db-master', 'db-slave1', 'db-slave2', 'db-slave3']
def home(request):
    estados = {}
    for cont in CONTAINERS:
        try:
            container = client.containers.get(cont)
            container.reload()
            estados[cont] = container.status
        except docker.errors.NotFound:
            estados[cont] = 'not found'

    # Detectar el último log
    ultimo_log = operation_log[-1] if operation_log else None

    return render(request, 'dashboard/home.html', {
        'logs': operation_log,
        'estados': estados,
        'ultimo_log': ultimo_log
    })



def create_task(request):
    contenedor_master = 'db-master'

    try:
        container = client.containers.get(contenedor_master)
        container.reload()
        estado = container.status
        print(f"📡 Estado real de {contenedor_master}: {estado}")

        if estado != 'running':
            operation_log.append(f"[{now().strftime('%H:%M:%S')}] ❌ No se puede crear tarea. Master caído.")
            return render(request, 'dashboard/master_down.html')

    except docker.errors.NotFound:
        operation_log.append(f"[{now().strftime('%H:%M:%S')}] ❌ Contenedor Master no encontrado")
        return render(request, 'dashboard/master_down.html')

    # Si el master está operativo
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')

        Task.objects.using('default').create(title=title, description=description)

        operation_log.append(f"[{now().strftime('%H:%M:%S')}] ✔ Tarea creada en ➡️ db-master")

        return redirect('home')

    return render(request, 'dashboard/create_task.html')



def list_tasks(request):
    slave_db = random.choice(['slave1', 'slave2', 'slave3'])
    tasks = Task.objects.using(slave_db).all()

    operation_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✔ Tareas leídas desde {slave_db}")

    return render(request, 'dashboard/list_tasks.html', {'tasks': tasks})

from django.db import DatabaseError
def list_tasks_slave(request, slave_name):
    contenedor_real = CONTAINER_NAMES.get(slave_name)

    if not contenedor_real:
        operation_log.append(f"[{now().strftime('%H:%M:%S')}] ❌ Nombre de slave inválido: {slave_name}")
        return render(request, 'dashboard/slave_down.html', {'slave': slave_name})

    try:
        container = client.containers.get(contenedor_real)
        container.reload()
        estado = container.status
        print(f"📡 Estado real de {contenedor_real}: {estado}")

        if estado != 'running':
            operation_log.append(f"[{now().strftime('%H:%M:%S')}] ⚠️ {slave_name} está caído")
            return render(request, 'dashboard/slave_down.html', {'slave': slave_name})

    except docker.errors.NotFound:
        operation_log.append(f"[{now().strftime('%H:%M:%S')}] ❌ Contenedor {contenedor_real} no encontrado")
        return render(request, 'dashboard/slave_down.html', {'slave': slave_name})

    # Si está en marcha
    tasks = Task.objects.using(slave_name).all()
    operation_log.append(f"[{now().strftime('%H:%M:%S')}] 📄 Consultado {slave_name} - {len(tasks)} tareas")
    return render(request, 'dashboard/list_tasks.html', {
        'tasks': tasks,
        'slave': slave_name
    })





client = docker.from_env()

def start_container(request, container_name):
    container = client.containers.get(container_name)
    container.start()
    operation_log.append(f"[{now().strftime('%H:%M:%S')}] ▶️ Arrancado {container_name}")
    return redirect('home')

def stop_container(request, container_name):
    container = client.containers.get(container_name)
    container.stop()
    operation_log.append(f"[{now().strftime('%H:%M:%S')}] 🛑 Parado {container_name}")
    return redirect('home')


COLORS = {
    "edge":    "#6b7280",  # gris medio para flechas
    "default": "#f0f0f5",  # nodos neutros
    "master":  "#d0e8ff",  # nodo master OK
    "slave":   "#e8eefd",  # nodo slave OK
    "ok":      "#d4f8d4",  # resalte operación OK
    "error":   "#ffd6d6",  # nodos / estados en error
}

plt.rcParams.update({
    "font.family":   "DejaVu Sans",
    "font.size":     10,
    "figure.facecolor": "none",
    "axes.facecolor":   "none",
})

# ──────────────────────────────────────────────────────────────────────────────
def esquema_dinamico(request):
    if not operation_log:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(
            0.5, 0.5,
            "Sin operaciones",
            fontsize=16, ha="center", va="center",
            color="#6b7280", fontweight="light",
        )
        ax.axis("off")

    else:
        ultimo_log = operation_log[-1]
        fig, ax = plt.subplots(figsize=(7.5, 4.5))
        ax.axis("off")

        # ── Helpers ────────────────────────────────────────────────────────────
        def draw_node(x, y, text, color="default", w=0.24, h=0.12):
            ax.add_patch(
                FancyBboxPatch(
                    (x, y), w, h,
                    boxstyle="round,pad=0.03",
                    edgecolor="#d1d5db",
                    facecolor=COLORS.get(color, color),
                    linewidth=1.5,
                )
            )
            ax.text(x + w / 2, y + h / 2, text,
                    ha="center", va="center",
                    color="#1f2937", fontsize=10, weight="semibold")
            return (x + w / 2, y + h / 2)              # ← DEVUELVE el centro


        def draw_arrow(x1, y1, x2, y2):
            ax.annotate(
                "",
                xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="->",
                    color=COLORS["edge"],
                    linewidth=1.6,
                    shrinkA=2, shrinkB=2,
                ),
            )


        # ── Plantillas de diagramas ───────────────────────────────────────────
        # 1) Creación de tarea
        if "Tarea creada" in ultimo_log:
            # Medidas de los nodos
            W, H = 0.24, 0.12             # ancho y alto (coherentes con draw_node)

            # Columna vertical (centrada aprox. en X = 0.44)
            col_x = 0.32                  # esquina izquierda de la columna
            cx   = col_x + W / 2          # centro X común

            y_usuario, y_django, y_master = 0.78, 0.58, 0.38
            draw_node(col_x, y_usuario, "Usuario")
            draw_node(col_x, y_django,  "Django")
            draw_node(col_x, y_master,  "Master", color="master")

            # Flechas verticales (centro-centro)
            draw_arrow(cx, y_usuario, cx, y_django + H)   # Usuario → Django
            draw_arrow(cx, y_django,  cx, y_master + H)   # Django  → Master

            # Fila inferior de slaves
            s1_x,  s2_x,  s3_x  = 0.02, 0.37, 0.72   # ← más distancia entre columnas
            y_slaves = 0.12
            c_s1 = draw_node(s1_x, y_slaves, "Slave 1", color="slave")
            c_s2 = draw_node(s2_x, y_slaves, "Slave 2", color="slave")
            c_s3 = draw_node(s3_x, y_slaves, "Slave 3", color="slave")
            # Replicación (Master → Slaves) -- partimos del centro‐inferior del Master
            master_x = cx
            master_y = y_master           # borde inferior (ya que centreY = y_master + H/2)

            #   ↑ añadimos un desplazamiento shrinkA/B = 4 px en draw_arrow para
            #     evitar que las puntas entren en las cajas.
            def draw_arrow_clean(x1, y1, x2, y2):
                ax.annotate(
                    "", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>",
                                    color=COLORS["edge"],
                                    linewidth=1.6,
                                    shrinkA=4, shrinkB=4)
                )

            draw_arrow_clean(master_x, master_y, s1_x + W/2, y_slaves + H)
            draw_arrow_clean(master_x, master_y, s2_x + W/2, y_slaves + H)
            draw_arrow_clean(master_x, master_y, s3_x + W/2, y_slaves + H)
        # 2) Consultas a slaves
        elif "Consultado" in ultimo_log:
            if "slave1" in ultimo_log:
                slave = "Slave 1"
            elif "slave2" in ultimo_log:
                slave = "Slave 2"
            elif "slave3" in ultimo_log:
                slave = "Slave 3"
            else:
                slave = "Slave"

            draw_node(0.05, 0.45, "Usuario")
            draw_node(0.38, 0.45, "Django")
            draw_node(0.71, 0.45, slave, color="slave")
            draw_arrow(0.29, 0.51, 0.38, 0.51)
            draw_arrow(0.62, 0.51, 0.71, 0.51)

        # 3) Replicación desde master a slaves
        elif "Replicada" in ultimo_log:
            draw_node(0.4, 0.68, "Master", color="master", w=0.28)
            draw_node(0.05, 0.35, "Slave 1", color="slave")
            draw_node(0.4, 0.35, "Slave 2", color="slave")
            draw_node(0.72, 0.35, "Slave 3", color="slave")
            draw_arrow(0.54, 0.68, 0.19, 0.41)
            draw_arrow(0.54, 0.68, 0.54, 0.41)
            draw_arrow(0.54, 0.68, 0.86, 0.41)

        # 4) Master caído
        elif "Master caído" in ultimo_log:
            draw_node(0.05, 0.45, "Usuario")
            draw_node(0.38, 0.45, "Django")
            draw_node(0.71, 0.45, "Master (OFF)", color="error")
            draw_arrow(0.29, 0.51, 0.38, 0.51)
            draw_arrow(0.62, 0.51, 0.71, 0.51)

        # 5) Slave caído
        elif "slave" in ultimo_log.lower() and "caído" in ultimo_log.lower():
            # Determinar qué slave
            if "slave1" in ultimo_log.lower():
                slave = "Slave 1"
            elif "slave2" in ultimo_log.lower():
                slave = "Slave 2"
            elif "slave3" in ultimo_log.lower():
                slave = "Slave 3"
            else:
                slave = "Slave"

            draw_node(0.05, 0.45, "Usuario")
            draw_node(0.38, 0.45, "Django")
            draw_node(0.71, 0.45, f"{slave} OFF", color="error")
            draw_arrow(0.29, 0.51, 0.38, 0.51)
            draw_arrow(0.62, 0.51, 0.71, 0.51)

        # 6) Contenedor arrancado
        elif "Arrancado" in ultimo_log:
            contenedor = ultimo_log.split("Arrancado ")[1]
            draw_node(0.38, 0.45, f"{contenedor} OK", color="ok", w=0.34, h=0.14)
            plt.title(f"{contenedor} arrancado correctamente", fontsize=12)

        # 7) Contenedor parado
        elif "Parado" in ultimo_log:
            contenedor = ultimo_log.split("Parado ")[1]
            draw_node(0.38, 0.45, f"{contenedor} detenido", color="error", w=0.34, h=0.14)
            plt.title(f"{contenedor} detenido", fontsize=12)

        else:
            ax.text(
                0.5, 0.5,
                "Operación no reconocida",
                fontsize=12, ha="center", va="center",
                color="#6b7280",
            )

    # ── Exportar imagen ─────────────────────────────────────────────────────────
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type="image/png")