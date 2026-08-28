USE datos_comercios;

SELECT
    categoria,
    MAX(precio) AS precio_maximo
FROM (
    
    SELECT
        p.categoria_1 AS categoria,
        pr.precio
    FROM productos p
    JOIN precios pr
        ON p.id = pr.producto_id
    WHERE p.categoria_1 IS NOT NULL
      AND p.categoria_1 <> ''

    UNION ALL

    SELECT
        p.categoria_2 AS categoria,
        pr.precio
    FROM productos p
    JOIN precios pr
        ON p.id = pr.producto_id
    WHERE p.categoria_2 IS NOT NULL
      AND p.categoria_2 <> ''

    UNION ALL

    SELECT
        p.categoria_3 AS categoria,
        pr.precio
    FROM productos p
    JOIN precios pr
        ON p.id = pr.producto_id
    WHERE p.categoria_3 IS NOT NULL
      AND p.categoria_3 <> ''

) AS categorias

GROUP BY categoria
ORDER BY precio_maximo DESC;
