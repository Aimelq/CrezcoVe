# 🏢 Arquitectura y Flujos del Sistema CrezcoVe (Inventario Inteligente)

El sistema **CrezcoVe** está diseñado como un ERP (Enterprise Resource Planning) focalizado en el control inteligente de inventario para PYMEs. Utiliza múltiples tecnologías coordinadas (React, Flask, PostgreSQL, Redis, Celery, n8n y Telegram) para no solo llevar cuentas, sino tomar decisiones activas (sugerir precios, auditar robos y prever quiebres de stock).

A continuación, se detalla orgánicamente cada capa, módulo, flujo y decisión que toma el sistema.

---

## 1. 🏗️ Arquitectura General y Módulos

El sistema está dividido en microservicios gestionados vía Docker:
1. **Frontend (App Web)**: Interfaz de usuario en React, Vite y TypeScript (+ Tailwind/Shadcn).
2. **Backend (API Base)**: Servidor Flask en Python, expone la API RESTful.
3. **Workers Asíncronos (Celery + Redis)**: Procesan tareas pesadas en segundo plano (cálculos masivos, envío de notificaciones).
4. **Base de Datos (PostgreSQL)**: Almacena todo el modelo relacional.
5. **Automatización (n8n)**: Motor de flujos (workflows) para ejecutar tareas recurrentes o responder a webhooks.
6. **Bot de Telegram**: Asistente móvil integrado a la misma base de datos, para reportes rápidos y alertas.

---

## 2. 🧠 Servicios Inteligentes (Lógica de Negocio Principal)

El corazón de CrezcoVe no es un simple CRUD, cuenta con 6 motores analíticos ("Servicios"):

### A. Calculadora de Costos y Asistente de Precios (`calculadora_costo.py`, `asistente_precios.py`)
- **Problema**: La inflación o cambio de proveedores varía los costos constantemente.
- **Toma de Decisión (Bifurcación)**:
  - Cuando se hace un *Ingreso de Mercancía*, el sistema evalúa: ¿Es un producto nuevo o ya había stock?
  - Si ya había stock, realiza el cálculo del **Costo Promedio Ponderado** (mezcla el costo del inventario viejo con el precio de la nueva factura).
  - Almacena por separado el *Último Costo de Compra* y genera un *Costo de Referencia* (usualmente el mayor entre el promedio y el último costo preventivamente).
  - El **Asistente de Precios** evalúa si el *Margen Deseado* estipulado por el dueño se sigue cumpliendo. Si el costo subió, genera una notificación recomendando ajustar el Precio de Venta.

### B. Predicción de Agotamiento (`prediccion_agotamiento.py`)
- **Problema**: Comprar a destiempo (muy temprano amarra dinero, muy tarde rompe stock).
- **Toma de Decisión**:
  - Lee el historial consecutivo de movimientos de tipo "Venta" en los últimos días.
  - Calcula la *Velocidad de Venta* (ej: 5 items por día promedio).
  - Divide el *Stock Actual* entre la *Velocidad de Venta* para proyectar la **Fecha Exacta de Agotamiento**.
  - Si los "días restantes" caen en nivel URGENCE o CRITICO, levanta una `Alerta` que Telegram / n8n enviarán de inmediato.

### C. Auditoría Ciega (Anti-Robo) (`auditoria_ciega.py`)
- **Problema**: El típico inventario muestra al empleado lo que "debería haber", facilitando que cuadren el número en caso de hurto.
- **Flujo**:
  - Un proceso automático lanza una "Auditoría Aleatoria".
  - En pantalla, el empleado ve una lista de X productos, pero **NO ve cuánto hay en sistema**, solo un campo vacío.
  - El empleado va físicamente, cuenta la mercancía y anota "5".
  - El backend cruza: Físico (5) vs Sistema (20). Detecta *Discrepancia*.
  - Registra temporalmente la discrepancia en un `Auditoria_Log` (log inmutable) y notifica directamente al gerente (vía Telegram) sobre una posible pérdida o merma silenciosa para que este la aplique.

  (ESTA FUNCIONALIDAD AUN NO SE HA PROBADO)

### D. Dinero Dormido (`dinero_dormido.py`)
- **Flujo**: Diariamente, Celery escanea aquellos productos con `cantidad_actual > 0` que no han tenido ninguna salida o venta en los últimos $N$ días (ej. 60 días).
- Genera un reporte de *Inmovilización de Capital* recomendando remates o promociones.

### E. Integración Multimoneda / BCV (`tasa_cambio.py`)
- Realiza de manera automatizada scraping o lectura del portal oficial del Banco Central de Venezuela para obtener la tasa de cambio USD/VES aplicable al día.

### F. Decimales y Fraccionamiento (`servicio_lotes.py`, Modelos)
- Tiene soporte estricto para bienes "a granel" (`permite_decimales = True`).
- Soporta relación *Padre-Hijo*. Si ingresas 1 "Cuerpo de Queso" (Padre) puedes configurar un factor de conversión para venderlo como múltiples "Kilos de Queso" (Hijo). 

---

## 3. 👥 Flujos a Nivel de Usuario

### Flujo 1: Ingreso de Inventario (Compra)
1. Usuario abre **Formulario de Compra**.
2. Selecciona Proveedor, Producto, Lote (con fecha de vencimiento si aplica), Cantidad, Costo Unitario Factura.
3. El Backend recibe el request -> Crea `MovimientoInventario` (Tipo: INGRESO).
4. El Backend inserta los items en `LoteProducto` asociados a la fecha caducidad.
5. Dispara el `Asistente de Precios` y recalcula costos promedios.
6. Cierra Alertas previas (si el producto estaba bajo de stock, ahora la alerta se pone en estado `resuelta`).
7. El sistema recalcula la **Fecha de Agotamiento**.

### Flujo 2: Salida (Venta de Mostrador)
1. Usuario anota ítems para Venta. 
2. Sistema valida en tiempo real: ¿Hay stock? Si es producto sin decimales e intenta vender "1.5 botellas", lanza error `400 Bad Request`.
3. Para artículos fraccionables, debita el peso (e.g. 0.25 kg). Descuenta usando método **FIFO en lotes** (se lleva del lote más viejo a expirar).
4. El backend detecta `cantidad_actual` < `stock_minimo`. Lanza un flag `esta_bajo_stock = True`.
5. Esto envía un webhook asíncrono a **n8n / Telegram** alertando inmediatamente: *"¡Stock Bajo en Refresco Cola!"*

### Flujo 3: Mermas y Cierres (Ajustes)
1. Todo ajuste que no sea venta lleva el tipo "MERMA" o "AJUSTE", forzando a llenar el campo *Descripción* obligatoriamente. 
2. En la base de datos se almacena de forma inauditable mediante `Auditoria_Log` para evitar colusión interna.

---

## 4. 📦 Sistema de Lotes (`LoteProducto`, `ServicioLotes`)

El sistema de lotes es el mecanismo que da **trazabilidad real** a cada unidad física de mercancía, desde que entra al almacén hasta que sale por una venta o se descarta. Es la diferencia entre saber *cuánto* hay y saber *de qué origen exacto* es cada unidad.

### 4.1 Estructura del Lote (`LoteProducto`)

Cada vez que ingresa mercancía, puede crear o actualizar un registro en la tabla `lotes_producto`. Un lote contiene:

| Campo | Descripción |
|---|---|
| `numero_lote` | Identificador del lote (del fabricante o autogenerado) |
| `fecha_recepcion` | Cuándo entró físicamente al almacén |
| `fecha_vencimiento` | Cuándo caduca (opcional, solo perecederos) |
| `cantidad_inicial` | Cuántas unidades entraron en ese lote |
| `cantidad_actual` | Cuánto queda todavía de ese lote |
| `costo_lote` | El costo unitario pagado en esa compra puntual |
| `proveedor_id` | Qué proveedor suministró ese lote |

Las propiedades calculadas en tiempo real son:
- `esta_vencido`: `True` si `fecha_vencimiento < hoy`
- `dias_hasta_vencimiento`: Número entero de días restantes
- `proximo_a_vencer`: `True` si quedan **≤ 7 días** para vencer

### 4.2 Autogeneración de Número de Lote

**Bifurcación en la recepción de mercancía:**
- Si el proveedor proporciona un número de lote del fabricante → se usa ese.
- Si el producto es perecedero (`tiene_vencimiento = True`) y NO se proporciona número de lote → el sistema **autogenera** uno basado en el timestamp: `LOTE-AUT-20260414143022`.
- Si el producto no es perecedero y no se proporciona lote → el ingreso se registra como movimiento "suelto" sin lote asignado (válido para productos sin trazabilidad de lote).

### 4.3 Algoritmo de Despacho: FEFO vs FIFO

Cuando ocurre una **venta, ajuste/merma o fraccionamiento**, el `ServicioLotes.descontar_lotes_estrategicos()` decide automáticamente de qué lote sacar la mercancía:

```
producto.tiene_vencimiento == True → aplica FEFO
producto.tiene_vencimiento == False → aplica FIFO
```

**FEFO (First Expire, First Out) — Perecederos:**
1. Busca todos los lotes activos con `cantidad_actual > 0`.
2. Separa los que tienen `fecha_vencimiento` de los que no la tienen.
3. Ordena los que sí tienen fecha: **los que vencen antes, primero**.
4. Los lotes sin fecha de vencimiento van al final (se usan de último).
5. Va extrayendo de cada lote en orden hasta completar la cantidad vendida.

**FIFO (First In, First Out) — No Perecederos:**
1. Ordena todos los lotes por `fecha_recepcion` ascendente.
2. Despacha del lote más antiguo primero.

**Resultado devuelto (para auditoría):**
```json
[
  { "lote_id": 12, "numero_lote": "LOTE-AUT-20260301...", "cantidad_descontada": 5.0, "restante_en_lote": 3.0 },
  { "lote_id": 15, "numero_lote": "LOTE-PROV-XYZ",      "cantidad_descontada": 2.0, "restante_en_lote": 0.0 }
]
```

> **Nota importante**: Si un producto **no tiene lotes registrados** (vieja mercancía sin trazabilidad), el sistema despacha igual pero sin descontar de ningún lote — el stock del producto disminuye solo a nivel del campo `cantidad_actual` del producto.

### 4.4 Flujo de Validación al Ingresar un Lote Perecedero

```
POST /api/inventario/ingreso
│
├─ ¿producto.tiene_vencimiento == True?
│   ├─ NO → continúa normalmente (lote opcional)
│   └─ SÍ → ¿Se envió fecha_vencimiento?
│           ├─ NO → Error 400: "Producto perecedero requiere fecha de vencimiento"
│           └─ SÍ → ¿fecha_vencimiento < hoy?
│                   ├─ SÍ → Error 400: "No se puede ingresar producto ya vencido"
│                   └─ NO → ¿Se envió numero_lote?
│                           ├─ SÍ → ¿Existe ya ese lote en BD?
│                           │       ├─ SÍ → Se ACUMULA cantidad al lote existente
│                           │       └─ NO → Se CREA lote nuevo
│                           └─ NO → Se AUTOGENERA numero_lote (LOTE-AUT-...)
│
└─ Se registra MovimientoInventario con lote_id vinculado
```

### 4.5 Fraccionamiento / Desempacado (`/api/inventario/desempacar`)

Esta es la operación más compleja del sistema de lotes. Permite **convertir 1 unidad grande (Padre) en N unidades pequeñas (Hijo)** manteniendo trazabilidad de costos y vencimientos.

**Ejemplo de negocio**: Tienes "Cuerpo de Queso Entero" (Padre) con factor de conversión = 10, y el producto hijo es "Kg de Queso".

**Flujo Completo de Desempacado:**

```
1. Recibe: producto_hijo_id + cantidad_a_desempacar (default: 1)

2. Validaciones:
   ├─ ¿Existe el producto hijo?
   ├─ ¿Tiene producto_padre configurado?
   ├─ ¿El padre tiene permite_decimales=False y cantidad es decimal? → Error 400
   └─ ¿El padre tiene stock suficiente? → Error 400

3. RESTAR DEL PADRE (Salida por Fraccionamiento):
   ├─ Descuenta cantidad_a_desempacar del campo cantidad_actual del padre
   ├─ Llama a ServicioLotes.descontar_lotes_estrategicos(padre_id) → FEFO/FIFO
   ├─ Captura el vencimiento del lote padre sacrificado (para heredarlo)
   └─ Crea MovimientoInventario tipo AJUSTE, motivo FRACCIONAMIENTO_SALIDA

4. SUMAR AL HIJO (Entrada por Fraccionamiento):
   ├─ cantidad_hijo = cantidad_a_desempacar × factor_conversion
   ├─ costo_unitario_hijo = costo_promedio_padre / factor_conversion  ← Pro-rateo de costo
   ├─ Actualiza costo_promedio del producto hijo
   │
   ├─ HERENCIA DE LOTE:
   │   ├─ Se genera: numero_lote_hijo = "{numero_lote_padre}-UNID"
   │   ├─ ¿Ese lote hijo ya existe?
   │   │   ├─ SÍ → Se acumula cantidad
   │   │   └─ NO → Se crea lote hijo con fecha_vencimiento HEREDADA del padre
   │   └─ El lote hijo queda vinculado al movimiento del hijo
   │
   └─ Crea MovimientoInventario tipo AJUSTE, motivo FRACCIONAMIENTO_ENTRADA

5. db.session.commit() — Todo es atómico (si algo falla, rollback total)

6. Retorna: estado actualizado del Padre + Hijo
```

> **Clave del diseño**: El costo se hereda dividido entre el factor, y la fecha de vencimiento del lote padre se **propaga automáticamente** al lote hijo. Esto garantiza que aunque fracciones la mercancía, el sistema sigue sabiendo cuándo vence cada unidad individual.

---

## 5. 🤖 Intervenciones Automatizadas (Bots y Scripts)

1. **Telegram**:
   - Tú (o empleado con permisos) envía `/ventashoy`.
   - El bot consulta directamente PostgreSQL filtrando Movimientos del día.
   - Retorna: Total Ventas USD, Margen de Ganancia del día, Gastos.
   - Funciona sin abrir la web app.

2. **Cron Jobs vía Celery / n8n**:
   - `Reporte Diario (21:00h)`: Sumariza actividad de cajeros y ventas, despachándolas por Telegram.
   - `Escaneo de Vencimientos`: Chequea la tabla `LoteProducto`. Si `fecha_vencimiento - current_date <= dias_alerta`, levanta una bandera de producto perecedero en riesgo.

---

## 5. 🗃️ Modelo de Base de Datos Subyacente (Bifurcaciones Lógicas)
- **Soft Delete**: Si eliminas un producto el sistema **NO** hace `DELETE FROM`. Hace un "Soft Delete" ocultándolo (`esta_activo = False`) y añadiendo un timestamp a su SKU (`SKU_DEL_17123`). Esto preserva el balance fiscal histórico; la venta que hiciste hace 3 meses con ese producto nunca se daña.
- **Doble Origen de Datos**: La entidad producto no asume un costo eterno. Contiene `costo_promedio` (usado para valoración real de tu balance de la empresa) y `ultimo_costo_compra` (usado referencialmente por si las cosas subieron bruscamente hoy para calcular precio nuevo).
- **Control de Acceso (RBAC)**: Validaciones para dueños vs de a pie. Si no tienes permisos de gerente no ves reportes de ganancia o márgenes de valor patrimonial.

## Resumen del Comportamiento Interno General:
Este software funciona conceptualmente como un **sistema predictivo más que un registro ciego**. Cada vez que entra o sale un byte de información del almacén, recalcula promedios financieros, evalúa tiempos de reposición mediante algoritmos predictivos de consumo histórico y envía correcciones o advertencias de manera proactiva previniendo robo o estancamiento de dinero.
