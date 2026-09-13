from conexion import ConexionBD

#insertar llamada al menu()

def delete_producto():

    try:
        bd = ConexionBD()

        bd.conectar()

        identificador = int(input("Ingrese el identificador del producto a eliminar: "))

        query_verificar_existencia = "SELECT id FROM productos WHERE id = %s"

        resultado = bd.ejecutar_consulta(query_verificar_existencia,(identificador,))

        if not resultado:
            print("El producto no existe")
            return

        confirmacion = input("¿Confirma que desea eliminar el producto? También se eliminarán sus precios (s/n): ")

        if confirmacion.lower() != 's':
            print("Operación cancelada")
            return

        query_eliminar_precios = "DELETE FROM precios WHERE producto_id = %s"

        bd.ejecutar_accion(query_eliminar_precios,(identificador,))

        query_eliminar_producto = "DELETE FROM productos WHERE id = %s"

        bd.ejecutar_accion(query_eliminar_producto,(identificador,))

        print("Producto eliminado correctamente")

    finally:
        bd.cerrar()
