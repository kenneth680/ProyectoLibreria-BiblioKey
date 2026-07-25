# Paradigma 4 — Declarativo

## ¿Qué es?
El **paradigma declarativo** es un modelo donde el flujo del programa
está determinado por *eventos* (acciones del usuario, mensajes del sistema, etc.)
en lugar de por una secuencia lineal predefinida. Usa el patrón
**Publicador/Suscriptor (Observer)** para desacoplar componentes.

## Archivos del paradigma

| Archivo | Descripción |
|---|---|
| `event_bus.py` | Bus global de eventos pub/sub |

## Principios aplicados

### EventBus — Publicador/Suscriptor
Cualquier módulo puede **publicar** un evento sin saber quién lo escucha.
Cualquier módulo puede **suscribirse** sin importar quién lo publicó:

```python
# Publicar evento (emisor no conoce a los suscriptores)
bus_global.publish("PRESTAMO_CREADO", {"prestamo": p.to_dict()})

# Suscribirse a un evento (suscriptor no conoce al emisor)
bus_global.subscribe("PRESTAMO_CREADO", lambda data: print(f"Nuevo: {data}"))
```

### Eventos del sistema BiblioKEY

| Evento | Cuándo se dispara | Datos adjuntos |
|---|---|---|
| `PRESTAMO_CREADO` | Al registrar un nuevo préstamo | `{prestamo: dict}` |
| `LIBRO_DEVUELTO` | Al marcar un préstamo como entregado | `{prestamo: dict}` |
| `MORA_DETECTADA` | Al detectar un libro vencido | `{prestamo: dict}` |

### Desacoplamiento reactivo
```
UI (form) ──publish──▶ EventBus ──notify──▶ Logger / Contador / Alerta
                                  ──notify──▶ Motor estadístico
                                  ──notify──▶ Sistema de multas
```

## Archivos relacionados (en el proyecto)
- [`event_bus.py`](../events/event_bus.py)
