# Diseño de la base de datos

## 1. Descripción

La base de datos `datos_comercios` fue diseñada para almacenar y analizar información sobre productos, precios y sucursales comerciales de la provincia de Córdoba.

Los datos originales provienen de archivos CSV y fueron previamente procesados para:

- Conservar únicamente las sucursales de Córdoba.
- Identificar Córdoba mediante el código de provincia `AR-X`.
- Normalizar los nombres de las columnas utilizando `snake_case`.
- Mantener los identificadores originales de productos y sucursales.

La base de datos está compuesta por tres tablas:

- `productos`
- `sucursales`
- `precios`

---

## 2. Modelo relacional

La estructura de la base de datos es:

```text
productos 1 ───────── N precios N ───────── 1 sucursales