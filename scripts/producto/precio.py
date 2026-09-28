"""
Clase Precio (POO): representa un registro de la tabla `precios`,
la tabla asociativa entre `productos` y `sucursales`
(cada fila es el precio de un producto en una sucursal puntual).
"""


class Precio:
    """Representa el precio de un producto en una sucursal (tabla `precios`)."""

    def __init__(self, producto_id, sucursal_id, precio):
        self.producto_id = producto_id
        self.sucursal_id = sucursal_id
        self.precio = precio

    def __str__(self):
        return f"Producto {self.producto_id} en sucursal {self.sucursal_id}: ${self.precio}"

    @classmethod
    def desde_fila(cls, fila):
        """Crea un Precio a partir de una fila (dict) devuelta por la BD."""
        return cls(
            producto_id=fila["producto_id"],
            sucursal_id=fila["sucursal_id"],
            precio=fila.get("precio"),
        )
