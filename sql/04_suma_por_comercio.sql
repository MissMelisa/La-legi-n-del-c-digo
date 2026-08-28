USE datos_comercios;

SELECT
    s.comercio_razon_social AS comercio,
    ROUND(SUM(pr.precio), 2) AS suma_precios
FROM precios pr
JOIN sucursales s
    ON pr.sucursal_id = s.id
GROUP BY s.comercio_razon_social
ORDER BY suma_precios DESC;