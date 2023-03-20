import subprocess

import sys

libs = ["pygame", "pyperclip", "numpy", "Pillow"]


def install(package):
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError:
        print("Package installation failed. Trying with a newer version...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--pre"])


for name in libs:
    if name not in sys.modules:
        install(name)
