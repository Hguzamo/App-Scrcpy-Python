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


def conectar_ver_pantalla():
    mensaje("Conectando por SSH a la Linux...")

    process = subprocess.Popen([
        PLINK_PATH,
        "-ssh",
        "-batch",
        f"{user.get()}@{ip.get()}",
        "-pw", password.get(),
        "adb devices"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout, stderr = process.communicate()
    print(stdout)

    mensaje("Móvil detectado")

    mensaje("Creando túnel SSH...")
    subprocess.Popen([
        PLINK_PATH,
        "-ssh",
        "-N",
        "-batch",
        f"{user.get()}@{ip.get()}",
        "-pw", password.get(),
        "-L", "5031:localhost:5037",
        "-R", "27183:localhost:27183"
    ])

    time.sleep(2)

    env = os.environ.copy()
    env["ADB_SERVER_SOCKET"] = "tcp:127.0.0.1:5031"

    scrcpy_path = find_scrcpy()

    mensaje("Abriendo scrcpy...")

    # 🔥 CAMBIO IMPORTANTE AQUÍ
    subprocess.Popen([
        scrcpy_path,
        "--video-codec=h264",
        "--no-audio",
        "--max-size=1024"
    ], env=env)

    mensaje("Pantalla del móvil abierta")


app = tk.Tk()
app.title("Scrcpy")
app.geometry("420x250")

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
    text="Conectar y ver pantalla",
    bg="green",
    fg="white",
    font=("Arial", 12),
    command=conectar_ver_pantalla
).pack(pady=15)

app.mainloop()