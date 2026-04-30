import tkinter as tk
import subprocess
import os
import time
import socket

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


# ---------------- ESPERAR PUERTO ---------------- #

def wait_port(port):
    while True:
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=1)
            s.close()
            return
        except:
            time.sleep(0.2)


# ---------------- CONECTAR ---------------- #

def conectar():
    mensaje("Creando túnel SSH...")

    tunnel = subprocess.Popen([
        PLINK_PATH,
        "-ssh",
        "-N",
        "-batch",
        f"{user.get()}@{ip.get()}",
        "-pw", password.get(),
        "-L", "5031:localhost:5037"
    ])

    # Esperar a que el túnel esté listo
    wait_port(5031)

    mensaje("Túnel listo")

    # ADB remoto a través del túnel
    env = os.environ.copy()
    env["ADB_SERVER_SOCKET"] = "tcp:127.0.0.1:5031"

    scrcpy_path = find_scrcpy()

    if not scrcpy_path:
        mensaje("No se encontró scrcpy")
        return

    mensaje("Abriendo scrcpy...")

    subprocess.Popen([
        scrcpy_path,
        "--video-codec=h264",
        "--no-audio",
        "--max-size=1024"
    ], env=env)

    mensaje("Pantalla abierta")


# ---------------- GUI ---------------- #

app = tk.Tk()
app.title("Scrcpy estable (modo pro)")
app.geometry("420x300")

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
    text="Conectar y abrir pantalla",
    bg="green",
    fg="white",
    font=("Arial", 12),
    command=conectar
).pack(pady=20)

app.mainloop()