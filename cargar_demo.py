"""Opcional: cargar datos ficticios en la base local."""
import csv
from src.inventario import conectar, alta
cx=conectar()
with open('datos/productos_demo.csv',encoding='utf-8',newline='') as f:
    for fila in csv.DictReader(f):
        try:
            alta(cx,fila['nombre'],fila['categoria'],fila['costo_mxn'],fila['precio_mxn'],int(fila['existencias']),int(fila['minimo']))
            print('Agregado:',fila['nombre'])
        except ValueError as e:print('Omitido:',fila['nombre'],e)
cx.close()
