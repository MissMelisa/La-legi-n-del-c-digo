USE datos_comercios;

SELECT
    p.nombre AS producto,
    MIN(pr.precio) AS precio_minimo,
    MAX(pr.precio) AS precio_maximo,
    ROUND(MAX(pr.precio) - MIN(pr.precio), 2) AS diferencia
FROM productos p
JOIN precios pr
    ON p.id = pr.producto_id
GROUP BY
    p.id,
    p.nombre
ORDER BY diferencia DESC;