import tkinter as tk
import subprocess
import os
import time

PLINK_PATH = r"C:\Program Files\PuTTY\plink.exe"
SCRCPY_PATH = r"C:\Users\usuario\Downloads\scrcpy-win64-v3.3.4\scrcpy.exe"

tunnel_process = None  # control del túnel


def mensaje(msg):
    display.config(text=msg)
    print(msg)


def listar_dispositivos():
    mensaje("Buscando dispositivos ADB...")

    process = subprocess.Popen([
        PLINK_PATH,
        "-ssh",
        "-batch",
        f"{user.get()}@{ip.get()}",
        "-pw", password.get(),
        "adb devices"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout, stderr = process.communicate()

    lista.delete(0, tk.END)

    for line in stdout.splitlines():
        if "\tdevice" in line:
            device_id = line.split("\t")[0]
            lista.insert(tk.END, device_id)

    mensaje("Dispositivos cargados")


def conectar_dispositivo():
    global tunnel_process

    seleccionado = lista.get(tk.ACTIVE)

    if not seleccionado:
        mensaje("Selecciona un dispositivo")
        return

    mensaje(f"Conectando a {seleccionado}...")

    # Cerrar túnel anterior si existe
    if tunnel_process:
        try:
            tunnel_process.terminate()
            tunnel_process.wait()
        except:
            pass

    # Crear túnel completo (ADB + vídeo)
    tunnel_process = subprocess.Popen([
        PLINK_PATH,
        "-ssh",
        "-N",
        "-batch",
        f"{user.get()}@{ip.get()}",
        "-pw", password.get(),
        "-L", "5031:localhost:5037",   # ADB
        "-R", "27183:localhost:27183"  # VIDEO
    ])

    mensaje("Esperando túnel...")
    time.sleep(3)

    # Forzar el ADB remoto
    env = os.environ.copy()
    env["ADB_SERVER_SOCKET"] = "tcp:127.0.0.1:5031"

    mensaje("Abriendo scrcpy...")

    subprocess.Popen([
        SCRCPY_PATH,
        "-s", seleccionado,
        "--video-codec=h264",
        "--no-audio",
        "--max-size=1024"
    ], env=env)

    mensaje("Pantalla abierta")


def crear_acceso_directo():
    seleccionado = lista.get(tk.ACTIVE)

    if not seleccionado:
        mensaje("Selecciona un dispositivo")
        return

    mensaje(f"Creando acceso directo para {seleccionado}...")

    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    nombre_archivo = f"Conectar_{seleccionado}.bat"
    ruta_bat = os.path.join(escritorio, nombre_archivo)

    contenido = f"""@echo off
echo Conectando a {seleccionado}...

start "" "{PLINK_PATH}" -ssh -N -batch {user.get()}@{ip.get()} -pw {password.get()} -L 5031:localhost:5037 -R 27183:localhost:27183

timeout /t 3

set ADB_SERVER_SOCKET=tcp:127.0.0.1:5031

"{SCRCPY_PATH}" -s {seleccionado} --video-codec=h264 --no-audio --max-size=1024

pause
"""

    with open(ruta_bat, "w") as f:
        f.write(contenido)

    mensaje(f"Acceso directo creado en el escritorio: {nombre_archivo}")


# ---------------- UI ----------------

app = tk.Tk()
app.title("Scrcpy (varios dispositivos)")
app.geometry("420x450")

ip = tk.StringVar()
user = tk.StringVar()
password = tk.StringVar()

display = tk.Label(
    app,
    text="Introduce los datos del servidor Linux",
    font=("Arial", 12),
    wraplength=380
)
display.pack(pady=10)

tk.Label(app, text="IP Linux").pack()
tk.Entry(app, textvariable=ip).pack()

tk.Label(app, text="Usuario").pack()
tk.Entry(app, textvariable=user).pack()

tk.Label(app, text="Contraseña").pack()
tk.Entry(app, textvariable=password, show="*").pack()

tk.Button(
    app,
    text="1. Listar dispositivos",
    bg="blue",
    fg="white",
    command=listar_dispositivos
).pack(pady=10)

lista = tk.Listbox(app, height=6)
lista.pack(pady=10)

tk.Button(
    app,
    text="2. Conectar al seleccionado",
    bg="green",
    fg="white",
    command=conectar_dispositivo
).pack(pady=10)

tk.Button(
    app,
    text="3. Crear acceso directo del seleccionado",
    bg="orange",
    fg="white",
    command=crear_acceso_directo
).pack(pady=10)

app.mainloop()