import tkinter as tk
import subprocess
import os
import time
import tempfile
import shutil
import sys

#PENDIENTE:
#Poder elegir nombre del .exe y sino pone uno predeterminado
#Que funcione en linux
#Si hay algo no instalado, que te lo diga

PLINK_PATH = r"C:\Program Files\PuTTY\plink.exe"
SCRCPY_PATH = r"C:\Users\usuario\Downloads\scrcpy-win64-v3.3.4\scrcpy.exe"

tunnel_process = None


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

    if tunnel_process:
        try:
            tunnel_process.terminate()
            tunnel_process.wait()
        except:
            pass

    tunnel_process = subprocess.Popen([
        PLINK_PATH,
        "-ssh",
        "-N",
        "-batch",
        f"{user.get()}@{ip.get()}",
        "-pw", password.get(),
        "-L", "5031:localhost:5037",
        "-R", "27183:localhost:27183"
    ])

    mensaje("Esperando túnel...")
    time.sleep(3)

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


def crear_exe():
    seleccionado = lista.get(tk.ACTIVE)

    if not seleccionado:
        mensaje("Selecciona un dispositivo")
        return

    mensaje(f"Creando EXE para {seleccionado}...")

    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")

    temp_dir = tempfile.mkdtemp()
    script_path = os.path.join(temp_dir, "launcher.py")

    contenido = f"""
import subprocess
import os
import time

PLINK_PATH = r"{PLINK_PATH}"
SCRCPY_PATH = r"{SCRCPY_PATH}"

ip = "{ip.get()}"
user = "{user.get()}"
password = "{password.get()}"
device = "{seleccionado}"

tunnel = subprocess.Popen([
    PLINK_PATH,
    "-ssh",
    "-N",
    "-batch",
    f"{{user}}@{{ip}}",
    "-pw", password,
    "-L", "5031:localhost:5037",
    "-R", "27183:localhost:27183"
])

time.sleep(3)

env = os.environ.copy()
env["ADB_SERVER_SOCKET"] = "tcp:127.0.0.1:5031"

subprocess.Popen([
    SCRCPY_PATH,
    "-s", device,
    "--video-codec=h264",
    "--no-audio",
    "--max-size=1024"
], env=env)
"""

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(contenido)

    # 🔥 FIX IMPORTANTE: PyInstaller correcto
    subprocess.run([
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconsole",
        script_path
    ], cwd=temp_dir)

    exe_path = os.path.join(temp_dir, "dist", "launcher.exe")

    if not os.path.exists(exe_path):
        mensaje("Error creando el EXE")
        return

    final_path = os.path.join(escritorio, f"Conectar_{seleccionado}.exe")
    shutil.move(exe_path, final_path)

    shutil.rmtree(temp_dir, ignore_errors=True)

    mensaje(f"EXE creado en escritorio: {final_path}")


# ---------------- UI ----------------

app = tk.Tk()
app.title("Scrcpy (varios dispositivos)")
app.geometry("420x500")

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
    text="3. Crear acceso rápido",
    bg="orange",
    fg="white",
    command=crear_exe
).pack(pady=10)

app.mainloop()