# Simulación y Modelos - MVP

## Descripción General
Este proyecto es un Producto Mínimo Viable (MVP) diseñado para la generación y validación estadística de números pseudoaleatorios. Consiste en una aplicación web con un frontend interactivo y una API backend robusta que realiza cálculos matemáticos y estadísticos precisos.

## Características Principales

### Generadores de Números Pseudoaleatorios
La aplicación soporta la generación de números a través de los siguientes métodos:
* **Método Congruencial**: Permite generadores lineales, mixtos y multiplicativos configurando el multiplicador (a), incremento (c) y módulo (m).
* **Método de Cuadrados Medios**: Generación basada en una semilla inicial.

### Pruebas de Validación Estadística
Una vez generados los números, el sistema permite aplicar diversas pruebas estadísticas para comprobar su uniformidad e independencia:
* **Pruebas de Uniformidad**: Prueba de Medias, Prueba de Varianza, Prueba Chi-Cuadrada (Bondad de Ajuste).
* **Pruebas de Independencia**: Prueba de Poker (5 decimales), Prueba de Corridas (Arriba/Abajo), Prueba de Series (Pares 2D).
* **Pruebas Avanzadas**: Prueba de Kolmogorov-Smirnov.

La interfaz proporciona el veredicto de la prueba (aprobado o rechazado), el razonamiento detallado, el desarrollo matemático renderizado en KaTeX y un análisis visual a través de gráficos.

## Tecnologías Utilizadas

* **Backend**: Python 3, FastAPI, Uvicorn, NumPy, SciPy, Pydantic.
* **Frontend**: HTML5, CSS3 (estilo Cyber-Industrial), JavaScript (Vanilla), Chart.js (para gráficos), KaTeX (para renderizado de fórmulas matemáticas).

## Estructura del Proyecto

* `/backend`: Contiene la lógica de la API.
  * `main.py`: Punto de entrada de la aplicación FastAPI, definición de endpoints y servicio de archivos estáticos.
  * `generators.py`: Lógica de los métodos de generación de números pseudoaleatorios.
  * `validators.py`: Implementación de todas las pruebas estadísticas.
* `/frontend`: Contiene los archivos estáticos de la interfaz de usuario (`index.html`, `style.css`, `app.js`).
* `requirements.txt`: Dependencias de Python necesarias para el backend.
* `start_server.ps1`: Script de PowerShell para iniciar el servidor localmente.

## Cómo hacer funcionar el proyecto en local

Sigue estos pasos para instalar y ejecutar el proyecto en tu máquina local.

### Prerrequisitos
* Tener Python (versión 3.8 o superior) instalado en el sistema.

### Instalación y Ejecución

1. **Abrir una terminal**
   Navega hasta el directorio raíz del proyecto (donde se encuentra el archivo `requirements.txt`).

2. **Crear y activar un entorno virtual (Recomendado)**
   Ejecuta los siguientes comandos en PowerShell para aislar las dependencias:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Instalar las dependencias**
   Con el entorno virtual activado, instala los paquetes requeridos usando pip:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Iniciar el servidor**
   Puedes iniciar el servidor utilizando el script de PowerShell provisto:
   ```powershell
   .\start_server.ps1
   ```
   *Alternativa*: Si prefieres ejecutar el comando manualmente con el entorno virtual activado:
   ```powershell
   uvicorn main:app --host 127.0.0.1 --port 8000 --app-dir backend
   ```

5. **Acceder a la aplicación**
   Una vez que el servidor esté en ejecución, abre tu navegador web y visita la siguiente dirección:
   `http://127.0.0.1:8000`

## Uso de la Aplicación

1. En la sección "Generar Números", selecciona un método de generación (Congruencial o Cuadrados Medios).
2. Ingresa la cantidad de números a generar (n), la semilla inicial, y los parámetros adicionales si estás usando el método congruencial (a, c, m).
3. Haz clic en "Generar Serie". Los resultados aparecerán tabulados debajo del formulario.
4. Una vez generada la serie, la sección "Pruebas de Validación" se hará visible.
5. Selecciona la prueba estadística deseada y el nivel de significancia (alpha).
6. Haz clic en "Ejecutar Prueba" para ver los resultados estadísticos, las fórmulas matemáticas aplicadas y las gráficas interactivas.
