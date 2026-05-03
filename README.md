# 🏦 Sistema de Gestión del Conocimiento - Banco Tecnológico

## 📋 Propósito

Este repositorio implementa un sistema básico de gestión del conocimiento (KM) para transformar el conocimiento tácito del equipo de TI en conocimiento explícito, documentado y transferible. En el contexto bancario, donde una caída de servicio impacta directamente la operación y confianza de los clientes, contar con un KM robusto es una medida de **resiliencia organizacional**.

## 🎯 Objetivos

- Eliminar la dependencia operativa de una sola persona
- Documentar configuraciones críticas y procedimientos
- Reducir el tiempo medio de respuesta (MTTR) ante incidentes
- Establecer trazabilidad y control de versiones
- Facilitar la capacitación cruzada y onboarding

## 📁 Estructura del Repositorio

```
km-banco-tecnologico/
├── docs/
│   ├── procedimientos/      # Procedimientos críticos de red
│   ├── scripts/             # Scripts de automatización
│   └── troubleshooting/     # Guías de diagnóstico
├── wiki/                    # Wiki interna
│   ├── Home.md
│   ├── Glosario.md
│   └── Contactos-y-Escalamiento.md
├── incidentes/              # Bitácora de incidentes
│   ├── INC-001-caida-mpls.md
│   └── INC-002-saturacion-firewall.md
└── README.md                # Este archivo
```

## 🚀 Procedimientos Documentados

| Procedimiento | Descripción | Ubicación |
|--------------|-------------|-----------|
| Configuración Router Core | Puesta en marcha del equipo crítico | `docs/procedimientos/configuracion-router-core.md` |
| Respaldo de Configuraciones | Política diaria y manual de backups | `docs/procedimientos/respaldo-configuraciones.md` |
| Gestión de VLANs | Inventario y procedimiento de creación | `docs/procedimientos/gestion-vlans.md` |

## 🛠️ Scripts de Automatización

| Script | Lenguaje | Propósito |
|--------|----------|-----------|
| `backup_configs.sh` | Bash | Respaldo automático vía SSH |
| `monitor_enlaces.py` | Python | Monitoreo de latencia y pérdida |

## 📖 Wiki Interna

La carpeta `/wiki` contiene:

- **Home.md**: Punto de entrada y guía de onboarding
- **Glosario.md**: Términos técnicos del repositorio
- **Contactos-y-Escalamiento.md**: Matriz de escalamiento por niveles

## 📊 Incidentes Documentados

| Incidente | Descripción | Lecciones Aprendidas |
|-----------|-------------|---------------------|
| INC-001 | Caída de enlace MPLS - Sucursal Mixco | Activación de respaldo 4G LTE |
| INC-002 | Saturación firewall perimetral | DDoS de baja intensidad |

## 🔧 Convenciones del Repositorio

### Control de Versiones
- Cada commit debe incluir mensaje descriptivo
- Usar Pull Requests para cambios en documentación crítica
- Revisión por pares obligatoria antes de merge

### Formato Markdown
- Usar bloques de código con resaltado de sintaxis
- Incluir diagramas Mermaid cuando aplique
- Seguir estructura SOP en procedimientos

### Nomenclatura de Archivos
- Minúsculas con guiones: `nombre-archivo.md`
- Prefijo INC- para incidentes: `INC-001-descripcion.md`
- Fechas en formato ISO: `YYYY-MM-DD`

## 👥 Flujo de Trabajo

1. **Crear/Actualizar** documentación en rama feature
2. **Pull Request** con descripción del cambio
3. **Revisión** por otro miembro del equipo
4. **Merge** a main después de aprobación
5. **Notificar** al equipo sobre cambios críticos

## 📈 Beneficios Alcanzados

✅ Disponibilidad permanente del conocimiento 24/7  
✅ Reducción del MTTR en escenarios documentados  
✅ Trazabilidad total mediante historial de Git  
✅ Cultura de mejora continua  
✅ Disminución del riesgo por rotación de personal  

---

**🏦 Banco Tecnológico - Departamento de TI**  
*Documentación versionada y bajo control de cambios*
