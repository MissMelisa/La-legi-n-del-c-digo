from conexion import ConexionBD
from producto import Producto


class ProductoCRUD:
    """Gestiona el acceso a la tabla productos."""

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
        """Elimina primero los precios relacionados."""

        self.conexion.ejecutar_accion(
            "DELETE FROM precios WHERE producto_id = %s",
            (producto_id,)
        )

        return self.conexion.ejecutar_accion(
            "DELETE FROM productos WHERE id = %s",
            (producto_id,)
        )

    # Búsquedas

    def buscar_por_nombre(self, texto, limite=50):
        sql = """
            SELECT *
            FROM productos
            WHERE nombre LIKE %s
            ORDER BY nombre
            LIMIT %s
        """

        filas = self.conexion.ejecutar_consulta(
            sql,
            (f"%{texto}%", limite)
        )

        return [Producto.desde_fila(fila) for fila in filas]

    def buscar_por_categoria(self, categoria, limite=50):
        sql = """
            SELECT *
            FROM productos
            WHERE categoria_1 = %s
            ORDER BY nombre
            LIMIT %s
        """

        filas = self.conexion.ejecutar_consulta(
            sql,
            (categoria, limite)
        )

        return [Producto.desde_fila(fila) for fila in filas]

    def listar_categorias(self):
        sql = """
            SELECT DISTINCT categoria_1
            FROM productos
            WHERE categoria_1 IS NOT NULL
              AND categoria_1 <> ''
            ORDER BY categoria_1
        """

        filas = self.conexion.ejecutar_consulta(sql)

        return [
            fila["categoria_1"]
            for fila in filas
        ]

    # Vista de precios

    def listar_vista_precios(self, producto_id=None, limite=50):
        if producto_id:
            sql = """
                SELECT *
                FROM vista_precios_detalle
                WHERE producto_id = %s
                LIMIT %s
            """

            parametros = (producto_id, limite)

        else:
            sql = """
                SELECT *
                FROM vista_precios_detalle
                LIMIT %s
            """

            parametros = (limite,)

        return self.conexion.ejecutar_consulta(
            sql,
            parametros
        )