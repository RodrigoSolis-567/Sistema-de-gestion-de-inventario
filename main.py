from database import Database
from inventario import Inventario

def login(db):
    print("=" * 40)
    print("   SISTEMA DE CONTROL DE INVENTARIOS")
    print("   Abarrotes Los Lobos")
    print("=" * 40)
    for _ in range(3):
        usuario  = input("Usuario: ")
        password = input("Contrasena: ")
        u = db.obtener_usuario(usuario)
        if u and u["password"] == password:
            print(f"\nBienvenido {usuario} | Rol: {u['rol']}\n")
            return u["rol"]
        print("Datos incorrectos, intenta de nuevo.")
    print("Demasiados intentos fallidos.")
    return None

def menu_gerente(inv):
    while True:
        print("\n" + "=" * 40)
        print("     MENU - GERENTE")
        print("=" * 40)
        print(" 1.  Registrar producto")
        print(" 2.  Consultar todos los productos")
        print(" 3.  Buscar producto")
        print(" 4.  Modificar producto")
        print(" 5.  Eliminar producto")
        print(" 6.  Entrada de mercancia")
        print(" 7.  Salida de mercancia")
        print(" 8.  Detectar stock bajo")
        print(" 9.  Reporte general")
        print(" 10. Exportar a CSV")
        print(" 11. Importar desde CSV")
        print(" 12. Cola de resurtido")
        print(" 13. Gestion de usuarios")
        print("  0. Cerrar Sesion")

        match input("\nOpcion: ").strip():
            case "1":  inv.registrar()
            case "2":  inv.consultar()
            case "3":  inv.buscar()
            case "4":  inv.modificar()
            case "5":  inv.eliminar()
            case "6":  inv.entrada()
            case "7":  inv.salida()
            case "8":  inv.stock_bajo()
            case "9":  inv.reporte()
            case "10": inv.exportar_csv()
            case "11": inv.importar_csv()
            case "12": inv.ver_cola()
            case "13": inv.gestionar_usuarios()
            case "0":
                print("Sesion cerrada. Volviendo al inicio de sesion...\n")
                return True
            case _:
                print("Opcion no valida.")

def menu_almacen(inv):
    while True:
        print("\n" + "=" * 40)
        print("     MENU - ENCARGADO DE ALMACEN")
        print("=" * 40)
        print(" 1. Entrada de mercancia")
        print(" 2. Salida de mercancia")
        print(" 3. Consultar stock bajo")
        print(" 4. Cola de resurtido")
        print(" 0. Cerrar Sesion")

        match input("\nOpcion: ").strip():
            case "1": inv.entrada()
            case "2": inv.salida()
            case "3": inv.stock_bajo()
            case "4": inv.ver_cola()
            case "0":
                print("Sesion cerrada. Volviendo al inicio de sesion...\n")
                return True
            case _:
                print("Opcion no valida.")

def menu_admin(inv):
    while True:
        print("\n" + "=" * 40)
        print("     MENU - ADMINISTRADOR")
        print("=" * 40)
        print(" 1. Consultar todos los productos")
        print(" 2. Buscar producto")
        print(" 3. Detectar stock bajo")
        print(" 4. Reporte general")
        print(" 5. Exportar a CSV")
        print(" 0. Cerrar Sesion")

        match input("\nOpcion: ").strip():
            case "1": inv.consultar()
            case "2": inv.buscar()
            case "3": inv.stock_bajo()
            case "4": inv.reporte()
            case "5": inv.exportar_csv()
            case "0":
                print("Sesion cerrada. Volviendo al inicio de sesion...\n")
                return True
            case _:
                print("Opcion no valida.")

if __name__ == "__main__":
    db = Database()
    db.iniciar()

    while True:
        rol = login(db)
        if not rol:
            print("Acceso denegado. Cerrando el sistema.")
            break

        inv = Inventario()
        match rol:
            case "Gerente":       continuar = menu_gerente(inv)
            case "Almacen":       continuar = menu_almacen(inv)
            case "Administrador": continuar = menu_admin(inv)
            case _:               continuar = False

        if not continuar:
            print("Hasta luego.")
            break
