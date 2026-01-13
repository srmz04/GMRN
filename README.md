# GMRN - Generador Masivo de Reportes Nutricionales

Sistema para generar reportes individuales de IMC para menores escolares. Se trata de una herramienta para facilitar la identificación de menores con problemas nutricionales previamente tamizados de manera masiva, esto en el marco de un proyecto colaborativo entre la Subdirección de Educación Física A (SEED) y el Departamento de Enfermedades Transmisibles (SSD) del estado de Durango.

## Qué hace

Procesa datos de somatometría de aprox. 63,000 menores (6-12 años) del subsistema federal y genera PDFs individuales de 3 paginas:

1. Gráfica de crecimiento OMS (IMC vs edad)
2. Cartilla de salud escolar con datos del alumno
3. Hoja de referencia para derivación a centros de salud

El sistema permite a profesores de educación física y personal de salud identificar rápidamente casos que requieren seguimiento (desnutrición, sobrepeso, obesidad).

### ¿Cómo calculamos el percentil?

Para saber si un niño está en su peso ideal, no usamos una simple división. Cruzamos su **IMC** real con su **edad exacta en meses** y lo comparamos contra las tablas de crecimiento de la OMS (2007). Estas tablas nos dicen cuál es el "camino" (curva) que debería seguir un niño sano. Si el punto del menor cae muy arriba o muy abajo de esa curva central (predichos), lanzamos la alerta.

## Uso

### 1. Procesar datos crudos

```bash
python src/process_data.py --input data/raw/IMC\ FEDERAL.xlsx --output-dir data/processed
```

Esto filtra los registros (percentiles < 15 o > 85.1) y los divide por zona/escuela.

### 2. Generar reportes PDF

```bash
python src/nutritional_app.py
```

Abre una interfaz gráfica donde puedes seleccionar archivos individuales o carpetas completas, activar/desactivar procesamiento paralelo y ver el progreso.

Para modo benchmark sin GUI:

```bash
python src/nutritional_app.py --benchmark data/processed/IMC_FILTERED.csv
```

## Instalacion

```bash
git clone [repo]
cd GMRN
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Nota sobre datos:** La carpeta `data/` no está en el repo por contener información sensible de menores. Si necesitas los datos contacta al administrador para obtener el archivo `data.zip` y descomprímelo en la raíz del proyecto.

### Columnas requeridas en el Excel

El archivo de entrada debe tener estas columnas:

**Obligatorias para generar PDFs:**
- NOMBRE_ALU - nombre del menor
- MESES - edad en meses
- IMC - índice de masa corporal
- GÉNERO - M/MASCULINO o F/FEMENINO

**Necesarias para filtrado:**
- PERCENTILES - para filtrar casos < 15 o > 85.1
- ZONA_EF - para dividir por zona
- ESCUELA - para dividir por escuela

**Opcionales (recomendadas):**
- PESO_Kg, TALLA_Mts, FECHA_NAC, FECHA_TAM, CURP

## Estructura del proyecto

```
GMRN/
├── data/
│   ├── raw/              # Datos originales (Excel de zonas escolares)
│   ├── processed/        # Datos filtrados y divididos
│   └── references/       # Tablas OMS (bmi-boys/girls-z-who-2007-exp.xlsx)
├── src/
│   ├── process_data.py   # Script de filtrado y división
│   ├── nutritional_app.py # Generador de PDFs (GUI + batch)
│   └── logger.py         # Sistema de logs JSON
├── logs/                 # Logs de ejecución
└── requirements.txt
```

## Dependencias principales

- pandas - manejo de datos
- matplotlib - generación de gráficas
- openpyxl - lectura/escritura Excel
- pypdf - combinación de PDFs
- tkinter - interfaz gráfica (incluido en Python)

## Stack técnico

Python 3.12+ con matplotlib (backend Agg para generacion sin GUI), multiprocessing para PDFs en paralelo. Los logs van a formato JSON.

## Notas sobre la evolución del proyecto

Este código consolidó scripts que originalmente corrían manualmente en Google Colab durante 2 años. La versión inicial solo generaba gráficas individuales usando bucles secuenciales y requería subir archivos manualmente.

Principales mejoras desde la versión Colab:

- Ejecución local sin depender de internet
- Procesamiento por lotes (miles de registros)
- Paralelización con multiprocessing
- Generación de 3 páginas por menor (antes solo 1 gráfica)
- Interfaz GUI para facilitar uso por personal no técnico

Los datos se procesan offline y los PDFs se pueden imprimir directamente para entregar a padres/tutores.
