# Benchmark de LLM de pesos abiertos para la elicitación de requisitos y obtención de resultados

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-orange.svg)
![Pandas](https://img.shields.io/badge/data-pandas-150458.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Este repositorio contiene un flujo de trabajo (pipeline) automatizado para la **elicitación de requisitos de ingeniería** utilizando modelos de lenguaje LLM locales y la consolidación de resultados en formatos estructurados para análisis.

---

## Características

* **Multi-Modelo:** Soporte nativo para `deepseek-r1`, `gemma3`, `llama3.1`, `qwen3` y `gpt-oss` a través de **Ollama**.
* **Gestión de VRAM:** Incluye rutinas de *Warm-up* (precarga) y *Unload* para optimizar el uso de la GPU.
* **Resiliencia:** Manejo de reintentos automáticos, timeouts y logs detallados de errores.
* **Consolidación Inteligente:** Procesa archivos `.md` y `.txt` dispersos para generar un único **Master Excel** limpio y sin duplicados.

---

## Estructura del Proyecto

```
.
├── textos/
│   └── es/                    # descripciones de proyectos de desarrollo de Software en formato texto natural (1)
├── salida_estudio/            # Resultado del proceso de elicitación por LLM (2)
├── prompt_es_few_shot.txt     # Prompt utilizado en el proceso (3)
├── requirements.txt           # Dependencias mínimas para ejecutar (4)
├── extract_requirements.py    # Ejecuta de forma automatizada los modelos sobre el texto de los proyectos de (1) generando las salidas en (2)
└── consolidate_results.py     # Exporta todas las salidas generadas en (2), consolidando en un solo fichero Excel
```

## Flujo de Ejecución
### Paso 1: Extracción de Requisitos

Ejecuta el programa de extracción para procesar los textos con los modelos configurados:

```
python test_models.py
```
- Funcionalidad: Envía los documentos a Ollama, gestiona la precarga/descarga de VRAM y guarda las respuestas en archivos .md.
- Métricas: Genera un archivo master_results.csv con tiempos de respuesta y conteo de tokens.

### Paso 2: Consolidación a Excel

Una vez terminada la fase anterior, unifica todos los requisitos detectados:

```
python procesa_salidas.py
```
- Funcionalidad: Escanea la carpeta salida_estudio/, limpia el formato y genera el archivo final.
- Resultado: consolidado_final_requisitos.xlsx.

## Archivos de Salida
| Archivo | Descripción |
| :--- | :--- |
| proceso.log | Historial técnico de errores y conexiones API. |
| master_results.csv | Reporte de rendimiento y calidad de los modelos. Almacena los tiempos de resultado, verifica si las respuestas son válidas (no están en blanco), y agrega información de tiempos y tokens utilizado |
| consolidado_final_requisitos.xlsx | Base de datos final de requisitos estructurada. |