from conexion import ConexionBD


def obtener_por_id(producto_id):
    """Busca un producto por su id y devuelve el dict, o None si no existe."""
    bd = ConexionBD()

    try:
        bd.conectar()

        # %s es el placeholder que PyMySQL reemplaza por el id (evita inyeccion SQL)
        query = "SELECT * FROM productos WHERE id = %s"

        resultado = bd.ejecutar_consulta(query, (producto_id,))

        if not resultado:
            return None

        return resultado[0]

    finally:
        bd.cerrar()


def buscar_por_nombre(texto, limite=20):
    """Busca productos cuyo nombre contenga `texto`. Devuelve hasta `limite` filas."""
    bd = ConexionBD()

    try:
        bd.conectar()

        # LIKE %texto% = coincidencia parcial en cualquier parte del nombre
        query = "SELECT * FROM productos WHERE nombre LIKE %s LIMIT %s"

        resultado = bd.ejecutar_consulta(query, (f"%{texto}%", limite))

        return resultado

    finally:
        bd.cerrar()


def buscar_por_categoria(categoria, limite=20):
    """Busca productos por categoria (busca en categoria_1/2/3)."""
    bd = ConexionBD()

    try:
        bd.conectar()

        # OR: alcanza con que la categoria aparezca en cualquiera de los 3 niveles
        query = (
            "SELECT * FROM productos "
            "WHERE categoria_1 LIKE %s OR categoria_2 LIKE %s "
            "OR categoria_3 LIKE %s "
            "LIMIT %s"
        )

        patron = f"%{categoria}%"

        resultado = bd.ejecutar_consulta(
            query,
            (patron, patron, patron, limite),
        )

        return resultado

    finally:
        bd.cerrar()


def listar_categorias():
    """Devuelve la lista de categorias unicas de nivel 1, ordenadas alfabeticamente."""
    bd = ConexionBD()

    try:
        bd.conectar()

        # DISTINCT: categorias sin repetir. Se descartan las vacias o NULL
        query = (
            "SELECT DISTINCT categoria_1 "
            "FROM productos "
            "WHERE categoria_1 IS NOT NULL AND categoria_1 <> '' "
            "ORDER BY categoria_1"
        )

        resultado = bd.ejecutar_consulta(query)

        # Cada fila es un dict; nos quedamos solo con el valor de categoria_1
        return [fila["categoria_1"] for fila in resultado]

    finally:
        bd.cerrar()