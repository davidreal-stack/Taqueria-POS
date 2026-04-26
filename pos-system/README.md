# 🍔 Taqueria POS System

Un sistema de Punto de Venta (POS) local (offline-first) desarrollado con Python, Flask, SQLite y JS nativo. Ideal para taquerías, hamburgueserías o restaurantes de comida rápida.

## 🚀 Requisitos y Configuración

1. **Instalar dependencias necesarias**:
   Asegúrate de tener Python >= 3.8 instalado. Abre tu terminal y ejecuta:
   ```bash
   pip install flask flask-sqlalchemy werkzeug pyinstaller
   ```

2. **Ejecutar en modo Desarrollo/Local**:
   Simplemente ejecuta el arcivo `run.py`:
   ```bash
   python run.py
   ```
   > 💡 Esto inicializará la base de datos automáticamente (si no existe), generará datos de prueba y un usuario administrador, y abrirá automáticamente tu navegador web en `http://localhost:5000`.

## 📦 Empaquetar como Ejecutable (.exe)

Para crear una versión portable para Windows sin necesidad de que el usuario final instale Python:

1. Ejecuta el script de construcción:
   ```bash
   python build_exe.py
   ```
2. Esto generará la carpeta `dist/Taqueria_POS`.
3. Entra a esa carpeta y ejecuta el archivo **`Taqueria_POS.exe`**.

## 🔑 Usuarios por Defecto

El seeder automático genera la base de datos `database.db` y crea el siguiente usuario administrador en el primer inicio:

- **Usuario**: `admin`
- **Contraseña**: `admin`

_El rol de Admin incluye acceso al Dashboard de reportes, catálogo de productos, punto de venta (Cajero) y vistas de múltiples cocinas._

---

## 🛠 Arquitectura

- **Backend**: Python + Flask. Emplea _blueprints_ (`routes/`) para mantener todo modular (auth, productos, ordenes, pagos, reportes).
- **ORM**: SQLAlchemy.
- **Frontend**: Plantillas de Jinja2 (`templates/`) combinadas con CSS y Vanilla JavaScript (`static/`).
- **Data**: Todo se guarda localmente en `database.db` en la carpeta raíz para máxima portabilidad (Offline-First).
