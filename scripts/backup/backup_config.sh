#!/bin/bash
#===============================================================================
# Script: backup_config.sh
# Autor: Equipo de Redes
# Propósito: Realizar backup automático de configuraciones de dispositivos de red
# Dependencias:
#     - Bash 4.0+
#     - sshpass (para autenticación SSH con contraseña)
#     - grep, sed (procesamiento de texto)
# Ejemplo de Uso:
#     ./backup_config.sh -h 192.168.1.1 -u admin -p password -d cisco
#     ./backup_config.sh -f devices.txt -o /backup/network/
#===============================================================================

set -euo pipefail

# Configuración por defecto
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE_STAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${BACKUP_DIR}/backup_${DATE_STAMP}.log"
MAX_BACKUPS=30

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

#-------------------------------------------------------------------------------
# Funciones de Logging
#-------------------------------------------------------------------------------
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

#-------------------------------------------------------------------------------
# Función de Ayuda
#-------------------------------------------------------------------------------
show_help() {
    cat << EOF
Uso: $0 [OPCIONES]

Opciones:
    -h, --host IP          Dirección IP o hostname del dispositivo
    -u, --user USER        Usuario para autenticación
    -p, --password PASS    Contraseña (o usar variable de entorno SSH_PASS)
    -d, --device TYPE      Tipo de dispositivo: cisco, juniper, hp, fortinet
    -f, --file FILE        Archivo con lista de dispositivos (formato: ip,user,pass,type)
    -o, --output DIR       Directorio de salida para backups
    -n, --dry-run          Modo simulación (no ejecuta comandos)
    --help                 Mostrar esta ayuda

Ejemplos:
    $0 -h 192.168.1.1 -u admin -p secret -d cisco
    $0 -f devices.txt -o /var/backups/network/
    $0 -h switch.local -u admin --device juniper

Formato del archivo devices.txt:
    192.168.1.1,admin,password,cisco
    192.168.1.2,root,secret,juniper
    # Los comentarios comienzan con #

EOF
}

#-------------------------------------------------------------------------------
# Función de Backup por Tipo de Dispositivo
#-------------------------------------------------------------------------------
backup_cisco() {
    local host=$1
    local user=$2
    local pass=$3
    local output_file=$4
    
    log_info "Iniciando backup Cisco: $host"
    
    sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
        "${user}@${host}" << 'EOSH' > "$output_file" 2>&1
enable
terminal length 0
show running-config
exit
EOSH
    
    if [ $? -eq 0 ]; then
        log_info "Backup completado: $output_file"
        return 0
    else
        log_error "Falló backup de $host"
        return 1
    fi
}

backup_juniper() {
    local host=$1
    local user=$2
    local pass=$3
    local output_file=$4
    
    log_info "Iniciando backup Juniper: $host"
    
    sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
        "${user}@${host}" << 'EOSH' > "$output_file" 2>&1
show configuration | display set
exit
EOSH
    
    if [ $? -eq 0 ]; then
        log_info "Backup completado: $output_file"
        return 0
    else
        log_error "Falló backup de $host"
        return 1
    fi
}

backup_hp() {
    local host=$1
    local user=$2
    local pass=$3
    local output_file=$4
    
    log_info "Iniciando backup HP/Aruba: $host"
    
    sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
        "${user}@${host}" << 'EOSH' > "$output_file" 2>&1
display current-configuration
exit
EOSH
    
    if [ $? -eq 0 ]; then
        log_info "Backup completado: $output_file"
        return 0
    else
        log_error "Falló backup de $host"
        return 1
    fi
}

backup_fortinet() {
    local host=$1
    local user=$2
    local pass=$3
    local output_file=$4
    
    log_info "Iniciando backup Fortinet: $host"
    
    sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
        "${user}@${host}" << 'EOSH' > "$output_file" 2>&1
show full-configuration
exit
EOSH
    
    if [ $? -eq 0 ]; then
        log_info "Backup completado: $output_file"
        return 0
    else
        log_error "Falló backup de $host"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# Función Principal de Backup
#-------------------------------------------------------------------------------
perform_backup() {
    local host=$1
    local user=$2
    local pass=$3
    local device_type=$4
    local dry_run=${5:-false}
    
    # Crear nombre de archivo único
    local filename="${host}_${DATE_STAMP}.cfg"
    local output_file="${BACKUP_DIR}/${filename}"
    
    if [ "$dry_run" = true ]; then
        log_info "[DRY-RUN] Backup de $host ($device_type) -> $output_file"
        return 0
    fi
    
    # Seleccionar función según tipo de dispositivo
    case "$device_type" in
        cisco|cisconxos)
            backup_cisco "$host" "$user" "$pass" "$output_file"
            ;;
        juniper|junos)
            backup_juniper "$host" "$user" "$pass" "$output_file"
            ;;
        hp|hpe|aruba)
            backup_hp "$host" "$user" "$pass" "$output_file"
            ;;
        fortinet|fortigate)
            backup_fortinet "$host" "$user" "$pass" "$output_file"
            ;;
        *)
            log_error "Tipo de dispositivo desconocido: $device_type"
            return 1
            ;;
    esac
}

#-------------------------------------------------------------------------------
# Limpieza de Backups Antiguos
#-------------------------------------------------------------------------------
cleanup_old_backups() {
    log_info "Limpiando backups antiguos (manteniendo últimos $MAX_BACKUPS)"
    
    # Contar y eliminar backups excedentes por host
    for backup_file in "${BACKUP_DIR}"/*.cfg; do
        [ -e "$backup_file" ] || continue
        
        # Extraer hostname del filename
        local hostname=$(basename "$backup_file" | cut -d'_' -f1)
        
        # Contar backups de este host
        local count=$(ls -1 "${BACKUP_DIR}/${hostname}"_*.cfg 2>/dev/null | wc -l)
        
        if [ "$count" -gt "$MAX_BACKUPS" ]; then
            # Eliminar los más antiguos
            local to_delete=$((count - MAX_BACKUPS))
            ls -1t "${BACKUP_DIR}/${hostname}"_*.cfg | tail -n "$to_delete" | xargs rm -f
            log_info "Eliminados $to_delete backups antiguos de $hostname"
        fi
    done
}

#-------------------------------------------------------------------------------
# Programa Principal
#-------------------------------------------------------------------------------
main() {
    local host=""
    local user=""
    local password=""
    local device_type="cisco"
    local devices_file=""
    local dry_run=false
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--host)
                host="$2"
                shift 2
                ;;
            -u|--user)
                user="$2"
                shift 2
                ;;
            -p|--password)
                password="$2"
                shift 2
                ;;
            -d|--device)
                device_type="$2"
                shift 2
                ;;
            -f|--file)
                devices_file="$2"
                shift 2
                ;;
            -o|--output)
                BACKUP_DIR="$2"
                shift 2
                ;;
            -n|--dry-run)
                dry_run=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Opción desconocida: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Crear directorio de backup si no existe
    mkdir -p "$BACKUP_DIR"
    touch "$LOG_FILE"
    
    log_info "=== Network Config Backup Started ==="
    log_info "Backup Directory: $BACKUP_DIR"
    
    # Procesar backup único o múltiple
    if [ -n "$devices_file" ]; then
        # Backup múltiple desde archivo
        if [ ! -f "$devices_file" ]; then
            log_error "Archivo de dispositivos no encontrado: $devices_file"
            exit 1
        fi
        
        local success_count=0
        local fail_count=0
        
        while IFS=',' read -r h u p t || [ -n "$h" ]; do
            # Saltar comentarios y líneas vacías
            [[ "$h" =~ ^#.*$ ]] && continue
            [ -z "$h" ] && continue
            
            # Usar valores por defecto si no se especifican
            [ -z "$t" ] && t="cisco"
            
            if perform_backup "$h" "$u" "$p" "$t" "$dry_run"; then
                ((success_count++))
            else
                ((fail_count++))
            fi
        done < "$devices_file"
        
        log_info "=== Backup Summary ==="
        log_info "Exitosos: $success_count"
        log_info "Fallidos: $fail_count"
        
    elif [ -n "$host" ]; then
        # Backup único
        if [ -z "$user" ]; then
            log_error "Usuario requerido para backup único"
            exit 1
        fi
        
        if [ -z "$password" ]; then
            password="${SSH_PASS:-}"
            if [ -z "$password" ]; then
                log_error "Contraseña requerida (usar -p o variable SSH_PASS)"
                exit 1
            fi
        fi
        
        perform_backup "$host" "$user" "$password" "$device_type" "$dry_run"
    else
        log_error "Debe especificar -h/--host o -f/--file"
        show_help
        exit 1
    fi
    
    # Limpieza de backups antiguos
    if [ "$dry_run" = false ]; then
        cleanup_old_backups
    fi
    
    log_info "=== Network Config Backup Completed ==="
}

# Ejecutar programa principal
main "$@"
