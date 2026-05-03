#!/usr/bin/env python3
"""
================================================================================
Script: check_latency.py
Autor: Equipo de Redes
Propósito: Verificar latencia de red hacia múltiples destinos y generar reporte
Dependencias: 
    - Python 3.6+
    - No requiere librerías externas (usa módulos estándar)
Ejemplo de Uso:
    python3 check_latency.py --target 8.8.8.8 --count 10
    python3 check_latency.py --targets targets.txt --output reporte.csv
================================================================================
"""

import subprocess
import sys
import argparse
import json
from datetime import datetime
from typing import List, Dict, Optional


def parse_arguments() -> argparse.Namespace:
    """Parsear argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Verificar latencia de red hacia múltiples destinos'
    )
    parser.add_argument(
        '-t', '--target',
        type=str,
        help='Dirección IP o hostname único para verificar'
    )
    parser.add_argument(
        '-f', '--targets-file',
        type=str,
        help='Archivo de texto con lista de targets (uno por línea)'
    )
    parser.add_argument(
        '-c', '--count',
        type=int,
        default=4,
        help='Número de paquetes ICMP a enviar (default: 4)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Archivo de salida para reporte CSV'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Salida en formato JSON'
    )
    return parser.parse_args()


def check_ping(target: str, count: int = 4) -> Dict:
    """
    Ejecutar ping hacia un target y retornar estadísticas.
    
    Args:
        target: Dirección IP o hostname
        count: Número de paquetes a enviar
    
    Returns:
        Diccionario con resultados del ping
    """
    result = {
        'target': target,
        'timestamp': datetime.now().isoformat(),
        'success': False,
        'packets_sent': count,
        'packets_received': 0,
        'packet_loss': 100.0,
        'min_latency': None,
        'max_latency': None,
        'avg_latency': None,
        'error': None
    }
    
    try:
        # Construir comando ping (compatible con Linux y macOS)
        if sys.platform == 'win32':
            cmd = ['ping', '-n', str(count), target]
        else:
            cmd = ['ping', '-c', str(count), target]
        
        output = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=count * 2 + 5  # Timeout generoso
        )
        
        # Parsear salida
        stdout_lines = output.stdout.split('\n')
        
        for line in stdout_lines:
            if 'packet loss' in line:
                # Extraer porcentaje de pérdida
                try:
                    loss_part = line.split('packet loss')[0].split(',')[-2].strip()
                    result['packet_loss'] = float(loss_part.replace('%', ''))
                except (IndexError, ValueError):
                    pass
            
            if 'rtt min/avg/max' in line or 'round-trip min/avg/max' in line:
                # Extraer latencias (formato: min/avg/max/mdev = x/x/x/x ms)
                try:
                    stats_part = line.split('=')[1].strip()
                    values = stats_part.split('/')[0:3]
                    result['min_latency'] = float(values[0])
                    result['avg_latency'] = float(values[1])
                    result['max_latency'] = float(values[2])
                except (IndexError, ValueError):
                    pass
        
        # Determinar éxito
        result['packets_received'] = count - int(count * result['packet_loss'] / 100)
        result['success'] = result['packets_received'] > 0
        
    except subprocess.TimeoutExpired:
        result['error'] = 'Timeout - El host no responde'
    except Exception as e:
        result['error'] = str(e)
    
    return result


def load_targets_from_file(filepath: str) -> List[str]:
    """Cargar lista de targets desde un archivo."""
    targets = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    targets.append(line)
    except FileNotFoundError:
        print(f"Error: Archivo '{filepath}' no encontrado")
        sys.exit(1)
    return targets


def generate_csv_report(results: List[Dict], output_file: str):
    """Generar reporte en formato CSV."""
    with open(output_file, 'w') as f:
        # Header
        f.write('Target,Timestamp,Success,Packets Sent,Packets Received,')
        f.write('Packet Loss (%),Min Latency,Avg Latency,Max Latency,Error\n')
        
        # Data rows
        for r in results:
            f.write(f"{r['target']},{r['timestamp']},{r['success']},")
            f.write(f"{r['packets_sent']},{r['packets_received']},")
            f.write(f"{r['packet_loss']},{r['min_latency'] or 'N/A'},")
            f.write(f"{r['avg_latency'] or 'N/A'},{r['max_latency'] or 'N/A'},")
            f.write(f"{r['error'] or 'None'}\n")
    
    print(f"Reporte CSV guardado en: {output_file}")


def main():
    """Función principal."""
    args = parse_arguments()
    
    # Determinar lista de targets
    targets = []
    if args.target:
        targets = [args.target]
    elif args.targets_file:
        targets = load_targets_from_file(args.targets_file)
    else:
        # Targets por defecto para demostración
        targets = ['8.8.8.8', '1.1.1.1', 'google.com']
    
    print(f"=== Network Latency Check ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Targets: {len(targets)}")
    print(f"Packets per target: {args.count}")
    print("=" * 40)
    
    # Ejecutar tests de latencia
    results = []
    for i, target in enumerate(targets, 1):
        print(f"\n[{i}/{len(targets)}] Checking {target}...")
        result = check_ping(target, args.count)
        results.append(result)
        
        # Mostrar resultado inmediato
        status = "✓ OK" if result['success'] else "✗ FAIL"
        print(f"  Status: {status}")
        if result['success']:
            print(f"  Packet Loss: {result['packet_loss']}%")
            if result['avg_latency']:
                print(f"  Avg Latency: {result['avg_latency']} ms")
        if result['error']:
            print(f"  Error: {result['error']}")
    
    # Resumen final
    print("\n" + "=" * 40)
    print("=== SUMMARY ===")
    successful = sum(1 for r in results if r['success'])
    print(f"Successful: {successful}/{len(results)}")
    
    if successful > 0:
        avg_latencies = [r['avg_latency'] for r in results if r['avg_latency']]
        if avg_latencies:
            overall_avg = sum(avg_latencies) / len(avg_latencies)
            print(f"Overall Average Latency: {overall_avg:.2f} ms")
    
    # Salida según formato solicitado
    if args.json:
        print("\n" + "=" * 40)
        print(json.dumps(results, indent=2))
    
    if args.output:
        generate_csv_report(results, args.output)
    
    # Retornar código de salida apropiado
    sys.exit(0 if successful == len(results) else 1)


if __name__ == '__main__':
    main()
