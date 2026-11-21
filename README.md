# 🌸 JacaStock | Jacaranda Labs

**Sistema de inventario para pequeñas tiendas de abarrotes**  
**Eslogan:** Organiza tu inventario, mejora tu negocio.  
**Proyecto:** Introducción a la Economía · Grupo 1413 · UNAM

## Descripción

JacaStock es un prototipo académico desarrollado por Jacaranda Labs para facilitar el control básico del inventario en tiendas de abarrotes. Permite registrar productos y movimientos de mercancía, consultar existencias y generar reportes. El proyecto también incluye una propuesta de negocio y su análisis económico.

Este repositorio reúne el código fuente, las pruebas automatizadas, la documentación técnica, el informe para Overleaf y la presentación comercial. El trabajo está organizado para que los integrantes del equipo puedan revisar y actualizar sus respectivas áreas.

## Requisitos

- Python 3.10 o posterior.
- Dependencias indicadas en `requirements.txt`.
- Un navegador web para abrir la interfaz local de Streamlit.

## Instalación y ejecución

Abrir una terminal en la carpeta principal del proyecto.

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Si el comando `py` no está disponible, puede utilizarse `python` si está configurado en el sistema. Si PowerShell bloquea la activación, puede usarse `cmd` con `.venv\Scripts\activate.bat`.

**macOS o Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit mostrará una dirección local, generalmente <http://localhost:8501>. La aplicación se ejecuta en la computadora en la que se inicia; no está publicada como servicio en Internet.

### Datos de demostración

Si se requiere preparar **una base de prueba**, puede ejecutarse:

```powershell
python cargar_demo.py
```

Este paso es **opcional** y debe hacerse únicamente después de revisar el estado de la base de datos. No es necesario repetirlo cada vez que se abre el sistema. Los datos de demostración son ficticios.

## Funciones del prototipo

- Alta, edición y consulta de productos.
- Archivo y reactivación de productos, conservando el historial.
- Registro de entradas y salidas de mercancía.
- Validación para impedir salidas superiores a las existencias disponibles.
- Visualización del saldo que quedará después de registrar un movimiento.
- Alertas de existencias bajas.
- Historial con precio unitario, total de venta, notas y existencias posteriores al movimiento.
- Confirmaciones visibles después de operaciones exitosas.
- Exportación de inventario y movimientos en CSV.

Los importes se almacenan internamente en centavos enteros para evitar errores de redondeo; en la interfaz se muestran en pesos mexicanos.

## Pruebas

Desde la carpeta principal, ejecutar:

```bash
python -m pytest -q
```

Las pruebas automatizadas comprueban reglas del inventario, incluidas validaciones de cantidades, conservación de registros y recuperación de saldos históricos. También es necesario realizar pruebas manuales de la interfaz y documentar los resultados observados.

## Organización del repositorio

| Ruta | Contenido |
| --- | --- |
| `app.py` | Interfaz web desarrollada en Streamlit |
| `src/inventario.py` | Lógica de inventario y persistencia SQLite |
| `cargar_demo.py` | Carga opcional de datos ficticios |
| `datos/` | Base de datos local; debe respaldarse antes de actualizar |
| `tests/` | Pruebas automatizadas |
| `assets/` y `.streamlit/` | Recursos visuales y configuración |
| `presentacion/` | Presentación comercial editable |
| `exposicion/` | Material de apoyo para la defensa oral |
| `docs/` | Bitácora, materiales de investigación y pruebas de usuario |

## Trabajo en equipo

Cada integrante debe mantener actualizados sus entregables y registrar cambios relevantes en el repositorio. Para proponer cambios al código o la documentación se recomienda utilizar ramas, describir los cambios en los commits y revisar las modificaciones antes de incorporarlas a la rama principal. El informe y la exposición deben reflejar las funciones que efectivamente se hayan probado.

## Alcance y limitaciones

JacaStock es un **prototipo local**, no un servicio comercial listo para clientes. No incluye facturación electrónica, pagos, inicio de sesión por usuario, gestión de caducidades ni respaldo automático. Una versión comercial requeriría mejoras técnicas y pruebas adicionales.

Las cifras de inversión, precio, elasticidad y rentabilidad incluidas en el informe corresponden a **escenarios académicos**, no a ventas o encuestas confirmadas. Las entrevistas, pruebas de uso y capturas del sistema deberán documentarse con evidencia real.

**Protección de datos:** no subir al repositorio bases de datos con información personal o comercial sensible. Guardar respaldos de trabajo fuera de los archivos que se publiquen.

## Identidad del proyecto

**Empresa propuesta:** Jacaranda Labs  
**Producto:** JacaStock  
**Identidad gráfica:** flor de jacaranda, con paleta morada y lila.  
**Eslogan:** *Organiza tu inventario, mejora tu negocio.*
