import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from inventario import conectar,alta,productos,movimiento,historial,resumen,editar,desactivar,reactivar,centavos

@pytest.fixture
def db(tmp_path):
    cx=conectar(tmp_path/'test.db')
    yield cx
    cx.close()

def test_alta_y_stock_inicial(db):
    alta(db,'Arroz','Abarrotes',20,30,8,3)
    assert productos(db)[0]['existencias']==8
    assert historial(db)[0]['nota']=='Inventario inicial'

def test_entrada_salida(db):
    pid=alta(db,'Leche','Lácteos',15,22,5,2)
    movimiento(db,pid,'entrada',4,'proveedor')
    movimiento(db,pid,'salida',3,'venta')
    assert productos(db)[0]['existencias']==6
    assert resumen(db)['ventas_centavos']==6600
    assert resumen(db)['margen_bruto_centavos']==2100

def test_no_permite_stock_negativo(db):
    pid=alta(db,'Agua','Bebidas',7,12,2,1)
    with pytest.raises(ValueError): movimiento(db,pid,'salida',3)
    assert productos(db)[0]['existencias']==2

def test_rechaza_nombre_duplicado(db):
    alta(db,'Arroz','Abarrotes',20,30)
    with pytest.raises(ValueError):alta(db,'arroz','Abarrotes',20,30)

def test_rechaza_cantidades_invalidas(db):
    pid=alta(db,'Galletas','Abarrotes',10,15)
    with pytest.raises(ValueError):movimiento(db,pid,'entrada',0)
    with pytest.raises(ValueError):alta(db,'X','Otros',-2,5)

def test_editar_desactivar_conserva_historial(db):
    pid=alta(db,'Pan','Abarrotes',10,15,3)
    editar(db,pid,'Pan dulce','Abarrotes',11,18,2)
    desactivar(db,pid)
    assert productos(db)==[]
    assert historial(db)[0]['nombre']=='Pan dulce'

def test_umbrales_y_redondeo(db):
    alta(db,'Sal','Abarrotes',2.345,3.456,4,4)
    assert resumen(db)['bajos']==1
    assert centavos('2.345')==235


def test_reactivar_conserva_id_stock_e_historial(db):
    pid=alta(db,'Galletas','Abarrotes',10,16,12,3)
    movimiento(db,pid,'salida',2,'venta antes de archivar')
    desactivar(db,pid)
    assert productos(db)==[]
    assert len(historial(db))==2
    reactivar(db,pid)
    recuperado=productos(db)[0]
    assert recuperado['id']==pid
    assert recuperado['existencias']==10
    assert len(historial(db))==2
    assert historial(db)[0]['nombre']=='Galletas'


def test_no_permite_alta_archivado_y_sugiere_reactivar(db):
    pid=alta(db,'Galletas','Abarrotes',10,16)
    desactivar(db,pid)
    with pytest.raises(ValueError, match='archivado'):
        alta(db,'GALLETAS','Abarrotes',10,16)
    assert len(productos(db, incluir_inactivos=True))==1


def test_reactivar_dos_veces_da_error(db):
    pid=alta(db,'Arroz','Abarrotes',10,16)
    desactivar(db,pid)
    reactivar(db,pid)
    with pytest.raises(ValueError, match='archivado'):
        reactivar(db,pid)


def test_existencias_despues_de_cada_movimiento(db):
    pid = alta(db, 'Arroz', 'Abarrotes', 21.5, 29, 18, 5)
    movimiento(db, pid, 'salida', 13)
    movimiento(db, pid, 'entrada', 4)
    movs = historial(db)
    assert [m['existencias_despues'] for m in movs] == [9, 5, 18]
    assert productos(db)[0]['existencias'] == 9


def test_salida_excesiva_no_modifica_ni_historial_ni_saldo(db):
    pid = alta(db, 'Jabón de trastes', 'Limpieza', 15, 22, 4, 2)
    original = len(historial(db))
    with pytest.raises(ValueError, match='solo hay 4'):
        movimiento(db, pid, 'salida', 6)
    assert productos(db)[0]['existencias'] == 4
    assert len(historial(db)) == original


def test_migracion_de_base_anterior(tmp_path):
    from inventario import conectar
    ruta = tmp_path/'antigua.db'
    cx = conectar(ruta)
    pid = alta(cx, 'Leche', 'Lácteos', 14, 20, 6)
    movimiento(cx, pid, 'salida', 2)
    cx.execute('UPDATE movimientos SET existencias_despues=NULL')
    cx.commit()
    cx.close()
    cx = conectar(ruta)
    assert [x['existencias_despues'] for x in historial(cx)] == [4, 6]
    cx.close()


def test_migracion_mixta_no_altera_movimientos_recientes(tmp_path):
    ruta = tmp_path / 'mezclada.db'
    cx = conectar(ruta)
    pid = alta(cx, 'Arroz', 'Abarrotes', 20, 30, 10)
    movimiento(cx, pid, 'salida', 3)
    movimiento(cx, pid, 'entrada', 5)
    # Falta el dato en el movimiento intermedio, pero el más nuevo sí lo tiene.
    cx.execute('UPDATE movimientos SET existencias_despues=NULL WHERE tipo="salida"')
    cx.commit()
    cx.close()
    cx = conectar(ruta)
    assert [m['existencias_despues'] for m in historial(cx)] == [12, 7, 10]
    cx.close()
