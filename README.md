# La Legión del Código

Proyecto de análisis de precios y comercios de Córdoba desarrollado para la Tecnicatura Superior en Ciencias de Datos e Inteligencia Artificial.

## Descripción

El proyecto utiliza archivos CSV con información sobre productos, precios y sucursales comerciales de Córdoba. Los datos son procesados y almacenados en una base de datos MySQL para realizar diferentes consultas y análisis mediante SQL.

## Tecnologías utilizadas

- Python
- Pandas
- MySQL
- MySQL Workbench
- SQL
- CSV

## Estructura del proyecto

```text
.
├── scripts/
│   ├── clean-up.py
│   └── update-columns.py
├── sql/
│   ├── 01_promedio_por_comercio.sql
│   ├── 02_maximo_por_categoria.sql
│   ├── 03_minimo_por_producto.sql
│   ├── 04_suma_por_comercio.sql
│   └── 05_diferencia_por_producto.sql
├── requirements.txt
└── README.md