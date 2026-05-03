# 📊 Incidente INC-001 - Caída de Enlace MPLS Sucursal Mixco

## Información General del Incidente

| Campo | Valor |
|-------|-------|
| **ID Incidente** | INC-001 |
| **Fecha** | 2024-01-10 |
| **Hora Inicio** | 14:35 |
| **Hora Resolución** | 16:03 |
| **Duración Total** | 1 hora 28 minutos |
| **Severidad** | 🔴 Crítica |
| **Sucursal Afectada** | Mixco |
| **Servicios Impactados** | Conexión a datacenter, transacciones en línea |

---

## 📝 Descripción del Incidente

La sucursal Mixco perdió completamente la conectividad con el datacenter central debido a un corte de fibra óptica del proveedor principal (Telefónica). El enlace afectado era el MPLS primario de 100 Mbps que proporciona conectividad a todas las aplicaciones core del banco.

### Impacto Operacional

- **Cajeros automáticos**: Operando en modo offline (transacciones almacenadas localmente)
- **Ventanilla**: Sin acceso a sistema core, solo consultas de saldo
- **Aplicaciones web**: Inaccesibles desde la sucursal
- **Usuarios afectados**: ~45 empleados + 8 cajeros automáticos

---

## 🔍 Cronología del Incidente

| Hora | Evento | Responsable |
|------|--------|-------------|
| 14:35 | Alerta automática de monitoreo - enlace MPLS abajo | Sistema Monitoreo |
| 14:37 | Help Desk recibe llamadas de sucursal Mixco | Help Desk |
| 14:40 | Admin Red Junior inicia diagnóstico inicial | Juan Pérez |
| 14:45 | Confirmado: interface GigabitEthernet0/0 down en router Mixco | Juan Pérez |
| 14:47 | Verificado: enlace secundario 4G activado automáticamente | Juan Pérez |
| 14:50 | Sucursal reporta recuperación parcial de servicios | Juan Pérez |
| 14:55 | Ticket abierto con Telefónica (Case #TEL-2024-00123) | Carlos Ramírez |
| 15:10 | Telefónica confirma corte de fibra por trabajos externos | Telefónica |
| 15:15 | ETA proporcionado: 1 hora para reparación | Telefónica |
| 15:20 | Comunicación enviada a gerencia de sucursal | Carlos Ramírez |
| 15:45 | Técnico de Telefónica llega al sitio | Telefónica |
| 15:55 | Reparación completada, enlace MPLS restaurado | Telefónica |
| 16:00 | Verificación completa de conectividad y servicios | Ana López |
| 16:03 | Incidente cerrado, monitoreo continuado | Ana López |

---

## 🔧 Diagnóstico Aplicado

Siguiendo el árbol de diagnóstico de [`perdida-conectividad.md`](../docs/troubleshooting/perdida-conectividad.md#nivel-3-una-sucursal-completa):

### Paso 1: Verificar enlaces WAN
```bash
# Desde router core
show interfaces GigabitEthernet0/0
# Resultado: line protocol is down

show interfaces GigabitEthernet0/1
# Resultado: line protocol is up (4G activo)
```

### Paso 2: Verificar enrutamiento
```bash
show ip route 10.12.0.0/16
# Ruta ahora usa interfaz 4G (ruta flotante activa)

show ip ospf neighbor
# Vecino OSPF de Mixco alcanzable vía 4G
```

### Paso 3: Activar respaldo (automático en este caso)
```bash
# El failover ocurrió automáticamente gracias a:
# - Rutas estáticas flotantes configuradas
# - OSPF detectó pérdida de vecindad
# - Tráfico se redirigió vía 4G sin intervención manual
```

---

## ✅ Acciones Tomadas

### Inmediatas (0-15 minutos)

1. ✅ Verificación de alertas de monitoreo
2. ✅ Confirmación de failover automático a 4G
3. ✅ Validación de servicios críticos restaurados
4. ✅ Comunicación inicial a stakeholders

### Durante el Incidente (15-60 minutos)

5. ✅ Apertura de ticket con proveedor ISP
6. ✅ Monitoreo continuo de calidad de enlace 4G
7. ✅ Comunicación de ETA a sucursal
8. ✅ Preparación de plan B (enlace satelital) si era necesario

### Post-Resolución (60+ minutos)

9. ✅ Verificación completa de todos los servicios
10. ✅ Validación de retorno a enlace primario
11. ✅ Cierre formal con proveedor
12. ✅ Documentación de lecciones aprendidas

---

## 📈 Métricas del Incidente

### Tiempo de Respuesta

| Métrica | Objetivo | Real | Estado |
|---------|----------|------|--------|
| Detección | < 5 min | 2 min | ✅ |
| Respuesta Inicial | < 10 min | 5 min | ✅ |
| Activación Respaldo | < 5 min | 2 min (auto) | ✅ |
| Resolución Total | < 2 horas | 1h 28min | ✅ |

### Calidad de Servicio Durante Incidente

| Métrica | Enlace Primario | Enlace Respaldo |
|---------|-----------------|-----------------|
| Ancho de Banda | 100 Mbps | 50 Mbps |
| Latencia Promedio | 25 ms | 45 ms |
| Pérdida de Paquetes | 100% (caído) | 0.1% |
| Jitter | N/A | 8 ms |

---

## 🎯 Lecciones Aprendidas

### ✅ Lo Que Funcionó Bien

1. **Failover Automático**: El sistema de rutas flotantes funcionó perfectamente, activando el 4G en menos de 30 segundos sin intervención manual.

2. **Monitoreo Proactivo**: Las alertas automáticas permitieron iniciar diagnóstico antes de que usuarios reportaran masivamente.

3. **Documentación Disponible**: El procedimiento de troubleshooting guió eficientemente al equipo junior.

4. **Comunicación Efectiva**: Stakeholders recibieron actualizaciones cada 15-20 minutos.

### ⚠️ Áreas de Mejora Identificadas

1. **Capacitación en Activación Manual**: No todo el equipo de turno conocía el procedimiento completo de activación manual del 4G por si el automático fallaba.

   **Acción Correctiva**: Agendar capacitación práctica para todo el equipo en las próximas 2 semanas.

2. **Ancho de Banda Insuficiente en Respaldo**: El enlace 4G de 50 Mbps fue suficiente para operaciones básicas pero causó lentitud en algunas aplicaciones.

   **Acción Correctiva**: Evaluar upgrade a plan 4G de 100 Mbps o agregar segundo enlace de respaldo.

3. **Visibilidad de Calidad de Enlace 4G**: No había dashboard específico para monitorear métricas detalladas del enlace de respaldo.

   **Acción Correctiva**: Implementar gráficos de latencia/pérdida específicos para enlaces de respaldo en el sistema de monitoreo.

---

## 🔗 Cambios Resultantes

### Documentación Actualizada

- [x] Procedimiento de activación manual de 4G agregado a `gestion-vlans.md`
- [x] Nuevos umbrales de alerta para enlaces de respaldo en `monitor_enlaces.py`
- [x] Esta lección aprendida agregada a la wiki

### Configuraciones Modificadas

```bash
# Se ajustó el threshold para alertas de enlace 4G
# Antes: alerta si latencia > 100ms
# Ahora: alerta si latencia > 60ms (más sensible para respaldo)

# Se agregó monitoreo de utilización de enlace 4G
# Alerta si utilización > 70% por más de 5 minutos
```

### Capacitaciones Programadas

| Tema | Fecha | Participantes | Estado |
|------|-------|---------------|--------|
| Activación Manual de Respaldo | 2024-01-25 | Todo el equipo | Programado |
| Troubleshooting de Enlaces WAN | 2024-02-01 | Admins Junior | Programado |

---

## 📞 Proveedores Involucrados

### Telefónica (ISP Principal)

- **Número de Caso**: TEL-2024-00123
- **Técnico Asignado**: Roberto Gómez
- **Tiempo Respuesta**: 1 hora 10 minutos
- **Causa Raíz**: Corte de fibra por trabajos de construcción externos
- **Acción Preventiva**: Telefónica instalará señalización adicional en zona de trabajos

### Claro (ISP Respaldo 4G)

- **Desempeño**: Satisfactorio
- **Incidencias**: Ninguna
- **Nota**: El enlace de respaldo funcionó como esperado durante toda la duración del incidente

---

## 📋 Checklist de Cierre

- [x] Servicios restaurados completamente
- [x] Verificación de conectividad punto a punto
- [x] Pruebas de aplicaciones críticas realizadas
- [x] Comunicación de cierre enviada a stakeholders
- [x] Ticket con proveedor cerrado
- [x] Documentación actualizada
- [x] Lecciones aprendidas registradas
- [x] Reunión post-incidente agendada (2024-01-12)

---

## 🔗 Referencias

- Procedimiento aplicado: [`/docs/troubleshooting/perdida-conectividad.md`](../docs/troubleshooting/perdida-conectividad.md)
- Matriz de escalamiento: [`/wiki/Contactos-y-Escalamiento.md`](../wiki/Contactos-y-Escalamiento.md)
- Script de monitoreo: [`/docs/scripts/monitor_enlaces.py`](../docs/scripts/monitor_enlaces.py)

---

**🏦 Banco Tecnológico - Departamento de TI**  
*Incidente cerrado y documentado*  
*Próxima revisión: 2024-07-10 (6 meses)*
