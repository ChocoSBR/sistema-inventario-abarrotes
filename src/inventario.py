"""Lógica de JacaStock. Sin dependencias externas; usa SQLite."""
from __future__ import annotations
import csv
import io
import sqlite3
from datetime import datetime
from pathlib import Path


def conectar(ruta="datos/inventario.db"):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    cx = sqlite3.connect(str(ruta), timeout=15)
    cx.row_factory = sqlite3.Row
    cx.execute("PRAGMA foreign_keys = ON")
    cx.execute("PRAGMA busy_timeout = 15000")
    cx.executescript("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL COLLATE NOCASE UNIQUE,
            categoria TEXT NOT NULL,
            costo_centavos INTEGER NOT NULL CHECK(costo_centavos>=0),
            precio_centavos INTEGER NOT NULL CHECK(precio_centavos>=0),
            existencias INTEGER NOT NULL DEFAULT 0 CHECK(existencias>=0),
            minimo INTEGER NOT NULL DEFAULT 5 CHECK(minimo>=0),
            activo INTEGER NOT NULL DEFAULT 1 CHECK(activo IN (0,1))
        );
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL REFERENCES productos(id),
            tipo TEXT NOT NULL CHECK(tipo IN ('entrada','salida')),
            cantidad INTEGER NOT NULL CHECK(cantidad>0),
            fecha TEXT NOT NULL,
            nota TEXT NOT NULL DEFAULT '',
            precio_venta_centavos INTEGER,
            costo_unitario_centavos INTEGER,
            existencias_despues INTEGER
        );
    """)
    # Migración transparente: bases creadas antes de esta actualización.
    columnas = {fila['name'] for fila in cx.execute('PRAGMA table_info(movimientos)')}
    if 'existencias_despues' not in columnas:
        cx.execute('ALTER TABLE movimientos ADD COLUMN existencias_despues INTEGER')

    # Completar saldos históricos faltantes sin modificar los ya registrados.
    # Recorrer TODOS los movimientos, incluso los recientes que ya tienen saldo,
    # para reconstruir correctamente bases que mezclan versiones del programa.
    pendientes = cx.execute("SELECT COUNT(*) FROM movimientos WHERE existencias_despues IS NULL").fetchone()[0]
    if pendientes:
        saldo = {r['id']: r['existencias'] for r in cx.execute('SELECT id, existencias FROM productos')}
        filas = cx.execute('SELECT id, producto_id, tipo, cantidad, existencias_despues '
                           'FROM movimientos ORDER BY producto_id, id DESC').fetchall()
        for fila in filas:
            pid = fila['producto_id']
            posterior = saldo[pid]
            if fila['existencias_despues'] is None:
                cx.execute('UPDATE movimientos SET existencias_despues=? WHERE id=?',
                           (posterior, fila['id']))
            saldo[pid] = posterior - fila['cantidad'] if fila['tipo'] == 'entrada' else posterior + fila['cantidad']
    cx.commit()
    return cx


def centavos(monto):
    from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
    try:
        valor = Decimal(str(monto))
        if not valor.is_finite() or valor < 0:
            raise ValueError('El monto debe ser un número no negativo.')
        return int((valor*100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    except (InvalidOperation, TypeError):
        raise ValueError('Monto inválido.') from None


def alta(cx, nombre, categoria, costo, precio, existencias=0, minimo=5):
    nombre, categoria = nombre.strip(), categoria.strip()
    if not nombre or not categoria or not isinstance(existencias, int) or not isinstance(minimo, int) or min(existencias, minimo) < 0:
        raise ValueError('Revisa nombre, categoría, existencias y mínimo.')
    c, p = centavos(costo), centavos(precio)
    try:
        with cx:
            cur = cx.execute('INSERT INTO productos(nombre,categoria,costo_centavos,precio_centavos,existencias,minimo) VALUES (?,?,?,?,?,?)',
                             (nombre,categoria,c,p,existencias,minimo))
            if existencias:
                cx.execute("INSERT INTO movimientos(producto_id,tipo,cantidad,fecha,nota,costo_unitario_centavos,existencias_despues) VALUES (?, 'entrada', ?, ?, 'Inventario inicial', ?, ?)", (cur.lastrowid,existencias,ahora(),c,existencias))
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        existente = cx.execute('SELECT activo FROM productos WHERE nombre=? COLLATE NOCASE', (nombre,)).fetchone()
        if existente is not None and existente['activo'] == 0:
            raise ValueError('Ese producto está archivado. Ve a Inventario → Productos archivados y pulsa Reactivar. Así conservas su historial.') from e
        raise ValueError('Ese nombre de producto ya existe en tu inventario.') from e


def ahora():
    return datetime.now().isoformat(timespec='seconds')


def productos(cx, incluir_inactivos=False):
    sql = 'SELECT * FROM productos' + ('' if incluir_inactivos else ' WHERE activo=1') + ' ORDER BY nombre'
    return [dict(r) for r in cx.execute(sql)]


def editar(cx, producto_id, nombre, categoria, costo, precio, minimo):
    if not nombre.strip() or not categoria.strip() or not isinstance(minimo,int) or minimo<0:
        raise ValueError('Datos del producto inválidos.')
    try:
        with cx:
            cur=cx.execute('UPDATE productos SET nombre=?,categoria=?,costo_centavos=?,precio_centavos=?,minimo=? WHERE id=? AND activo=1',
                      (nombre.strip(),categoria.strip(),centavos(costo),centavos(precio),minimo,producto_id))
            if cur.rowcount==0: raise ValueError('Producto no encontrado.')
    except sqlite3.IntegrityError as e:
        raise ValueError('Ya existe un producto con ese nombre.') from e


def desactivar(cx, producto_id):
    with cx:
        cur = cx.execute('UPDATE productos SET activo=0 WHERE id=? AND activo=1', (producto_id,))
        if cur.rowcount==0: raise ValueError('Producto no encontrado.')



def reactivar(cx, producto_id):
    """Recupera un producto archivado sin cambiar sus existencias o historial."""
    with cx:
        cur = cx.execute('UPDATE productos SET activo=1 WHERE id=? AND activo=0', (producto_id,))
        if cur.rowcount == 0:
            raise ValueError('No existe un producto archivado con ese ID.')


def movimiento(cx, producto_id, tipo, cantidad, nota=''):
    if tipo not in ('entrada','salida') or not isinstance(cantidad,int) or cantidad<=0:
        raise ValueError('Tipo o cantidad incorrectos.')
    with cx:
        p=cx.execute('SELECT * FROM productos WHERE id=? AND activo=1',(producto_id,)).fetchone()
        if p is None: raise ValueError('Producto no encontrado.')
        if tipo=='salida' and p['existencias']<cantidad:
            raise ValueError(f'Existencias insuficientes: intentaste vender {cantidad}, pero solo hay {p["existencias"]} unidades disponibles.')
        cambio = cantidad if tipo=='entrada' else -cantidad
        cx.execute('UPDATE productos SET existencias=existencias+? WHERE id=?',(cambio,producto_id))
        nuevo_stock = p['existencias'] + cambio
        cx.execute('INSERT INTO movimientos(producto_id,tipo,cantidad,fecha,nota,precio_venta_centavos,costo_unitario_centavos,existencias_despues) VALUES (?,?,?,?,?,?,?,?)',
                   (producto_id,tipo,cantidad,ahora(),nota.strip(),p['precio_centavos'] if tipo=='salida' else None,p['costo_centavos'],nuevo_stock))


def historial(cx):
    return [dict(r) for r in cx.execute('''SELECT m.id,m.fecha,p.nombre,m.tipo,m.cantidad,m.nota,m.precio_venta_centavos,m.costo_unitario_centavos,m.existencias_despues
                                          FROM movimientos m JOIN productos p ON p.id=m.producto_id ORDER BY m.id DESC''')]


def resumen(cx):
    p=productos(cx)
    ventas=cx.execute("SELECT COALESCE(SUM(cantidad*precio_venta_centavos),0) FROM movimientos WHERE tipo='salida'").fetchone()[0]
    costo_ventas=cx.execute("SELECT COALESCE(SUM(cantidad*costo_unitario_centavos),0) FROM movimientos WHERE tipo='salida'").fetchone()[0]
    return {'productos':len(p),'unidades':sum(x['existencias'] for x in p),
            'bajos':sum(x['existencias']<=x['minimo'] for x in p),
            'valor_costo_centavos':sum(x['existencias']*x['costo_centavos'] for x in p),
            'ventas_centavos':ventas,'margen_bruto_centavos':ventas-costo_ventas}


def exportar_csv(filas):
    if not filas: return ''
    salida=io.StringIO()
    w=csv.DictWriter(salida,fieldnames=list(filas[0].keys()))
    w.writeheader(); w.writerows(filas)
    return '\ufeff'+salida.getvalue()
