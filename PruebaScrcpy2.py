import tkinter as tk
import subprocess
import os
import time

PLINK_PATH = r"C:\Program Files\PuTTY\plink.exe"
SCRCPY_FOLDER = r"C:\Users\usuario\Downloads\scrcpy-win64-v3.3.4"


def find_scrcpy():
    for root, dirs, files in os.walk(SCRCPY_FOLDER):
        for f in files:
            if f.lower() == "scrcpy.exe":
                return os.path.join(root, f)
    return None


def mensaje(msg):
    display.config(text=msg)
    print(msg)


# ---------------- ADB DEVICES ---------------- #

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

    lines = stdout.splitlines()

    for line in lines:
        if "\tdevice" in line:
            device_id = line.split("\t")[0]
            lista.insert(tk.END, device_id)

    mensaje("Dispositivos cargados")


# ---------------- CONECTAR SCRCPY ---------------- #

def conectar_dispositivo():
    seleccionado = lista.get(tk.ACTIVE)

    if not seleccionado:
        mensaje("Selecciona un dispositivo")
        return

    mensaje(f"Conectando a {seleccionado}...")

    subprocess.Popen([
        PLINK_PATH,
        "-ssh",
        "-N",
        "-batch",
        f"{user.get()}@{ip.get()}",
        "-pw", password.get(),
        "-L", "5031:localhost:5037"
    ])

    time.sleep(2)

    env = os.environ.copy()
    env["ADB_SERVER_SOCKET"] = "tcp:127.0.0.1:5031"

    scrcpy_path = find_scrcpy()

    mensaje("Abriendo scrcpy...")

    subprocess.Popen([
        scrcpy_path,
        "-s", "A75259FRCN9A2DV0538",
        "--video-codec=h264",
        "--no-audio",
        "--max-size=1024"
    ])

    mensaje("Pantalla abierta")


# ---------------- GUI ---------------- #

app = tk.Tk()
app.title("Scrcpy selector de dispositivos")
app.geometry("420x400")

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

lista = tk.Listbox(app, height=5)
lista.pack(pady=10)

tk.Button(
    app,
    text="2. Conectar al seleccionado",
    bg="green",
    fg="white",
    command=conectar_dispositivo
).pack(pady=10)

app.mainloop()