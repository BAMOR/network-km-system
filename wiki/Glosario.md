# 📖 Glosario de Términos Técnicos

Este glosario contiene definiciones de los términos técnicos más utilizados en la documentación del Banco Tecnológico.

---

## A

### ACL (Access Control List)
Lista de control de acceso que define reglas para permitir o denegar tráfico de red según criterios como IP, puerto o protocolo.

### Administrative Distance (AD)
Valor numérico que determina la preferencia de una ruta cuando múltiples protocolos de enrutamiento proporcionan información sobre el mismo destino. Menor valor = mayor preferencia.

### Área OSPF
División lógica de una red OSPF que agrupa routers y enlaces para optimizar el intercambio de información de enrutamiento. El área 0 es el backbone obligatorio.

---

## B

### Backup Flotante (Floating Static Route)
Ruta estática con administrative distance mayor que sirve como respaldo cuando la ruta primaria falla.

### Buffer Pool
Memoria asignada a la base de datos para cachear páginas de datos y reducir I/O físico al disco.

### BGP (Border Gateway Protocol)
Protocolo de enrutamiento exterior usado para intercambiar información de rutas entre sistemas autónomos en Internet.

---

## C

### Core (Núcleo de Red)
Capa central de la arquitectura de red que interconecta todas las distribuciones y proporciona conectividad de alta velocidad.

### CPU Ready (Virtualización)
Métrica que indica el porcentaje de tiempo que una máquina virtual espera por recursos de CPU física en el hypervisor.

### CRC Error
Error de verificación cíclica de redundancia que indica corrupción de datos en transmisión, generalmente causado por cableado defectuoso.

---

## D

### DHCP (Dynamic Host Configuration Protocol)
Protocolo que asigna automáticamente direcciones IP y configuración de red a dispositivos clientes.

### Distribución (Capa de)
Capa intermedia de la arquitectura jerárquica de red que agrega tráfico de acceso y aplica políticas.

### DDoS (Distributed Denial of Service)
Ataque que satura un servicio o recurso mediante tráfico malicioso desde múltiples fuentes distribuidas.

---

## E

### Enlace WAN
Conexión de área amplia que interconecta sucursales con el datacenter central del banco.

### Escalamiento
Proceso de elevar un incidente a niveles superiores de soporte según severidad y tiempo transcurrido.

### SVI (Switched Virtual Interface)
Interfaz virtual Layer 3 en un switch que representa una VLAN y permite enrutamiento entre VLANs.

---

## F

### Failover
Proceso automático o manual de cambio a un componente o enlace de respaldo cuando el primario falla.

### Firewall
Dispositivo de seguridad que filtra tráfico de red según reglas predefinidas para proteger la infraestructura.

### Full Table Scan
Operación de base de datos que lee todas las filas de una tabla porque no hay índice útil para la consulta.

---

## G

### Gateway (Puerta de Enlace)
Dispositivo que sirve como punto de salida de una red local hacia otras redes o Internet.

### QoS (Quality of Service)
Conjunto de tecnologías que priorizan cierto tipo de tráfico (voz, video, transacciones) sobre otro en la red.

---

## H

### Hit Ratio
Porcentaje de solicitudes de datos que se satisfacen desde caché en lugar de leer desde disco. Valores >90% son deseables.

### Helper Address (IP Helper)
Dirección IP configurada en un router o switch para reenviar broadcasts DHCP a un servidor DHCP en otra subred.

---

## I

### I/O (Input/Output)
Operaciones de lectura y escritura en dispositivos de almacenamiento. Métrica crítica para rendimiento de bases de datos.

### Índice (Base de Datos)
Estructura que mejora la velocidad de recuperación de datos en una tabla a cambio de espacio adicional y overhead en escrituras.

### ISP (Internet Service Provider)
Proveedor de servicios de Internet que proporciona conectividad WAN al banco.

---

## J

### Jitter
Variación en la latencia de paquetes consecutivos. Crítico para aplicaciones de voz y video en tiempo real.

---

## L

### LAN (Local Area Network)
Red de área local dentro de una sucursal o datacenter del banco.

### Latencia
Tiempo que tarda un paquete en viajar desde el origen hasta el destino. Medido en milisegundos (ms).

### Lock (Bloqueo)
Mecanismo de base de datos que previene acceso concurrente conflictivo a datos durante transacciones.

---

## M

### MPLS (Multiprotocol Label Switching)
Tecnología de red WAN que usa etiquetas para dirigir datos a través de caminos predefinidos, común en bancos.

### MTTR (Mean Time To Resolution)
Tiempo promedio para resolver incidentes. Métrica clave de efectividad del equipo de operaciones.

### MTBF (Mean Time Between Failures)
Tiempo promedio entre fallos de un sistema. Métrica de confiabilidad.

---

## N

### NIC (Network Interface Card)
Tarjeta de interfaz de red que conecta un dispositivo a la red.

### Next-Hop
Dirección IP del siguiente router en el camino hacia un destino.

### NX-OS
Sistema operativo de Cisco para switches y routers de datacenter de gama alta.

---

## O

### OSPF (Open Shortest Path First)
Protocolo de enrutamiento interior basado en estado de enlace, ampliamente usado en redes empresariales.

### Onboarding
Proceso de incorporación y capacitación de nuevo personal al equipo y sistemas.

---

## P

### Packet Loss (Pérdida de Paquetes)
Porcentaje de paquetes que no llegan a su destino. Cualquier pérdida >0% es preocupante para tráfico crítico.

### PGA (Program Global Area)
Memoria privada asignada a cada sesión de usuario en Oracle Database.

### Pull Request (PR)
Mecanismo de Git para proponer cambios al repositorio que requieren revisión antes de ser mergeados.

---

## R

### Router Core
Router principal que interconecta toda la red del banco y proporciona conectividad a ISPs.

### ROMMON (ROM Monitor)
Modo de bajo nivel en routers Cisco usado para recovery cuando el sistema no puede bootear normalmente.

### RTT (Round Trip Time)
Tiempo total para que un paquete viaje ida y vuelta entre origen y destino.

---

## S

### Scope DHCP
Rango de direcciones IP que un servidor DHCP puede asignar a clientes.

### SGA (System Global Area)
Memoria compartida asignada a una instancia de Oracle Database para caché y estructuras de control.

### SSH (Secure Shell)
Protocolo criptográfico para acceso remoto seguro a dispositivos de red y servidores.

### Subred (Subnet)
División lógica de una red IP que permite segmentación y mejor gestión del espacio de direcciones.

### Swap
Espacio en disco usado como extensión de memoria RAM cuando esta se agota. Debe minimizarse en servidores críticos.

---

## T

### TCP (Transmission Control Protocol)
Protocolo de transporte orientado a conexión que garantiza entrega ordenada y sin errores de datos.

### Throughput
Cantidad de datos procesados o transmitidos por unidad de tiempo. Medido en Mbps o Gbps.

### Timeout
Límite de tiempo máximo esperado para una operación antes de considerarla fallida.

### Trunk
Enlace que transporta tráfico de múltiples VLANs entre switches usando tagging 802.1Q.

---

## V

### VLAN (Virtual Local Area Network)
Segmentación lógica de una red física en múltiples dominios de broadcast independientes.

### VPN (Virtual Private Network)
Túnel cifrado que extiende una red privada a través de una red pública (Internet).

### VRF (Virtual Routing and Forwarding)
Instancia de tabla de enrutamiento independiente que permite múltiples redes virtuales en un mismo router físico.

---

## W

### Wait Event (Evento de Espera)
Estado en base de datos donde una sesión espera por un recurso (I/O, lock, red). Usado para diagnóstico de rendimiento.

### WAN (Wide Area Network)
Red de área amplia que interconecta sucursales geográficamente dispersas del banco.

---

## Símbolos y Abreviaturas Comunes

| Símbolo | Significado |
|---------|-------------|
| <  | Menor que |
| >  | Mayor que |
| ≤  | Menor o igual que |
| ≥  | Mayor o igual que |
| →  | Conduce a / resulta en |
| ±  | Más o menos / aproximadamente |
| ~  | Aproximadamente |
| /  | Por / o (según contexto) |
| &  | Y / Ampersand |

---

**🏦 Banco Tecnológico - Departamento de TI**  
*Última actualización: 2024-01-15*  
*¿Falta algún término? Contribuye vía Pull Request*
