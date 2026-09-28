"""
Clase Producto (POO): representa un registro de la tabla `productos`.

Esta clase es solo una entidad de datos (no accede a la base de datos:
eso es responsabilidad exclusiva de ProductoCRUD, para evitar la
dependencia circular Producto <-> ProductoCRUD).
"""


class Producto:
    """Representa un producto del dataset (tabla `productos`)."""

    def __init__(self, id, marca="", nombre="", presentacion="",
                 categoria_1="", categoria_2="", categoria_3=""):
        self.id = id
        self.marca = marca
        self.nombre = nombre
        self.presentacion = presentacion
        self.categoria_1 = categoria_1
        self.categoria_2 = categoria_2
        self.categoria_3 = categoria_3

    def __str__(self):
        categorias = "/".join(
            c for c in (self.categoria_1, self.categoria_2, self.categoria_3) if c
        )
        return (
            f"[{self.id}] {self.nombre} ({self.marca}) - {self.presentacion}"
            + (f" | {categorias}" if categorias else "")
        )

    @classmethod
    def desde_fila(cls, fila):
        """Crea un Producto a partir de una fila (dict) devuelta por la BD."""
        return cls(
            id=fila["id"],
            marca=fila.get("marca") or "",
            nombre=fila.get("nombre") or "",
            presentacion=fila.get("presentacion") or "",
            categoria_1=fila.get("categoria_1") or "",
            categoria_2=fila.get("categoria_2") or "",
            categoria_3=fila.get("categoria_3") or "",
        )


