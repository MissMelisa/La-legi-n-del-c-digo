from conexion import ConexionBD
from producto import Producto
from sucursal import Sucursal
from precio import Precio


def _dividir_truncado(filas, limite):
    """Recorta a `limite` elementos y avisa si había más resultados.

    Se usa pidiendo `limite + 1` filas a la base: si vuelven más de
    `limite`, significa que hay más resultados de los que se muestran
    (evita que un "Total: 50" se confunda con el total real).
    """
    truncado = len(filas) > limite
    return filas[:limite], truncado


class ProductoCRUD:
    """Gestiona el acceso a la tabla productos (y, de forma acotada,
    a sucursales y precios para las operaciones que los necesitan)."""

    def __init__(self, conexion: ConexionBD):
        self.conexion = conexion

    # CRUD

    def crear(self, producto: Producto):
        sql = """
            INSERT INTO productos
                (id, marca, nombre, presentacion,
                 categoria_1, categoria_2, categoria_3)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        parametros = (
            producto.id,
            producto.marca,
            producto.nombre,
            producto.presentacion,
            producto.categoria_1,
            producto.categoria_2,
            producto.categoria_3,
        )

        return self.conexion.ejecutar_accion(sql, parametros)

    def obtener_por_id(self, producto_id):
        sql = "SELECT * FROM productos WHERE id = %s"

        filas = self.conexion.ejecutar_consulta(
            sql,
            (producto_id,)
        )

        return Producto.desde_fila(filas[0]) if filas else None

    def actualizar(self, producto: Producto):
        sql = """
            UPDATE productos
            SET marca = %s,
                nombre = %s,
                presentacion = %s,
                categoria_1 = %s,
                categoria_2 = %s,
                categoria_3 = %s
            WHERE id = %s
        """

        parametros = (
            producto.marca,
            producto.nombre,
            producto.presentacion,
            producto.categoria_1,
            producto.categoria_2,
            producto.categoria_3,
            producto.id,
        )

        return self.conexion.ejecutar_accion(sql, parametros)

    def eliminar(self, producto_id):
        """Elimina el producto y sus precios asociados en una única
        transacción: si falla el DELETE de productos, se revierte
        también el DELETE de precios (evita dejar precios huérfanos
        eliminados sin haber borrado el producto)."""

        return self.conexion.ejecutar_transaccion([
            (
                "DELETE FROM precios WHERE producto_id = %s",
                (producto_id,),
            ),
            (
                "DELETE FROM productos WHERE id = %s",
                (producto_id,),
            ),
        ])

    # Búsquedas

    def buscar_por_nombre(self, texto, limite=50):
        """Devuelve (productos, truncado). `truncado` es True si hay más
        resultados de los que se devuelven (más de `limite`)."""
        sql = """
            SELECT *
            FROM productos
            WHERE nombre LIKE %s
            ORDER BY nombre
            LIMIT %s
        """

        filas = self.conexion.ejecutar_consulta(
            sql,
            (f"%{texto}%", limite + 1)
        )
        filas, truncado = _dividir_truncado(filas, limite)

        return [Producto.desde_fila(fila) for fila in filas], truncado

    def buscar_por_categoria(self, categoria, limite=50):
        """Busca en las tres columnas de categoría (categoria_1/2/3),
        no solo en categoria_1. Devuelve (productos, truncado)."""
        sql = """
            SELECT *
            FROM productos
            WHERE categoria_1 = %s
               OR categoria_2 = %s
               OR categoria_3 = %s
            ORDER BY nombre
            LIMIT %s
        """

        filas = self.conexion.ejecutar_consulta(
            sql,
            (categoria, categoria, categoria, limite + 1)
        )
        filas, truncado = _dividir_truncado(filas, limite)

        return [Producto.desde_fila(fila) for fila in filas], truncado

    def listar_categorias(self):
        """Lista las categorías existentes combinando las tres columnas
        (categoria_1, categoria_2, categoria_3), sin duplicados."""
        sql = """
            SELECT categoria_1 AS categoria FROM productos
            WHERE categoria_1 IS NOT NULL AND categoria_1 <> ''
            UNION
            SELECT categoria_2 AS categoria FROM productos
            WHERE categoria_2 IS NOT NULL AND categoria_2 <> ''
            UNION
            SELECT categoria_3 AS categoria FROM productos
            WHERE categoria_3 IS NOT NULL AND categoria_3 <> ''
            ORDER BY categoria
        """

        filas = self.conexion.ejecutar_consulta(sql)

        return [fila["categoria"] for fila in filas]

    # Sucursales

    def obtener_sucursal(self, sucursal_id):
        sql = """
            SELECT id, comercio_id, bandera_id, bandera_descripcion,
                   comercio_razon_social, provincia, localidad, direccion,
                   lat, lng, sucursal_nombre, sucursal_tipo
            FROM sucursales
            WHERE id = %s
        """

        filas = self.conexion.ejecutar_consulta(sql, (sucursal_id,))

        return Sucursal.desde_fila(filas[0]) if filas else None

    def buscar_sucursales(self, texto, limite=20):
        sql = """
            SELECT id, comercio_id, bandera_id, bandera_descripcion,
                   comercio_razon_social, provincia, localidad, direccion,
                   lat, lng, sucursal_nombre, sucursal_tipo
            FROM sucursales
            WHERE bandera_descripcion LIKE %s
               OR sucursal_nombre LIKE %s
               OR localidad LIKE %s
            ORDER BY bandera_descripcion, sucursal_nombre
            LIMIT %s
        """

        patron = f"%{texto}%"

        filas = self.conexion.ejecutar_consulta(
            sql, (patron, patron, patron, limite)
        )

        return [Sucursal.desde_fila(fila) for fila in filas]

    # Precios

    def agregar_precio(self, producto_id, sucursal_id, precio):
        return self.crear_precio(Precio(producto_id, sucursal_id, precio))

    def crear_precio(self, precio: Precio):
        sql = """
            INSERT INTO precios (precio, producto_id, sucursal_id)
            VALUES (%s, %s, %s)
        """

        return self.conexion.ejecutar_accion(
            sql,
            (precio.precio, precio.producto_id, precio.sucursal_id)
        )

    # Vista de precios

    def listar_vista_precios(self, producto_id=None, limite=50):
        """Devuelve (filas, truncado) desde vista_precios_detalle."""
        if producto_id:
            sql = """
                SELECT *
                FROM vista_precios_detalle
                WHERE producto_id = %s
                LIMIT %s
            """

            parametros = (producto_id, limite + 1)

        else:
            sql = """
                SELECT *
                FROM vista_precios_detalle
                LIMIT %s
            """

            parametros = (limite + 1,)

        filas = self.conexion.ejecutar_consulta(sql, parametros)
        return _dividir_truncado(filas, limite)
