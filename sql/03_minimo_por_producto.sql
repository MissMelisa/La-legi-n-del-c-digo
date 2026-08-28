USE datos_comercios;

SELECT
    p.nombre AS producto,
    MIN(pr.precio) AS precio_minimo,
    s.comercio_razon_social AS comercio
FROM productos p
JOIN precios pr
    ON p.id = pr.producto_id
JOIN sucursales s
    ON pr.sucursal_id = s.id
WHERE pr.precio = (
    SELECT MIN(pr2.precio)
    FROM precios pr2
    WHERE pr2.producto_id = p.id
)
GROUP BY
    p.id,
    p.nombre,
    s.comercio_razon_social
ORDER BY p.nombre;