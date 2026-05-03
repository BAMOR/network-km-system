#!/bin/bash
#===============================================================================
# Script: backup_configs.sh
# Propósito: Realizar respaldo automático de configuraciones de dispositivos de red
# Autor: Departamento de TI - Banco Tecnológico
# Versión: 1.0
# Fecha: 2024-01-15
# Dependencias: sshpass, openssh-client, git, mailx
# Uso: ./backup_configs.sh
# Cron: 0 2 * * * /opt/banco/scripts/backup_configs.sh
#===============================================================================

#-------------------------------------------------------------------------------
# CONFIGURACIÓN GLOBAL
#-------------------------------------------------------------------------------

# Directorios
BACKUP_BASE="/backup/router-configs"
LOG_FILE="/var/log/backup_configs.log"
INVENTORY_FILE="/opt/banco/inventory/devices.txt"
CREDENTIALS_FILE="/opt/banco/vault/credentials.enc"
GIT_REPO="/backup/router-configs-git"

# Configuración de correo
EMAIL_TO="network-team@banco.local"
EMAIL_FROM="backup-system@banco.local"
SMTP_SERVER="smtp.banco.local"

# Umbrales
MAX_BACKUP_TIME=1800  # 30 minutos en segundos
MIN_CONFIG_LINES=50   # Mínimo líneas esperadas en configuración

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

#-------------------------------------------------------------------------------
# FUNCIONES
#-------------------------------------------------------------------------------

log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${LOG_FILE}"
}

log_info() {
    log_message "INFO" "$1"
}

log_error() {
    log_message "${RED}ERROR${NC}" "$1"
}

log_success() {
    log_message "${GREEN}SUCCESS${NC}" "$1"
}

log_warning() {
    log_message "${YELLOW}WARNING${NC}" "$1"
}

# Verificar prerequisitos
check_prerequisites() {
    log_info "Verificando prerequisitos..."
    
    local missing_deps=()
    
    # Verificar comandos necesarios
    for cmd in sshpass ssh git md5sum mail; do
        if ! command -v $cmd &> /dev/null; then
            missing_deps+=($cmd)
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Faltan dependencias: ${missing_deps[*]}"
        exit 1
    fi
    
    # Verificar directorios
    if [ ! -d "${BACKUP_BASE}" ]; then
        log_info "Creando directorio base: ${BACKUP_BASE}"
        mkdir -p "${BACKUP_BASE}"
    fi
    
    if [ ! -f "${INVENTORY_FILE}" ]; then
        log_error "Archivo de inventario no encontrado: ${INVENTORY_FILE}"
        exit 1
    fi
    
    if [ ! -f "${CREDENTIALS_FILE}" ]; then
        log_error "Archivo de credenciales no encontrado: ${CREDENTIALS_FILE}"
        exit 1
    fi
    
    log_success "Prerequisitos verificados"
}

# Cargar inventario de dispositivos
load_inventory() {
    log_info "Cargando inventario de dispositivos..."
    
    declare -g -a DEVICES
    local index=0
    
    while IFS='|' read -r hostname ip device_type location; do
        # Saltar comentarios y líneas vacías
        [[ "${hostname}" =~ ^#.*$ ]] && continue
        [[ -z "${hostname}" ]] && continue
        
        DEVICES[$index]="${hostname}|${ip}|${device_type}|${location}"
        ((index++))
        
        log_info "Dispositivo cargado: ${hostname} (${ip})"
    done < "${INVENTORY_FILE}"
    
    log_success "Inventario cargado: ${#DEVICES[@]} dispositivos"
}

# Realizar backup de un dispositivo
backup_device() {
    local hostname=$1
    local ip=$2
    local device_type=$3
    local location=$4
    
    local start_time=$(date +%s)
    local backup_dir="${BACKUP_BASE}/${hostname}/$(date +%Y)/$(date +%m)"
    local backup_file="${backup_dir}/${hostname}-$(date +%Y%m%d-%H%M%S).cfg"
    local latest_link="${BACKUP_BASE}/${hostname}/latest.cfg"
    
    # Crear directorio de backup
    mkdir -p "${backup_dir}"
    
    log_info "Iniciando backup de ${hostname} (${ip})"
    
    # Obtener credenciales (desencriptar si es necesario)
    local username=$(decrypt_credential "${hostname}" "username")
    local password=$(decrypt_credential "${hostname}" "password")
    
    # Ejecutar backup según tipo de dispositivo
    local config=""
    case "${device_type}" in
        "cisco_ios"|"cisco_nxos")
            config=$(sshpass -p "${password}" ssh -o StrictHostKeyChecking=no \
                    -o ConnectTimeout=10 \
                    ${username}@${ip} "show running-config" 2>&1)
            ;;
        "cisco_asa")
            config=$(sshpass -p "${password}" ssh -o StrictHostKeyChecking=no \
                    -o ConnectTimeout=10 \
                    ${username}@${ip} "show running-config all" 2>&1)
            ;;
        "hp_procurve"|"aruba")
            config=$(sshpass -p "${password}" ssh -o StrictHostKeyChecking=no \
                    -o ConnectTimeout=10 \
                    ${username}@${ip} "show running-config" 2>&1)
            ;;
        "paloalto")
            config=$(sshpass -p "${password}" ssh -o StrictHostKeyChecking=no \
                    -o ConnectTimeout=10 \
                    ${username}@${ip} "show configuration" 2>&1)
            ;;
        *)
            log_warning "Tipo de dispositivo desconocido: ${device_type}. Usando comando genérico."
            config=$(sshpass -p "${password}" ssh -o StrictHostKeyChecking=no \
                    -o ConnectTimeout=10 \
                    ${username}@${ip} "show running-config" 2>&1)
            ;;
    esac
    
    local ssh_exit_code=$?
    
    # Verificar resultado
    if [ ${ssh_exit_code} -ne 0 ]; then
        log_error "Falló conexión SSH a ${hostname}: código ${ssh_exit_code}"
        return 1
    fi
    
    # Verificar que la configuración no esté vacía
    if [ -z "${config}" ]; then
        log_error "Configuración vacía para ${hostname}"
        return 1
    fi
    
    # Guardar configuración
    echo "${config}" > "${backup_file}"
    
    # Verificar tamaño mínimo
    local line_count=$(wc -l < "${backup_file}")
    if [ ${line_count} -lt ${MIN_CONFIG_LINES} ]; then
        log_warning "Configuración pequeña para ${hostname}: ${line_count} líneas"
    fi
    
    # Calcular hash MD5
    md5sum "${backup_file}" > "${backup_file}.md5"
    
    # Actualizar enlace latest
    ln -sf "${backup_file}" "${latest_link}"
    
    # Calcular tiempo transcurrido
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Verificar tiempo de backup
    if [ ${duration} -gt ${MAX_BACKUP_TIME} ]; then
        log_warning "Backup lento para ${hostname}: ${duration} segundos"
    fi
    
    log_success "Backup completado para ${hostname} en ${duration}s (${line_count} líneas)"
    
    # Retornar información para estadísticas
    echo "${hostname}|${duration}|${line_count}|success"
    return 0
}

# Desencriptar credenciales (implementación simplificada)
decrypt_credential() {
    local hostname=$1
    local cred_type=$2
    
    # En producción, usar OpenSSL o vault real
    # Esto es solo un ejemplo
    if [ "${cred_type}" == "username" ]; then
        echo "admin"
    elif [ "${cred_type}" == "password" ]; then
        echo "secure_password_from_vault"
    fi
}

# Commit a repositorio Git
git_commit_backup() {
    log_info "Actualizando repositorio Git..."
    
    cd "${GIT_REPO}" || return 1
    
    # Copiar nuevos backups al repo git
    cp -r "${BACKUP_BASE}"/* "${GIT_REPO}/" 2>/dev/null
    
    git add -A
    git diff --cached --quiet && return 0
    
    git commit -m "Backup automático $(date +%Y-%m-%d)"
    git push origin main 2>/dev/null || log_warning "Falló push a Git"
    
    log_success "Repositorio Git actualizado"
}

# Generar reporte y enviar por correo
send_report() {
    local success_count=$1
    local fail_count=$2
    local total_devices=$3
    
    local subject="[BACKUP] Reporte Diario - $(date +%Y-%m-%d)"
    local body_file=$(mktemp)
    
    cat > "${body_file}" << EOF
=============================================================
REPORTE DIARIO DE BACKUP - BANCO TECNOLÓGICO
Fecha: $(date '+%Y-%m-%d %H:%M:%S')
=============================================================

RESUMEN:
--------
Total de dispositivos: ${total_devices}
Backups exitosos: ${success_count}
Backups fallidos: ${fail_count}
Tasa de éxito: $(echo "scale=2; ${success_count}*100/${total_devices}" | bc)%

DETALLE DE DISPOSITIVOS:
------------------------
$(cat /tmp/backup_details_$$)

ESTADÍSTICAS:
-------------
Tiempo promedio de backup: $(echo "scale=2; ${TOTAL_TIME}/${success_count}" | bc) segundos
Tamaño promedio de config: $(echo "scale=0; ${TOTAL_LINES}/${success_count}" | bc) líneas

ESPACIO EN DISCO:
-----------------
$(df -h ${BACKUP_BASE} | tail -1)

PRÓXIMO BACKUP PROGRAMADO:
--------------------------
Mañana a las 02:00 AM

=============================================================
Sistema Automático de Backups - Banco Tecnológico
=============================================================
EOF

    # Enviar correo
    mail -s "${subject}" -r "${EMAIL_FROM}" "${EMAIL_TO}" < "${body_file}"
    
    rm -f "${body_file}"
    
    log_info "Reporte enviado por correo a ${EMAIL_TO}"
}

#-------------------------------------------------------------------------------
# PROGRAMA PRINCIPAL
#-------------------------------------------------------------------------------

main() {
    log_info "=========================================="
    log_info "Iniciando proceso de backup automático"
    log_info "=========================================="
    
    # Inicializar contadores
    local success_count=0
    local fail_count=0
    local total_devices=0
    TOTAL_TIME=0
    TOTAL_LINES=0
    
    # Verificar prerequisitos
    check_prerequisites
    
    # Cargar inventario
    load_inventory
    
    total_devices=${#DEVICES[@]}
    
    # Procesar cada dispositivo
    for device in "${DEVICES[@]}"; do
        IFS='|' read -r hostname ip device_type location <<< "${device}"
        
        result=$(backup_device "${hostname}" "${ip}" "${device_type}" "${location}")
        exit_code=$?
        
        # Guardar detalle para reporte
        echo "${result}" >> /tmp/backup_details_$$
        
        if [ ${exit_code} -eq 0 ]; then
            ((success_count++))
            
            # Extraer estadísticas del resultado
            IFS='|' read -r _ duration lines _ <<< "${result}"
            TOTAL_TIME=$((TOTAL_TIME + duration))
            TOTAL_LINES=$((TOTAL_LINES + lines))
        else
            ((fail_count++))
        fi
    done
    
    # Actualizar repositorio Git
    git_commit_backup
    
    # Enviar reporte
    send_report ${success_count} ${fail_count} ${total_devices}
    
    # Limpieza
    rm -f /tmp/backup_details_$$
    
    log_info "=========================================="
    log_info "Proceso de backup finalizado"
    log_info "Exitosos: ${success_count} | Fallidos: ${fail_count}"
    log_info "=========================================="
    
    # Retornar código de salida apropiado
    if [ ${fail_count} -gt 0 ]; then
        exit 1
    fi
    exit 0
}

# Ejecutar programa principal
main "$@"
