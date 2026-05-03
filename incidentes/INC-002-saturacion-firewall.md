# 📊 Incidente INC-002 - Saturación del Firewall Perimetral

## Información General del Incidente

| Campo | Valor |
|-------|-------|
| **ID Incidente** | INC-002 |
| **Fecha** | 2024-01-12 |
| **Hora Inicio** | 09:15 |
| **Hora Resolución** | 10:47 |
| **Duración Total** | 1 hora 32 minutos |
| **Severidad** | 🟠 Alta |
| **Sistema Afectado** | Firewall Perimetral Palo Alto PA-5220 |
| **Servicios Impactados** | Acceso a internet, aplicaciones cloud |

---

## 📝 Descripción del Incidente

El firewall perimetral principal (Palo Alto PA-5220) presentó saturación de CPU (95%) y número elevado de sesiones concurrentes (1.2M / 1.5M máx) debido a un ataque de Denegación de Servicio (DDoS) de baja intensidad originado desde una botnet distribuida. El ataque consistió en múltiples conexiones HTTP/HTTPS simultáneas hacia el portal de banca en línea.

### Impacto Operacional

- **Portal Banca en Línea**: Lentitud significativa, timeouts intermitentes
- **Navegación Web**: Experiencia degradada para usuarios internos
- **Aplicaciones Cloud**: Latencia elevada en acceso a SaaS
- **Correo Electrónico**: Retrasos en entrega/recepción
- **Usuarios afectados**: ~200 usuarios internos + clientes externos de banca en línea

---

## 🔍 Cronología del Incidente

| Hora | Evento | Responsable |
|------|--------|-------------|
| 09:15 | Alerta automática: CPU firewall > 90% | Sistema Monitoreo |
| 09:17 | Segunda alerta: Sesiones > 1M | Sistema Monitoreo |
| 09:18 | Help Desk reporta lentitud generalizada | Help Desk |
| 09:20 | Admin Red Junior inicia diagnóstico | María González |
| 09:23 | Identificado: Tráfico anómalo desde múltiples IPs externas | María González |
| 09:25 | Escalado a Admin Senior (posible DDoS) | María González |
| 09:27 | Admin Senior se une al incidente | Carlos Ramírez |
| 09:30 | Revisada guía de latencia-alta.md aplicada a firewall | Carlos Ramírez |
| 09:32 | Confirmado: Patrón de ataque DDoS Layer 7 | Carlos Ramírez |
| 09:35 | Activadas políticas anti-DDoS preconfiguradas | Carlos Ramírez |
| 09:40 | CPU comienza a descender (85%) | Sistema |
| 09:45 | Contactado equipo de Seguridad Informática | Carlos Ramírez |
| 09:50 | Implementadas reglas adicionales de rate limiting | Ana López |
| 09:55 | CPU estabilizada en 65% | Sistema |
| 10:00 | Sesiones activas descendiendo (800K) | Sistema |
| 10:10 | Usuarios reportan mejora significativa | Help Desk |
| 10:20 | Verificación completa de servicios | Ana López |
| 10:30 | Tráfico malicioso mitigado completamente | Sistema |
| 10:40 | Monitoreo continuo por 10 minutos | Equipo |
| 10:47 | Incidente cerrado oficialmente | Carlos Ramírez |

---

## 🔧 Diagnóstico Aplicado

Siguiendo la guía de [`latencia-alta.md`](../docs/troubleshooting/latencia-alta.md) adaptada para firewall:

### Paso 1: Verificar Recursos del Firewall

```bash
# Desde CLI del Palo Alto
show system resources

# Output observado:
# CPU: 95% (normal < 60%)
# Memory: 78% (normal < 70%)
# Session Count: 1,234,567 / 1,500,000

show session info

# Mostrar sesiones top por origen
show session all filter source <ip-sospechosa>
```

### Paso 2: Identificar Tráfico Anómalo

```bash
# Top talkers de sesión
show session top-n source-ip 10

# Resultado: Múltiples IPs externas con 500+ sesiones cada una
# Patrón: Conexiones HTTP/HTTPS repetitivas mismo destino

# Verificar logs de amenaza
show log threat direction equal incoming

# Detectado: Multiple HTTP flood desde botnet conocida
```

### Paso 3: Analizar Tráfico en Tiempo Real

```bash
# Captura de tráfico para análisis
debug dataplane packet-diag set capture on
debug dataplane packet-diag capture file http-flood.pcap

# Análisis mostró:
# - Peticiones HTTP GET repetitivas
# - User-Agent genérico o vacío
# - Mismo URL objetivo: /banca-en-linea/login
```

---

## ✅ Acciones Tomadas

### Inmediatas (0-15 minutos)

1. ✅ Verificación de alertas y métricas del firewall
2. ✅ Identificación de patrón de ataque DDoS
3. ✅ Escalamiento inmediato a senior y seguridad
4. ✅ Activación de políticas anti-DDoS existentes

### Durante el Incidente (15-60 minutos)

5. ✅ Implementación de rate limiting adicional
6. ✅ Bloqueo de rangos de IP identificados como maliciosos
7. ✅ Habilitación de GeoIP blocking para países no relevantes
8. ✅ Comunicación a stakeholders sobre degradación

### Post-Resolución (60+ minutos)

9. ✅ Verificación completa de servicios restaurados
10. ✅ Monitoreo continuo por posible rebrote
11. ✅ Recolección de evidencia para análisis forense
12. ✅ Documentación completa del incidente

---

## 🛡️ Configuraciones de Mitigación Aplicadas

### 1. Rate Limiting por IP Origen

```bash
# Crear objeto de protección DDoS
set deviceconfig setting resource session-aggressiveness aggressive

# Policy de rate limiting
set rules security DDoS-Protection source any destination any \
    application web-browsing service application-default \
    action allow profile-setting profiles \
    vulnerability-protection "DDoS-Mitigation"

# Profile específico
set profiles vulnerability "DDoS-Mitigation" rules \
    "HTTP-Flood" severity high action drop \
    http-flood-threshold 100
```

### 2. GeoIP Blocking Temporal

```bash
# Bloquear tráfico de países donde no hay operaciones
set rules security GeoIP-Block source [CN RU KP IR] \
    destination any action deny log-start log-end
```

### 3. Zone Protection

```bash
# Habilitar protección de zona externa
set network zone-protection-profile "External-Zone-Protection" \
    flood tcp-syn red activate 10000 max 15000 \
    flood udp red activate 5000 max 8000 \
    flood icmp red activate 1000 max 2000
```

---

## 📈 Métricas del Incidente

### Tiempo de Respuesta

| Métrica | Objetivo | Real | Estado |
|---------|----------|------|--------|
| Detección | < 5 min | 2 min | ✅ |
| Diagnóstico | < 15 min | 12 min | ✅ |
| Mitigación Inicial | < 20 min | 20 min | ✅ |
| Resolución Total | < 2 horas | 1h 32min | ✅ |

### Recursos del Firewall Durante Incidente

| Métrica | Normal | Pico Incidente | Post-Mitigación |
|---------|--------|----------------|-----------------|
| CPU | 25-40% | 95% | 35% |
| Memoria | 55-65% | 78% | 60% |
| Sesiones Activas | 200-400K | 1.2M | 250K |
| Throughput | 500 Mbps | 1.8 Gbps | 600 Mbps |

### Efectividad de Contramedidas

| Acción | Tiempo Implementación | Reducción CPU |
|--------|----------------------|---------------|
| Políticas Anti-DDoS | 5 min | 95% → 85% |
| Rate Limiting | 10 min | 85% → 65% |
| GeoIP Blocking | 15 min | 65% → 45% |
| Combinación total | 25 min | 95% → 35% |

---

## 🎯 Lecciones Aprendidas

### ✅ Lo Que Funcionó Bien

1. **Detección Temprana**: El sistema de monitoreo alertó antes de que usuarios masivos reportaran problemas.

2. **Guía de Troubleshooting Disponible**: La existencia de `latencia-alta.md` permitió que dos miembros junior iniciaran el diagnóstico sin esperar al administrador senior, reduciendo el tiempo inicial de respuesta de unos 30 minutos estimados a **8 minutos reales**.

3. **Políticas Preconfiguradas**: Las reglas anti-DDoS ya existían pero no estaban activas; activarlas fue cuestión de minutos.

4. **Respuesta Coordinada**: La colaboración entre equipo de red y seguridad fue efectiva.

### ⚠️ Áreas de Mejora Identificadas

1. **Políticas Anti-DDoS No Activas**: Las reglas existían pero requerían activación manual.

   **Acción Correctiva**: Configurar activación automática basada en umbrales de CPU/sesiones.

2. **Visibilidad Limitada de Amenazas**: No había dashboard unificado de amenazas en tiempo real.

   **Acción Correctiva**: Implementar Panorama o SIEM para visualización centralizada.

3. **Capacitación en DDoS**: No todo el equipo estaba familiarizado con procedimientos específicos de mitigación DDoS.

   **Acción Correctiva**: Capacitación trimestral en respuesta a incidentes de seguridad.

4. **Ancho de Banda Saturado**: El enlace de internet llegó a 90% de utilización durante el pico.

   **Acción Correctiva**: Evaluar aumento de ancho de banda o implementación de scrubbing center.

---

## 🔗 Cambios Resultantes

### Documentación Actualizada

- [x] Sección específica de DDoS agregada a `latencia-alta.md`
- [x] Procedimiento de activación rápida anti-DDoS creado
- [x] Playbook de respuesta a incidentes de seguridad actualizado

### Configuraciones Modificadas

```bash
# Auto-activación de políticas anti-DDoS cuando:
# - CPU > 80% por 2 minutos consecutivos
# - O Sesiones > 1M
# - O Throughput > 80% del máximo

# Nuevas reglas permanentes:
# - Rate limiting base siempre activo
# - GeoIP blocking para 15 países de alto riesgo
# - TCP SYN flood protection activado
```

### Herramientas Adicionales

| Herramienta | Propósito | Estado |
|-------------|-----------|--------|
| Panorama | Gestión centralizada firewalls | En evaluación |
| AutoFocus | Threat intelligence Palo Alto | Contratado |
| Grafana Dashboard | Visualización métricas seguridad | En implementación |

---

## 📞 Proveedores Involucrados

### Palo Alto Networks

- **Caso TAC**: PAN-2024-00456
- **Ingeniero Asignado**: Jennifer Liu
- **Tiempo Respuesta**: 20 minutos
- **Recomendaciones**: 
  - Actualizar Threat Prevention a versión 8457
  - Considerar servicio WildFire para análisis sandbox
  - Implementar DNS Security

### ISP (Tigo Business)

- **Contacto**: Luis Hernández
- **Acción**: Proporcionado logging adicional de tráfico entrante
- **Recomendación**: Evaluar servicio DDoS Scrubbing del ISP

---

## 📋 Checklist de Cierre

- [x] Servicios restaurados completamente
- [x] CPU y sesiones en niveles normales
- [x] Políticas de mitigación activas y probadas
- [x] Evidencia recolectada para análisis forense
- [x] Comunicación de cierre enviada
- [x] Documentación actualizada
- [x] Lecciones aprendidas registradas
- [x] Reunión post-incidente completada (2024-01-15)
- [x] Plan de acción aprobado por gerencia

---

## 📊 ROI del Sistema de Gestión del Conocimiento

Este incidente demuestra concretamente el valor de la inversión en KM:

| Factor | Sin KM (Estimado) | Con KM (Real) | Ahorro |
|--------|------------------|---------------|--------|
| Tiempo diagnóstico inicial | 30 min | 8 min | 73% |
| Personal requerido | 3 seniors | 2 juniors + 1 senior | Menor costo |
| Estrés del equipo | Alto | Moderado | Mejor experiencia |
| Impacto operacional | 2+ horas | 1h 32min | 24% menos |

**Conclusión**: La documentación disponible permitió una respuesta **3.75 veces más rápida** en la fase crítica de diagnóstico.

---

## 🔗 Referencias

- Guía aplicada: [`/docs/troubleshooting/latencia-alta.md`](../docs/troubleshooting/latencia-alta.md)
- Matriz de escalamiento: [`/wiki/Contactos-y-Escalamiento.md`](../wiki/Contactos-y-Escalamiento.md)
- Script de monitoreo: [`/docs/scripts/monitor_enlaces.py`](../docs/scripts/monitor_enlaces.py)

---

**🏦 Banco Tecnológico - Departamento de TI**  
*Incidente cerrado y documentado*  
*Próxima revisión: 2024-07-12 (6 meses)*
