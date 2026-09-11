# Configuración en MacOS y Linux

Ejecute los siguientes comandos en el terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
source setup.sh
```

# Configuración en Windows

Ejecute los siguientes comandos en el terminal:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

También puede usar `.\.venv\Scripts\python.exe` directamente sin activar el entorno.

# Ejecución de pruebas

Ejecute el siguiente comando en el terminal:

```bash
pytest
```

Para verificar únicamente la actividad uno (`PRE_01_hola_mundo`):

```powershell
.\.venv\Scripts\python.exe -m pytest PRE_01_hola_mundo/tests -q
```
