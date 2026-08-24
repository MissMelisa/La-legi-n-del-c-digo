USE datos_comercios;

SELECT
    s.comercio_razon_social AS comercio,
    ROUND(AVG(pr.precio), 2) AS precio_promedio
FROM precios pr
JOIN sucursales s
    ON pr.sucursal_id = s.id
GROUP BY s.comercio_razon_social
ORDER BY precio_promedio DESC;