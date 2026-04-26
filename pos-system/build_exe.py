import subprocess
import os

def build_exe():
    print("Instalando dependencias necesarias (PyInstaller)...")
    subprocess.call(["pip", "install", "pyinstaller", "flask", "flask-sqlalchemy", "werkzeug"])
    
    print("\nGenerando ejecutable con PyInstaller...")
    
    # Constuir el comando de pyinstaller
    cmd = [
        "pyinstaller",
        "--name", "Taqueria_POS",
        "--onedir",
        "--add-data", f"templates{os.pathsep}templates",
        "--add-data", f"static{os.pathsep}static",
        "--console", # Mantiene consola para ver errores o logs si se requiere, para quitarlo: --windowed
        "--clean",
        "-y",
        "run.py"
    ]
    
    subprocess.call(cmd)
    print("\n==================================")
    print("✅ ¡Construcción terminada exitosamente!")
    print("✅ Busca el programa en la carpeta 'dist/Taqueria_POS/' y ejecuta Taqueria_POS.exe")
    print("==================================")

if __name__ == "__main__":
    build_exe()
