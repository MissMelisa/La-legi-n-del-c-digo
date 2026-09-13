from CRUD.delete_product import delete_product

print("MENU INTERACTIVO DE LA APLICACION")
print("==================================================")

opcion = 0;

while opcion != 5:
    print("1. Ingresar nuevo producto")
    print("2. Modificar producto")
    print("3. Eliminar producto")
    print("4. Buscar producto")
    print("5. Salir")
    print("==================================================")
    try:
        opcion = int(input("Ingrese una opcion: "))
    except ValueError:
        print("Opcion no valida")
        continue
    print("==================================================")
    match opcion:
        case 1:
            """ LLAMADA A METODO PARA INGRESAR NUEVO PRODUCTO """
        case 2:
            """ LLAMADA A METODO PARA MODIFICAR PRODUCTO """
        case 3:
            delete_product()
        case 4:
            """ LLAMADA A METODO PARA BUSCAR PRODUCTO """
        case 5:
            """ SALIDA DEL MENU """
            break;
        case _:
            print("Opcion no valida")

print("==================================================") 
print("Gracias por usar la aplicacion")
print("==================================================")