# Benchmark de LLM de pesos abiertos para la elicitación de requisitos y obtención de resultados

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-orange.svg)
![Pandas](https://img.shields.io/badge/data-pandas-150458.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Este repositorio contiene un flujo de trabajo (pipeline) automatizado para la **elicitación de requisitos de ingeniería** utilizando modelos de lenguaje de gran escala (LLMs) locales y la consolidación de resultados en formatos estructurados para análisis.

---

## 🌟 Características

* **Multi-Modelo:** Soporte nativo para `deepseek-r1`, `gemma3`, `llama3.1`, `qwen3` y `gpt-oss` a través de **Ollama**.
* **Gestión de VRAM:** Incluye rutinas de *Warm-up* (precarga) y *Unload* para optimizar el uso de la GPU.
* **Resiliencia:** Manejo de reintentos automáticos, timeouts y logs detallados de errores.
* **Consolidación Inteligente:** Procesa archivos `.md` y `.txt` dispersos para generar un único **Master Excel** limpio y sin duplicados.

---

## 📂 Estructura del Proyecto

```text
.
├── textos/
│   └── es/                    # 📥 Coloca aquí tus archivos .txt de origen
├── salida_estudio/            # 📤 Resultados intermedios y finales (Auto-generado)
├── prompt_es_few_shot.txt     # 📝 Plantilla de prompt (requiere marcador [system_text])
├── requirements.txt           # 📦 Dependencias mínimas
├── extract_requirements.py    # 🚀 Script 2: Interacción con la API de Ollama
└── consolidate_results.py     # 📊 Script 1: Procesador y exportador a Excel
```text

# 🤖 LLM Requirements Elicitation & Consolidation Pipeline

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-orange.svg)
![Pandas](https://img.shields.io/badge/data-pandas-150458.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Este repositorio contiene un flujo de trabajo (pipeline) automatizado para la **elicitación de requisitos de ingeniería** utilizando modelos de lenguaje de gran escala (LLMs) locales y la consolidación de resultados en formatos estructurados para análisis.

---

## 🌟 Características

* **Multi-Modelo:** Soporte nativo para `deepseek-r1`, `gemma3`, `llama3.1`, `qwen3` y `gpt-oss` a través de **Ollama**.
* **Gestión de VRAM:** Incluye rutinas de *Warm-up* (precarga) y *Unload* para optimizar el uso de la GPU.
* **Resiliencia:** Manejo de reintentos automáticos, timeouts y logs detallados de errores.
* **Consolidación Inteligente:** Procesa archivos `.md` y `.txt` dispersos para generar un único **Master Excel** limpio y sin duplicados.

---

## 🚀 Flujo de Ejecución
### Paso 1: Extracción de Requisitos

Ejecuta el programa de extracción para procesar los textos con los modelos configurados:
Bash

python extractor_llm.py

    Funcionalidad: Envía los documentos a Ollama, gestiona la precarga/descarga de VRAM y guarda las respuestas en archivos .md.

    Métricas: Genera un archivo master_results.csv con tiempos de respuesta y conteo de tokens.

### Paso 2: Consolidación a Excel

Una vez terminada la fase anterior, unifica todos los requisitos detectados:
Bash

python procesa_salidas.py

    Funcionalidad: Escanea la carpeta salida_estudio/, limpia el formato, elimina duplicados y genera el archivo final.

    Resultado: consolidado_final_requisitos.xlsx.

## 📝 Formato del Prompt

Para que el consolidador pueda parsear correctamente los resultados, el archivo prompt_es_few_shot.txt debe instruir al modelo a responder utilizando el punto y coma (;) como separador.

Ejemplo de estructura esperada en el prompt:
`

Extrae los requisitos del siguiente texto técnico. 
Responde ÚNICAMENTE con líneas siguiendo este formato:
ID; Descripción del Requisito; Fragmento de origen

Texto a procesar:
[system_text]
`

## 📊 Archivos de Salida
| Archivo | EDescripción |
| :--- | :--- |
| proceso.log | Historial técnico de errores y conexiones API. |
| master_results.csv | Reporte de rendimiento y calidad de los modelos. |
| consolidado_final_requisitos.xlsx | Base de datos final de requisitos estructurada. |