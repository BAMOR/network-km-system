#!/usr/bin/env python3
"""
================================================================================
Script: monitor_enlaces.py
Propósito: Monitorear enlaces WAN principales mediante ping continuo
Autor: Departamento de TI - Banco Tecnológico
Versión: 1.0
Fecha: 2024-01-15
Dependencias: Python 3.6+, pandas (opcional para reportes)
Uso: python3 monitor_enlaces.py
Cron: */5 * * * * /usr/bin/python3 /opt/banco/scripts/monitor_enlaces.py
================================================================================
"""

import subprocess
import sys
import json
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional
import time

# ==============================================================================
# CONFIGURACIÓN GLOBAL
# ==============================================================================

# Directorios y archivos
LOG_DIR = Path("/var/log/banco")
LOG_FILE = LOG_DIR / "monitor_enlaces.log"
ALERTS_FILE = LOG_DIR / "alertas_enlaces.json"
CONFIG_FILE = Path("/opt/banco/config/enlaces_monitor.json")

# Configuración de correo
SMTP_SERVER = "smtp.banco.local"
SMTP_PORT = 587
EMAIL_FROM = "monitoreo@banco.local"
EMAIL_TO = ["network-team@banco.local", "noc@banco.local"]
EMAIL_PASSWORD = ""  # Cargar desde vault en producción

# Umbrales de alerta
LATENCIA_ALTA_MS = 100  # Latencia considerada alta
LATENCIA_CRITICA_MS = 200  # Latencia crítica
PERDIDA_ALTA_PCT = 10  # Porcentaje de pérdida considerado alto
PERDIDA_CRITICA_PCT = 50  # Porcentaje de pérdida crítico

# Intervalos
PING_COUNT = 5  # Número de pings por verificación
PING_INTERVAL = 1  # Segundos entre pings
TIMEOUT = 2  # Timeout por ping en segundos

# ==============================================================================
# CONFIGURACIÓN DE LOGGING
# ==============================================================================

def setup_logging():
    """Configurar el sistema de logging."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ==============================================================================
# CLASES PRINCIPALES
# ==============================================================================

class EnlaceMonitor:
    """Clase para monitorear un enlace WAN específico."""
    
    def __init__(self, nombre: str, destino: str, descripcion: str, prioridad: str = "normal"):
        self.nombre = nombre
        self.destino = destino
        self.descripcion = descripcion
        self.prioridad = prioridad  # critica, normal, baja
        
        # Estadísticas
        self.latencia_actual = 0.0
        self.perdida_actual = 0.0
        self.estado = "desconocido"  # up, down, degradado
        self.ultimo_cambio = datetime.now()
        
    def ejecutar_ping(self) -> Dict:
        """
        Ejecutar ping al destino y retornar resultados.
        
        Returns:
            Dict con latencia_promedio, perdida_porcentaje, exitoso
        """
        try:
            comando = [
                "ping",
                "-c", str(PING_COUNT),
                "-i", str(PING_INTERVAL),
                "-W", str(TIMEOUT),
                self.destino
            ]
            
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=PING_COUNT * (PING_INTERVAL + TIMEOUT) + 5
            )
            
            # Parsear output del ping
            output = resultado.stdout
            return self._parse_ping_output(output)
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout en ping a {self.nombre} ({self.destino})")
            return {"latencia_promedio": 0, "perdida_porcentaje": 100, "exitoso": False}
        except Exception as e:
            logger.error(f"Error ejecutando ping a {self.nombre}: {str(e)}")
            return {"latencia_promedio": 0, "perdida_porcentaje": 100, "exitoso": False}
    
    def _parse_ping_output(self, output: str) -> Dict:
        """
        Parsear el output del comando ping.
        
        Args:
            output: Output crudo del comando ping
            
        Returns:
            Dict con estadísticas parseadas
        """
        resultado = {
            "latencia_promedio": 0.0,
            "perdida_porcentaje": 0.0,
            "exitoso": False,
            "min": 0.0,
            "max": 0.0,
            "avg": 0.0,
            "mdev": 0.0
        }
        
        lines = output.strip().split('\n')
        
        # Buscar línea de estadísticas (rtt min/avg/max/mdev)
        for line in lines:
            if 'rtt' in line.lower() or 'round-trip' in line.lower():
                try:
                    # Formato típico: rtt min/avg/max/mdev = 10.5/15.2/25.3/5.1 ms
                    partes = line.split('=')[1].strip()
                    valores = [float(x) for x in partes.split('/')]
                    
                    if len(valores) >= 4:
                        resultado["min"] = valores[0]
                        resultado["avg"] = valores[1]
                        resultado["max"] = valores[2]
                        resultado["mdev"] = valores[3]
                        resultado["latencia_promedio"] = valores[1]
                        resultado["exitoso"] = True
                except (IndexError, ValueError):
                    pass
        
        # Buscar porcentaje de pérdida
        for line in lines:
            if 'packet loss' in line.lower():
                try:
                    # Formato típico: 5 packets transmitted, 5 received, 0% packet loss
                    partes = line.split(',')
                    for parte in partes:
                        if 'loss' in parte.lower():
                            perdida = float(parte.strip().replace('%', '').replace('packet loss', ''))
                            resultado["perdida_porcentaje"] = perdida
                            break
                except (IndexError, ValueError):
                    pass
        
        # Determinar si fue exitoso basado en pérdida
        if resultado["perdida_porcentaje"] < 100:
            resultado["exitoso"] = True
        
        return resultado
    
    def actualizar_estado(self, resultado_ping: Dict):
        """
        Actualizar el estado del enlace basado en resultados de ping.
        
        Args:
            resultado_ping: Diccionario con resultados del ping
        """
        estado_anterior = self.estado
        
        self.latencia_actual = resultado_ping.get("latencia_promedio", 0)
        self.perdida_actual = resultado_ping.get("perdida_porcentaje", 0)
        
        # Determinar estado
        if self.perdida_actual >= PERDIDA_CRITICA_PCT:
            self.estado = "down"
        elif self.perdida_actual >= PERDIDA_ALTA_PCT or \
             self.latencia_actual >= LATENCIA_CRITICA_MS:
            self.estado = "degradado"
        else:
            self.estado = "up"
        
        # Registrar cambio de estado
        if estado_anterior != self.estado and estado_anterior != "desconocido":
            logger.warning(
                f"Cambio de estado en {self.nombre}: "
                f"{estado_anterior} -> {self.estado}"
            )
            self.ultimo_cambio = datetime.now()
    
    def generar_alerta(self) -> Optional[Dict]:
        """
        Generar alerta si los umbrales son superados.
        
        Returns:
            Dict con información de alerta o None si no hay alerta
        """
        alerta = None
        
        if self.perdida_actual >= PERDIDA_CRITICA_PCT:
            alerta = {
                "nivel": "CRITICO",
                "tipo": "PERDIDA_TOTAL",
                "mensaje": f"Pérdida de conectividad en {self.nombre} ({self.descripcion})",
                "destino": self.destino,
                "perdida": self.perdida_actual,
                "latencia": self.latencia_actual,
                "timestamp": datetime.now().isoformat()
            }
        elif self.perdida_actual >= PERDIDA_ALTA_PCT:
            alerta = {
                "nivel": "ALTO",
                "tipo": "PERDIDA_PARCIAL",
                "mensaje": f"Pérdida parcial de paquetes en {self.nombre}: {self.perdida_actual}%",
                "destino": self.destino,
                "perdida": self.perdida_actual,
                "latencia": self.latencia_actual,
                "timestamp": datetime.now().isoformat()
            }
        elif self.latencia_actual >= LATENCIA_CRITICA_MS:
            alerta = {
                "nivel": "ALTO",
                "tipo": "LATENCIA_CRITICA",
                "mensaje": f"Latencia crítica en {self.nombre}: {self.latencia_actual}ms",
                "destino": self.destino,
                "perdida": self.perdida_actual,
                "latencia": self.latencia_actual,
                "timestamp": datetime.now().isoformat()
            }
        elif self.latencia_actual >= LATENCIA_ALTA_MS:
            alerta = {
                "nivel": "MEDIO",
                "tipo": "LATENCIA_ALTA",
                "mensaje": f"Latencia elevada en {self.nombre}: {self.latencia_actual}ms",
                "destino": self.destino,
                "perdida": self.perdida_actual,
                "latencia": self.latencia_actual,
                "timestamp": datetime.now().isoformat()
            }
        
        return alerta


class MonitorEnlaces:
    """Clase principal para monitorear múltiples enlaces WAN."""
    
    def __init__(self):
        self.enlaces: List[EnlaceMonitor] = []
        self.alertas_recientes: List[Dict] = []
        self.cargar_configuracion()
    
    def cargar_configuracion(self):
        """Cargar configuración de enlaces desde archivo JSON."""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                
                for enlace_config in config.get("enlaces", []):
                    enlace = EnlaceMonitor(
                        nombre=enlace_config["nombre"],
                        destino=enlace_config["destino"],
                        descripcion=enlace_config.get("descripcion", ""),
                        prioridad=enlace_config.get("prioridad", "normal")
                    )
                    self.enlaces.append(enlace)
                
                logger.info(f"Cargados {len(self.enlaces)} enlaces para monitoreo")
            else:
                # Configuración por defecto
                logger.warning("Archivo de configuración no encontrado, usando defaults")
                self._configuracion_defecto()
                
        except Exception as e:
            logger.error(f"Error cargando configuración: {str(e)}")
            self._configuracion_defecto()
    
    def _configuracion_defecto(self):
        """Crear configuración por defecto para demostración."""
        enlaces_defecto = [
            {
                "nombre": "WAN-PRINCIPAL-MPLS",
                "destino": "200.10.50.2",
                "descripcion": "Enlace MPLS principal hacia datacenter",
                "prioridad": "critica"
            },
            {
                "nombre": "WAN-RESPALDO-4G",
                "destino": "198.51.100.2",
                "descripcion": "Enlace 4G LTE de respaldo",
                "prioridad": "critica"
            },
            {
                "nombre": "INTERNET-DIRECTO",
                "destino": "8.8.8.8",
                "descripcion": "Conectividad directa a Internet",
                "prioridad": "normal"
            }
        ]
        
        for enlace_config in enlaces_defecto:
            enlace = EnlaceMonitor(**enlace_config)
            self.enlaces.append(enlace)
    
    def monitorear_todos(self):
        """Ejecutar monitoreo de todos los enlaces."""
        logger.info("=" * 60)
        logger.info("Iniciando ciclo de monitoreo de enlaces WAN")
        logger.info("=" * 60)
        
        for enlace in self.enlaces:
            logger.info(f"Monitoreando {enlace.nombre} ({enlace.destino})")
            
            # Ejecutar ping
            resultado = enlace.ejecutar_ping()
            
            # Actualizar estado
            enlace.actualizar_estado(resultado)
            
            # Log resultado
            logger.info(
                f"Resultado {enlace.nombre}: Estado={enlace.estado}, "
                f"Latencia={enlace.latencia_actual:.2f}ms, "
                f"Pérdida={enlace.perdida_actual:.1f}%"
            )
            
            # Verificar alertas
            alerta = enlace.generar_alerta()
            if alerta:
                self.alertas_recientes.append(alerta)
                logger.warning(
                    f"ALERTA [{alerta['nivel']}]: {alerta['mensaje']}"
                )
        
        # Procesar alertas
        self._procesar_alertas()
        
        # Guardar estado actual
        self._guardar_estado()
        
        logger.info("Ciclo de monitoreo completado")
    
    def _procesar_alertas(self):
        """Procesar y enviar alertas generadas."""
        if not self.alertas_recientes:
            return
        
        # Filtrar alertas críticas para envío inmediato
        alertas_criticas = [
            a for a in self.alertas_recientes 
            if a["nivel"] in ["CRITICO", "ALTO"]
        ]
        
        if alertas_criticas:
            self._enviar_email_alertas(alertas_criticas)
            self._guardar_alertas(alertas_criticas)
        
        # Limpiar alertas antiguas (mantener últimas 100)
        if len(self.alertas_recientes) > 100:
            self.alertas_recientes = self.alertas_recientes[-100:]
    
    def _enviar_email_alertas(self, alertas: List[Dict]):
        """Enviar email con alertas críticas."""
        try:
            asunto = f"[ALERTA MONITOREO] {len(alertas)} alertas detectadas - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            cuerpo = "=============================================================\n"
            cuerpo += "ALERTAS DE MONITOREO DE ENLACES WAN\n"
            cuerpo += "Banco Tecnológico - Departamento de TI\n"
            cuerpo += "=============================================================\n\n"
            
            for alerta in alertas:
                cuerpo += f"NIVEL: {alerta['nivel']}\n"
                cuerpo += f"TIPO: {alerta['tipo']}\n"
                cuerpo += f"MENSAJE: {alerta['mensaje']}\n"
                cuerpo += f"DESTINO: {alerta['destino']}\n"
                cuerpo += f"LATENCIA: {alerta['latencia']:.2f} ms\n"
                cuerpo += f"PÉRDIDA: {alerta['perdida']:.1f}%\n"
                cuerpo += f"TIMESTAMP: {alerta['timestamp']}\n"
                cuerpo += "-" * 60 + "\n"
            
            cuerpo += "\n=============================================================\n"
            cuerpo += "Este es un mensaje automático del sistema de monitoreo.\n"
            cuerpo += "=============================================================\n"
            
            msg = MIMEMultipart()
            msg['From'] = EMAIL_FROM
            msg['To'] = ", ".join(EMAIL_TO)
            msg['Subject'] = asunto
            msg.attach(MIMEText(cuerpo, 'plain'))
            
            # En producción, configurar autenticación SMTP real
            # server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            # server.starttls()
            # server.login(EMAIL_FROM, EMAIL_PASSWORD)
            # server.send_message(msg)
            # server.quit()
            
            logger.info(f"Email de alerta enviado a {', '.join(EMAIL_TO)}")
            
        except Exception as e:
            logger.error(f"Error enviando email de alerta: {str(e)}")
    
    def _guardar_alertas(self, alertas: List[Dict]):
        """Guardar alertas en archivo JSON para histórico."""
        try:
            historial = []
            if ALERTS_FILE.exists():
                with open(ALERTS_FILE, 'r') as f:
                    historial = json.load(f)
            
            historial.extend(alertas)
            
            # Mantener solo últimas 1000 alertas
            historial = historial[-1000:]
            
            with open(ALERTS_FILE, 'w') as f:
                json.dump(historial, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error guardando alertas: {str(e)}")
    
    def _guardar_estado(self):
        """Guardar estado actual de enlaces para dashboard."""
        estado_actual = {
            "timestamp": datetime.now().isoformat(),
            "enlaces": []
        }
        
        for enlace in self.enlaces:
            estado_actual["enlaces"].append({
                "nombre": enlace.nombre,
                "destino": enlace.destino,
                "descripcion": enlace.descripcion,
                "prioridad": enlace.prioridad,
                "estado": enlace.estado,
                "latencia_ms": round(enlace.latencia_actual, 2),
                "perdida_pct": round(enlace.perdida_actual, 1),
                "ultimo_cambio": enlace.ultimo_cambio.isoformat()
            })
        
        estado_file = LOG_DIR / "estado_enlaces.json"
        try:
            with open(estado_file, 'w') as f:
                json.dump(estado_actual, f, indent=2)
        except Exception as e:
            logger.error(f"Error guardando estado: {str(e)}")
    
    def generar_reporte(self) -> str:
        """Generar reporte textual del estado actual."""
        reporte = "=" * 70 + "\n"
        reporte += "REPORTE DE ESTADO DE ENLACES WAN - BANCO TECNOLÓGICO\n"
        reporte += f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        reporte += "=" * 70 + "\n\n"
        
        for enlace in self.enlaces:
            icono = "✅" if enlace.estado == "up" else "⚠️" if enlace.estado == "degradado" else "❌"
            
            reporte += f"{icono} {enlace.nombre} ({enlace.descripcion})\n"
            reporte += f"   Destino: {enlace.destino}\n"
            reporte += f"   Estado: {enlace.estado.upper()}\n"
            reporte += f"   Latencia: {enlace.latencia_actual:.2f} ms\n"
            reporte += f"   Pérdida: {enlace.perdida_actual:.1f}%\n"
            reporte += f"   Prioridad: {enlace.prioridad}\n"
            reporte += "\n"
        
        reporte += "=" * 70 + "\n"
        reporte += "UMBRALES CONFIGURADOS:\n"
        reporte += f"  - Latencia Alta: {LATENCIA_ALTA_MS} ms\n"
        reporte += f"  - Latencia Crítica: {LATENCIA_CRITICA_MS} ms\n"
        reporte += f"  - Pérdida Alta: {PERDIDA_ALTA_PCT}%\n"
        reporte += f"  - Pérdida Crítica: {PERDIDA_CRITICA_PCT}%\n"
        reporte += "=" * 70 + "\n"
        
        return reporte


# ==============================================================================
# PROGRAMA PRINCIPAL
# ==============================================================================

def main():
    """Función principal del script."""
    logger.info("Iniciando monitor de enlaces WAN v1.0")
    
    # Crear instancia del monitor
    monitor = MonitorEnlaces()
    
    # Ejecutar monitoreo
    monitor.monitorear_todos()
    
    # Generar y mostrar reporte
    reporte = monitor.generar_reporte()
    print(reporte)
    
    # Guardar reporte en archivo
    reporte_file = LOG_DIR / f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(reporte_file, 'w') as f:
            f.write(reporte)
        logger.info(f"Reporte guardado en {reporte_file}")
    except Exception as e:
        logger.error(f"Error guardando reporte: {str(e)}")
    
    logger.info("Script finalizado")


if __name__ == "__main__":
    main()
