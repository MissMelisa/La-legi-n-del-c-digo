from conexion import ConexionBD


class ProductoCRUD:

    @staticmethod
    def crear(producto):
        """Inserta un producto nuevo. `producto` es un dict con claves:
        id, marca, nombre, presentacion, categoria_1/2/3.
        Devuelve la cantidad de filas insertadas, o None si el id ya existe."""

        bd = ConexionBD()

        try:
            bd.conectar()

            # Verificamos antes si el id ya esta en la tabla (la PK no admite duplicados)
            query_verificar_existencia = "SELECT id FROM productos WHERE id = %s"

            existe = bd.ejecutar_consulta(
                query_verificar_existencia,
                (producto["id"],),
            )

            if existe:
                print(f"El producto {producto['id']} ya existe")
                return None

            # INSERT con placeholders %s, uno por columna de la tabla productos
            query_insertar = (
                "INSERT INTO productos "
                "(id, marca, nombre, presentacion, "
                "categoria_1, categoria_2, categoria_3) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            )

            # get() permite campos opcionales (None si no vienen en el dict)
            valores = (
                producto["id"],
                producto.get("marca"),
                producto.get("nombre"),
                producto.get("presentacion"),
                producto.get("categoria_1"),
                producto.get("categoria_2"),
                producto.get("categoria_3"),
            )

            filas_afectadas = bd.ejecutar_accion(query_insertar, valores)

            print("Producto creado correctamente")

            return filas_afectadas

        finally:
            bd.cerrar()