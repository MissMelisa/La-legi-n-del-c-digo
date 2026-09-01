-- =========================================================
-- View: vista_precios_detalle
-- =========================================================

USE datos_comercios;

CREATE OR REPLACE VIEW vista_precios_detalle AS
SELECT
    p.id AS producto_id,
    p.nombre AS producto,
    p.marca,
    p.presentacion,
    p.categoria_1,
    p.categoria_2,
    p.categoria_3,
    pr.precio,
    s.id AS sucursal_id,
    s.sucursal_nombre,
    s.localidad,
    s.provincia
FROM precios pr
INNER JOIN productos p
    ON pr.producto_id = p.id
INNER JOIN sucursales s
    ON pr.sucursal_id = s.id;


SELECT *
FROM vista_precios_detalle
LIMIT 25;
