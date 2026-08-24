import pandas as pd
from pathlib import Path

dataset_path = Path("/Users/riosmelisa/Desktop/dataset")

column_mappings = {
    "productos.csv": {
        "id": "id",
        "marca": "marca",
        "nombre": "nombre",
        "presentacion": "presentacion",
        "categoria1": "categoria_1",
        "categoria2": "categoria_2",
        "categoria3": "categoria_3",
    },
    "precios.csv": {
        "precio": "precio",
        "producto_id": "producto_id",
        "sucursal_id": "sucursal_id",
    },
    "sucursales_cordoba.csv": {
        "id": "id",
        "comercioid": "comercio_id",
        "banderaid": "bandera_id",
        "banderadescripcion": "bandera_descripcion",
        "comerciorazonsocial": "comercio_razon_social",
        "provincia": "provincia",
        "localidad": "localidad",
        "direccion": "direccion",
        "lat": "lat",
        "lng": "lng",
        "sucursalnombre": "sucursal_nombre",
        "sucursaltipo": "sucursal_tipo",
    },
}

for file_name, mapping in column_mappings.items():
    file_path = dataset_path / file_name

    df = pd.read_csv(file_path, encoding="utf-8")

    df.rename(columns=mapping, inplace=True)

    df.to_csv(
        file_path,
        index=False,
        encoding="utf-8",
    )

    print(f"{file_name}:")
    print(df.columns.tolist())
    print()

    