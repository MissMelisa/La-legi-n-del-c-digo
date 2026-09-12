from conexion import ConexionBD

#insertar llamada al menu()

def update_producto():

    try:
        bd = ConexionBD()

        bd.conectar()

        identificador = int(input("Ingrese el identificador del producto a modificar: "))

        query_verificar_existencia = "SELECT id FROM productos WHERE id = %s"

        resultado = bd.ejecutar_consulta(query_verificar_existencia,(identificador,))

        if not resultado:
            print("El producto no existe")
            return

        while True:
            print("-------------")
            print("1. Marca")
            print("2. Nombre")
            print("3. Presentación")
            print("4. Categoría")

            opcion_ingresada = int(input("Ingrese el número del dato que quiere actualizar: "))

            if opcion_ingresada == 1:
                campo_a_actualizar = 'marca'
                valor_actualizar = input('Ingrese la nueva marca: ')

            elif opcion_ingresada == 2:
                campo_a_actualizar = 'nombre'
                valor_actualizar = input('Ingrese el nuevo nombre: ')

            elif opcion_ingresada == 3:
                campo_a_actualizar = 'presentacion'
                valor_actualizar = input('Ingrese la nueva presentación: ')

            elif opcion_ingresada == 4:

                while True:
                    numero_categoria = int(input('Ingrese el nivel de categoría que quiere actualizar (1/2/3): '))

                    if numero_categoria == 1:
                        campo_a_actualizar = 'categoria_1'
                        valor_actualizar = input('Ingrese la nueva categoria: ')
                        break

                    elif numero_categoria == 2:
                        campo_a_actualizar = 'categoria_2'
                        valor_actualizar = input('Ingrese la nueva categoria: ')
                        break

                    elif numero_categoria == 3:
                        campo_a_actualizar = 'categoria_3'
                        valor_actualizar = input('Ingrese la nueva categoria: ')
                        break

                    else:
                        print("Opción inválida. Debe ingresar 1, 2 o 3.")

            else:
                print("Opción inválida. Debe ingresar 1, 2, 3 o 4.")
                continue

            query_para_actualizar = f"UPDATE productos SET {campo_a_actualizar} = %s WHERE id = %s"

            bd.ejecutar_accion(query_para_actualizar,(valor_actualizar,identificador))

            print("Producto actualizado correctamente")

    finally:
        bd.cerrar()