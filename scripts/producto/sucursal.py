"""
Clase Sucursal (POO): representa un registro de la tabla `sucursales`
(comercios y sucursales de Córdoba).
"""


class Sucursal:
    """Representa una sucursal comercial del dataset (tabla `sucursales`)."""

    def __init__(self, id, comercio_id=None, bandera_id=None,
                 bandera_descripcion="", comercio_razon_social="",
                 provincia="", localidad="", direccion="",
                 lat=None, lng=None, sucursal_nombre="", sucursal_tipo=""):
        self.id = id
        self.comercio_id = comercio_id
        self.bandera_id = bandera_id
        self.bandera_descripcion = bandera_descripcion
        self.comercio_razon_social = comercio_razon_social
        self.provincia = provincia
        self.localidad = localidad
        self.direccion = direccion
        self.lat = lat
        self.lng = lng
        self.sucursal_nombre = sucursal_nombre
        self.sucursal_tipo = sucursal_tipo

    def __str__(self):
        return (
            f"[{self.id}] {self.bandera_descripcion} - {self.sucursal_nombre} "
            f"| {self.localidad} ({self.provincia})"
        )

    @classmethod
    def desde_fila(cls, fila):
        """Crea una Sucursal a partir de una fila (dict) devuelta por la BD."""
        return cls(
            id=fila["id"],
            comercio_id=fila.get("comercio_id"),
            bandera_id=fila.get("bandera_id"),
            bandera_descripcion=fila.get("bandera_descripcion") or "",
            comercio_razon_social=fila.get("comercio_razon_social") or "",
            provincia=fila.get("provincia") or "",
            localidad=fila.get("localidad") or "",
            direccion=fila.get("direccion") or "",
            lat=fila.get("lat"),
            lng=fila.get("lng"),
            sucursal_nombre=fila.get("sucursal_nombre") or "",
            sucursal_tipo=fila.get("sucursal_tipo") or "",
        )
