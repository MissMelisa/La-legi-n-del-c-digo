"""
Menú de consola: CRUD de productos, búsquedas y vista de precios,
todo conectado a la base de datos (datos_comercios).

How to use it:
    python scripts/menu.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "producto"))

from conexion import ConexionBD
from producto import Producto
from productoCRUD import ProductoCRUD


def pedir_texto(mensaje, permitir_vacio=True):
    valor = input(mensaje).strip()
    while not permitir_vacio and not valor:
        print("Este dato es obligatorio.")
        valor = input(mensaje).strip()
    return valor


# ==================================================
# CRUD
# ==================================================

def alta_producto(repo):
    print("\n--- Alta de producto ---")
    producto_id = pedir_texto("ID del producto: ", permitir_vacio=False)

    if repo.obtener_por_id(producto_id):
        print(f"Ya existe un producto con id '{producto_id}'.")
        return

    marca = pedir_texto("Marca: ")
    nombre = pedir_texto("Nombre: ")
    presentacion = pedir_texto("Presentación: ")
    categoria_1 = pedir_texto("Categoría 1: ")
    categoria_2 = pedir_texto("Categoría 2: ")
    categoria_3 = pedir_texto("Categoría 3: ")

    producto = Producto(
        id=producto_id, marca=marca, nombre=nombre,
        presentacion=presentacion, categoria_1=categoria_1,
        categoria_2=categoria_2, categoria_3=categoria_3,
    )
    repo.crear(producto)
    print(f"Producto '{producto_id}' creado.")


def baja_producto(repo):
    print("\n--- Baja de producto ---")
    producto_id = pedir_texto("ID del producto a eliminar: ", permitir_vacio=False)

    producto = repo.obtener_por_id(producto_id)
    if not producto:
        print(f"No existe un producto con id '{producto_id}'.")
        return

    print(producto)
    confirmacion = pedir_texto(
        "¿Confirma la eliminación? También se eliminan sus precios (s/n): "
    ).lower()
    if confirmacion == "s":
        repo.eliminar(producto_id)
        print("Producto eliminado.")
    else:
        print("Operación cancelada.")


def modificar_producto(repo):
    print("\n--- Modificación de producto ---")
    producto_id = pedir_texto("ID del producto a modificar: ", permitir_vacio=False)

    producto = repo.obtener_por_id(producto_id)
    if not producto:
        print(f"No existe un producto con id '{producto_id}'.")
        return

    print(producto)
    print("(Dejar vacío para mantener el valor actual)")

    marca = pedir_texto(f"Marca [{producto.marca}]: ") or producto.marca
    nombre = pedir_texto(f"Nombre [{producto.nombre}]: ") or producto.nombre
    presentacion = pedir_texto(
        f"Presentación [{producto.presentacion}]: "
    ) or producto.presentacion
    categoria_1 = pedir_texto(
        f"Categoría 1 [{producto.categoria_1}]: "
    ) or producto.categoria_1
    categoria_2 = pedir_texto(
        f"Categoría 2 [{producto.categoria_2}]: "
    ) or producto.categoria_2
    categoria_3 = pedir_texto(
        f"Categoría 3 [{producto.categoria_3}]: "
    ) or producto.categoria_3

    producto_actualizado = Producto(
        id=producto_id, marca=marca, nombre=nombre,
        presentacion=presentacion, categoria_1=categoria_1,
        categoria_2=categoria_2, categoria_3=categoria_3,
    )
    repo.actualizar(producto_actualizado)
    print("Producto actualizado.")


# ==================================================
# Búsquedas
# ==================================================

def mostrar_productos(productos, incluir_id=True):
    if not productos:
        print("No se encontraron productos.")
        return
    for producto in productos:
        if incluir_id:
            print(producto)
        else:
            categorias = "/".join(
                c for c in (
                    producto.categoria_1, producto.categoria_2, producto.categoria_3
                ) if c
            )
            print(
                f"{producto.nombre} ({producto.marca}) - {producto.presentacion}"
                + (f" | {categorias}" if categorias else "")
            )
    print(f"Total: {len(productos)}")


def buscar_por_nombre(repo):
    print("\n--- Búsqueda por nombre ---")
    texto = pedir_texto("Texto a buscar en el nombre: ", permitir_vacio=False)
    mostrar_productos(repo.buscar_por_nombre(texto), incluir_id=False)


def buscar_por_categoria(repo):
    print("\n--- Búsqueda por categoría ---")

    categorias = repo.listar_categorias()
    if not categorias:
        print("No hay categorías cargadas.")
        return

    for i, categoria in enumerate(categorias, start=1):
        print(f"{i}. {categoria}")

    opcion = pedir_texto("Elegí una categoría (número): ", permitir_vacio=False)
    if not opcion.isdigit() or not (1 <= int(opcion) <= len(categorias)):
        print("Opción inválida.")
        return

    categoria = categorias[int(opcion) - 1]
    mostrar_productos(repo.buscar_por_categoria(categoria))


# ==================================================
# Vista
# ==================================================

def ver_vista_precios(repo):
    print("\n--- Vista: precios por producto y sucursal ---")
    producto_id = pedir_texto("ID de producto (vacío = todos, primeros 50): ")

    filas = repo.listar_vista_precios(producto_id or None)
    if not filas:
        print("No hay datos para mostrar (¿se creó la vista con "
              "sql/06_vista_precios_detalle.sql?).")
        return

    for fila in filas:
        print(
            f"{fila['producto']} ({fila['marca']}) - "
            f"${fila['precio']} en {fila['sucursal_nombre']} "
            f"({fila['localidad']}, {fila['provincia']})"
        )
    print(f"Total: {len(filas)}")


# ==================================================
# MENÚ PRINCIPAL
# ==================================================

MENU = """
========================================
 datos_comercios - Menú principal
========================================
1. Alta de producto
2. Baja de producto
3. Modificación de producto
4. Buscar productos por nombre
5. Buscar productos por categoría
6. Ver vista de precios por producto/sucursal
0. Salir
"""

ACCIONES = {
    "1": alta_producto,
    "2": baja_producto,
    "3": modificar_producto,
    "4": buscar_por_nombre,
    "5": buscar_por_categoria,
    "6": ver_vista_precios,
}


def main():
    conexion = ConexionBD()
    repo = ProductoCRUD(conexion)

    try:
        conexion.conectar()
    except Exception as exc:
        print(f"No se pudo conectar a la base de datos: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        while True:
            print(MENU)
            opcion = input("Elegí una opción: ").strip()

            if opcion == "0":
                print("¡Hasta luego!")
                break

            accion = ACCIONES.get(opcion)
            if accion is None:
                print("Opción inválida.")
                continue

            try:
                accion(repo)
            except Exception as exc:
                print(f"Ocurrió un error: {exc}", file=sys.stderr)
    finally:
        conexion.cerrar()


if __name__ == "__main__":
    main()
