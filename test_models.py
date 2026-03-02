import requests
import json
import logging
import time
import csv
from datetime import datetime
from pathlib import Path

# --- CONFIGURACIÓN ---
BASE_DIR_TEXTOS = Path("./textos/es")
BASE_SALIDA = Path("./salida_estudio")
PROMPT_FILE = Path("./prompt_es_few_shot.txt")
OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = ["gpt-oss:20b", "deepseek-r1:32b", "gemma3:27b", "llama3.1:70b", "qwen3:30b"]


# --- INICIALIZACIÓN ---
BASE_SALIDA.mkdir(parents=True, exist_ok=True)
csv_metrics_path = BASE_SALIDA / "master_results.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(BASE_SALIDA / "proceso.log"), logging.StreamHandler()]
)


def is_model_loaded(model):
    """
    Verifica si el modelo está actualmente cargado en memoria.
    
    Returns:
        bool: True si está cargado, False si no
    """
    try:
        response = requests.get("http://localhost:11434/api/ps", timeout=5)
        response.raise_for_status()
        loaded_models = response.json().get("models", [])
        
        for loaded in loaded_models:
            if loaded.get("name") == model:
                return True
        return False
    except Exception as e:
        logging.warning(f"No se pudo verificar modelos cargados: {e}")
        return False


def warm_up_model(model, max_wait=2400):
    """
    Precarga el modelo en memoria/VRAM y espera a que esté listo.
    Hace una inferencia dummy para asegurar inicialización completa.
    
    Args:
        model: Nombre del modelo a precargar
        max_wait: Tiempo máximo de espera en segundos
    
    Returns:
        bool: True si se cargó exitosamente, False si falló
    """
    logging.info(f"🔄 Precargando modelo: {model}")
    
    warmup_payload = {
        "model": model,
        "prompt": "Test",
        "stream": False,
        "options": {
            "num_predict": 1,
            "num_ctx": 2048
        }
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json=warmup_payload,
            timeout=max_wait
        )
        response.raise_for_status()
        
        elapsed = round(time.time() - start_time, 2)
        
        if is_model_loaded(model):
            logging.info(f"✅ Modelo cargado en {elapsed}s")
            time.sleep(2)  # Pausa para estabilización
            return True
        else:
            logging.warning(f"⚠️  Modelo respondió pero no aparece en lista de cargados")
            return True
            
    except requests.exceptions.Timeout:
        logging.error(f"❌ Timeout al cargar modelo (>{max_wait}s)")
        return False
    except Exception as e:
        logging.error(f"❌ Error al precargar modelo: {e}")
        return False


def unload_model(model):
    """
    Descarga el modelo de memoria para liberar recursos.
    
    Args:
        model: Nombre del modelo a descargar
    """
    try:
        payload = {
            "model": model,
            "keep_alive": 0
        }
        
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logging.info(f"🗑️  Modelo descargado: {model}")
        
    except Exception as e:
        logging.warning(f"No se pudo descargar modelo: {e}")


def call_ollama_api(model, prompt, timeout=25*60):
    """
    Llamada robusta a la API con manejo de errores.
    IMPORTANTE: Asume que el modelo ya está precargado con warm_up_model()
    
    Args:
        model: Nombre del modelo en Ollama
        prompt: Texto del prompt
        timeout: Segundos máximos de espera (default: 25 minutos)
    
    Returns:
        tuple: (response_text, status_dict)
    """

    payload_qwen = {
        "model": "qwen3:30b",
        "prompt": prompt,
        "stream": False,
        "keep_alive": "20m",
        "options": {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 20,
            "min_p": 0,
            
            # CRÍTICOS para tu 16GB VRAM:
            "num_ctx": 32768,        # Reduce de 65536 a 32K para ahorrar VRAM
            "num_predict": 16384,    # Ajustado proporcionalmente
            "num_batch": 512,        # Reduce de 2048 a 512 (menos VRAM)
            
            # GPU
            #"num_gpu": 99,           # Carga todo en tu única GPU
            
            # Rope scaling (si tu Ollama lo soporta)
            "rope_frequency_scale": 0.25,  # Para 32K (1/4 en lugar de 1/8)
        }
    }
    
    payload_gemma = {
        "model": "gemma3:27b",
        "prompt": prompt,
        "stream": False,
        "keep_alive": "20m",
        "options": {
            "temperature": 0.0,
            "top_p": 1.0,
            "top_k": 1,
            "num_ctx": 4096,
            "repeat_penalty": 1.0
        }
    }

    payload_gpt_oss = {
        "model": "gpt-oss:20b",
        "prompt": prompt,
        "stream": False,
        "keep_alive": "20m",
        "options": {
            "temperature": 0.0,      # Determinista
            "top_k": 1,              # Solo el mejor token
            "repeat_penalty": 1.0,   
            "num_ctx": 16384,        # ✅ Aumentado
            "num_predict": 8192
        }
    }

    payload_deepseek = {
        "model": "deepseek-r1:32b",
        "prompt": prompt,
        "stream": False,
        "keep_alive": "20m",
        "options": {
            "temperature": 0.0,      # Determinista
            "top_k": 1,              # Solo el mejor token
            "repeat_penalty": 1.0,   
            "num_ctx": 4096,          # ✅ Aumentado (DeepSeek-R1 soporta hasta 64K)
            "num_predict": 4096,      # ✅ Añadido
        }
    }

    payload_llama = {
        "model": "llama3.1:70b",
        "prompt": prompt,
        "stream": False,
        "keep_alive": "20m",
        "options": {
            "temperature": 0.0,      # Determinista
            "top_k": 1,              # Solo el mejor token
            "repeat_penalty": 1.0,   
            "num_ctx": 8192,         # ✅ Aumentado (Llama 3.1 soporta 128K)
            "num_predict": 4096      # ✅ Añadido
        }
    }

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "20m",
        "options": {
            "temperature": 0.0,
            "top_p": 1.0,
            "top_k": 1,
            "repeat_penalty": 1.0
        }
    }

    if model == "qwen3:30b":
        payload = payload_qwen
    elif model == "gemma3:27b":
        payload = payload_gemma
    elif model == "gpt-oss:20b":
        payload = payload_gpt_oss
    elif model == "deepseek-r1:32b":
        payload = payload_deepseek
    elif model == "llama3.1:70b":
        payload = payload_llama
    else:
        payload = payload

    logging.info(f"🚀 Llamando a API: {model} (timeout={timeout}s, options={payload['options']})")
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        result = response.json()
        
        response_text = result.get("response", "").strip()
        
        if not response_text:
            logging.warning(f"⚠️  {model}: Respuesta vacía detectada")
            return None, {
                "success": False,
                "error": "empty_response",
                "model": model
            }
        
        return response_text, {
            "success": True,
            "model": model,
            "tokens": result.get("eval_count", 0),
            "duration": result.get("total_duration", 0) / 1e9,
        }
        
    except requests.exceptions.Timeout:
        logging.error(f"⏱️  {model}: Timeout después de {timeout}s")
        return None, {
            "success": False,
            "error": "timeout",
            "model": model,
            "timeout": timeout
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ {model}: Error de conexión - {e}")
        return None, {
            "success": False,
            "error": "connection_error",
            "model": model,
            "details": str(e)
        }
    except Exception as e:
        logging.error(f"❌ {model}: Error inesperado - {e}")
        return None, {
            "success": False,
            "error": "unknown",
            "model": model,
            "details": str(e)
        }


def call_with_retry(model, prompt, max_retries=2):
    """
    Llama a la API con reintentos automáticos si falla.
    
    Args:
        model: Nombre del modelo
        prompt: Texto del prompt
        max_retries: Número máximo de reintentos
    
    Returns:
        tuple: (response_text, status_dict)
    """
    for attempt in range(max_retries):
        response_text, status = call_ollama_api(model, prompt)
        
        if status["success"] and response_text:
            return response_text, status
        
        if attempt < max_retries - 1:
            error_type = status.get("error", "unknown")
            
            if error_type in ["empty_response", "timeout"]:
                logging.info(f"🔄 {model}: Reintento {attempt + 2}/{max_retries}")
            else:
                logging.error(f"    ❌ Error fatal, cancelando reintentos")
                break
    
    return None, {
        "success": False,
        "error": "max_retries_exceeded",
        "model": model,
        "attempts": max_retries
    }


def sanitize_for_csv(text):
    """Limpia texto para que sea seguro en CSV"""
    if not text:
        return ""
    return text.replace("\n", " ").replace("\r", " ").replace('"', '""')


def main():
    logging.info("="*60)
    logging.info("INICIANDO PROCESO DE EXTRACCIÓN DE REQUISITOS")
    logging.info("="*60)
    
    # 1. Cargar Prompt
    if not PROMPT_FILE.exists():
        logging.error(f"❌ No se encontró el archivo de prompt: {PROMPT_FILE}")
        return
    
    prompt_template = PROMPT_FILE.read_text(encoding="utf-8")
    logging.info(f"✅ Prompt cargado: {PROMPT_FILE}")
    
    # 2. Listar archivos de texto
    text_files = sorted([p for p in BASE_DIR_TEXTOS.glob("*.txt")])
    if not text_files:
        logging.error(f"❌ No se encontraron archivos .txt en: {BASE_DIR_TEXTOS}")
        return
    
    logging.info(f"✅ Encontrados {len(text_files)} archivos de texto")
    for txt_file in text_files:
        logging.info(f"   - {txt_file.name}")
    
    # 3. Preparar CSV Maestro
    file_exists = csv_metrics_path.exists()
    with open(csv_metrics_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        
        if not file_exists:
            writer.writerow([
                "Timestamp", 
                "Modelo", 
                "Proyecto", 
                "Tiempo_Seg", 
                "Tokens_Generados",
                "Status", 
                "Error_Tipo",
                "Resultado_Raw"
            ])
            logging.info(f"✅ CSV maestro creado: {csv_metrics_path}")
        
        # 4. Procesar cada modelo
        total_tasks = len(MODELS) * len(text_files)
        current_task = 0
        
        for model in MODELS:
            logging.info("")
            logging.info("🔷"*30)
            logging.info(f"PROCESANDO MODELO: {model}")
            logging.info("🔷"*30)
            
            # ⭐ PRECARGA DEL MODELO (WARMUP)
            if not warm_up_model(model, max_wait=120):
                logging.error(f"❌ No se pudo cargar {model}, saltando...")
                
                # Registra todos los archivos como fallidos
                for txt_file in text_files:
                    current_task += 1
                    writer.writerow([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        model,
                        txt_file.name,
                        0,
                        0,
                        "ERROR",
                        "model_load_failed",
                        ""
                    ])
                    f.flush()
                continue
            
            # Procesar todos los archivos con el modelo ya cargado
            for txt_file in text_files:
                current_task += 1
                logging.info("")
                logging.info("="*60)
                logging.info(f"📊 Tarea {current_task}/{total_tasks}")
                logging.info(f"   Modelo: {model}")
                logging.info(f"   Archivo: {txt_file.name}")
                logging.info("="*60)
                
                texto_entrada = txt_file.read_text(encoding="utf-8")
                prompt_final = prompt_template.replace("[system_text]", texto_entrada)
                
                start_time = time.time()
                output, status = call_with_retry(model, prompt_final, max_retries=2)
                elapsed = round(time.time() - start_time, 2)
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tokens = status.get("tokens", 0) if status["success"] else 0
                status_str = "OK" if status["success"] else "ERROR"
                error_type = status.get("error", "") if not status["success"] else ""
                output_clean = sanitize_for_csv(output) if output else ""
                
                writer.writerow([
                    timestamp,
                    model,
                    txt_file.name,
                    elapsed,
                    tokens,
                    status_str,
                    error_type,
                    output_clean
                ])
                f.flush()
                
                if output:
                    safe_name = f"{model.replace(':', '-')}_{txt_file.stem}.md"
                    output_path = BASE_SALIDA / safe_name
                    output_path.write_text(output, encoding="utf-8")
                    logging.info(f"✅ Guardado en: {safe_name}")
                
                if status["success"]:
                    logging.info(f"✅ Completado exitosamente")
                    logging.info(f"   └─ Tiempo: {elapsed}s")
                    logging.info(f"   └─ Tokens: {tokens}")
                else:
                    logging.error(f"❌ Falló: {error_type}")
                    if status.get("details"):
                        logging.error(f"   └─ Detalles: {status['details']}")
            
            # ⭐ OPCIONAL: Descarga el modelo para liberar memoria
            # Descomenta si tienes RAM/VRAM limitada:
            unload_model(model)
    
    logging.info("")
    logging.info("="*60)
    logging.info("✅ PROCESO COMPLETADO")
    logging.info(f"📁 Resultados guardados en: {BASE_SALIDA}")
    logging.info(f"📊 CSV maestro: {csv_metrics_path}")
    logging.info("="*60)


if __name__ == "__main__":
    main()