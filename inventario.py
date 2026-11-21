import csv
import os
from database import Database
from estructura_datos import Pila, Cola, buscar_en_lista

class Inventario:

    def __init__(self):
        self.db     = Database()
        self.pila   = Pila()
        self.cola   = Cola()

    def registrar(self):
        print("\n-- 1. Registrar Producto --")
        id_p = input("ID o codigo: ").strip()
        if not id_p:
            print("El ID no puede estar vacio.")
            return
        if self.db.obtener_uno(id_p):
            print("Ese ID ya esta registrado.")
            return
        nombre = input("Nombre: ").strip()
        desc   = input("Descripcion: ").strip()
        cat    = input("Categoria (ej. Abarrotes, Limpieza): ").strip()
        try:
            precio = float(input("Precio de venta ($): "))
            cant   = int(input("Cantidad inicial en almacen: "))
            minimo = int(input("Stock minimo (cuando hay muy poco): "))
        except ValueError:
            print("Los precios y cantidades deben ser numeros.")
            return
        if precio < 0 or cant < 0 or minimo < 0:
            print("Los valores no pueden ser negativos.")
            return
        p = {"id": id_p, "nombre": nombre, "descripcion": desc,
             "categoria": cat, "precio": precio, "cantidad": cant, "stock_minimo": minimo}
        self.db.insertar(p)
        self.pila.push(f"Alta: {nombre} (ID: {id_p})")
        print("Producto guardado correctamente.")

    def consultar(self):
        print("\n-- 2. Todos los Productos --")
        todos = self.db.obtener_todos()
        if not todos:
            print("El inventario esta vacio.")
            return
        print(f"\n{'ID':<10} {'Nombre':<22} {'Categoria':<15} {'Precio':>9} {'Cant.':>6} {'Min.':>5}")
        print("-" * 72)
        for p in todos:
            alerta = " << BAJO" if p["cantidad"] <= p["stock_minimo"] else ""
            print(f"{p['id']:<10} {p['nombre']:<22} {p['categoria']:<15} ${p['precio']:>8.2f} {p['cantidad']:>6} {p['stock_minimo']:>5}{alerta}")
        print(f"\nTotal: {len(todos)} producto(s)")

    def buscar(self):
        print("\n-- 3. Buscar Producto --")
        print("1. Buscar por ID exacto")
        print("2. Buscar por nombre")
        op = input("Opcion: ").strip()

        match op:
            case "1":
                id_p = input("ID: ").strip()
                p = self.db.obtener_uno(id_p)
                if p:
                    self._mostrar_detalle(p)
                else:
                    print("No se encontro ningun producto con ese ID.")

            case "2":
                texto = input("Nombre (o parte del nombre): ").strip()
                resultados = self.db.buscar_nombre(texto)
                if not resultados:
                    print("No se encontraron productos.")
                    return
                exacto = buscar_en_lista(resultados, texto)
                if exacto:
                    print("(Coincidencia exacta encontrada)")
                    self._mostrar_detalle(exacto)
                else:
                    print(f"\nSe encontraron {len(resultados)} producto(s):")
                    for p in resultados:
                        print(f"  {p['id']} | {p['nombre']} | ${p['precio']:.2f} | Cant: {p['cantidad']}")

            case _:
                print("Opcion no valida.")

    def _mostrar_detalle(self, p):
        print(f"\n  ID          : {p['id']}")
        print(f"  Nombre      : {p['nombre']}")
        print(f"  Descripcion : {p['descripcion']}")
        print(f"  Categoria   : {p['categoria']}")
        print(f"  Precio      : ${p['precio']:.2f}")
        print(f"  Cantidad    : {p['cantidad']}")
        print(f"  Stock min.  : {p['stock_minimo']}")

    def modificar(self):
        print("\n-- 4. Modificar Producto --")
        id_p = input("ID del producto a modificar: ").strip()
        p = self.db.obtener_uno(id_p)
        if not p:
            print("Producto no encontrado.")
            return
        print(f"Editando: {p['nombre']}. Deja vacio para no cambiar un campo.")

        n = input(f"Nombre [{p['nombre']}]: ").strip()
        if n: p["nombre"] = n

        d = input(f"Descripcion [{p['descripcion']}]: ").strip()
        if d: p["descripcion"] = d

        c = input(f"Categoria [{p['categoria']}]: ").strip()
        if c: p["categoria"] = c

        pr = input(f"Precio [${p['precio']:.2f}]: ").strip()
        if pr:
            try:
                val = float(pr)
                p["precio"] = val if val >= 0 else p["precio"]
            except ValueError:
                print("Precio invalido, no se cambio.")

        sm = input(f"Stock minimo [{p['stock_minimo']}]: ").strip()
        if sm:
            try:
                val = int(sm)
                p["stock_minimo"] = val if val >= 0 else p["stock_minimo"]
            except ValueError:
                print("Stock minimo invalido, no se cambio.")

        self.db.actualizar(p)
        self.pila.push(f"Modificacion: {p['nombre']}")
        print("Cambios guardados.")

    def eliminar(self):
        print("\n-- 5. Eliminar Producto --")
        id_p = input("ID del producto a eliminar: ").strip()
        p = self.db.obtener_uno(id_p)
        if not p:
            print("Producto no encontrado.")
            return
        conf = input(f"Seguro que quieres eliminar '{p['nombre']}'? (s/n): ").strip().lower()
        if conf == "s":
            self.db.eliminar(id_p)
            self.pila.push(f"Baja: {p['nombre']}")
            print("Producto eliminado.")
        else:
            print("Cancelado.")

    def entrada(self):
        print("\n-- 6. Entrada de Mercancia --")
        id_p = input("ID del producto: ").strip()
        p = self.db.obtener_uno(id_p)
        if not p:
            print("Producto no encontrado.")
            return
        try:
            cant = int(input(f"Cuantas unidades ingresan de '{p['nombre']}': "))
            if cant <= 0:
                print("La cantidad tiene que ser mayor a 0.")
                return
        except ValueError:
            print("Escribe un numero valido.")
            return
        p["cantidad"] += cant
        self.db.actualizar(p)
        self.db.guardar_movimiento(id_p, "ENTRADA", cant)
        self.pila.push(f"Entrada +{cant}: {p['nombre']}")
        print(f"Entrada registrada. Existencia nueva: {p['cantidad']} unidades.")

    def salida(self):
        print("\n-- 7. Salida de Mercancia --")
        id_p = input("ID del producto: ").strip()
        p = self.db.obtener_uno(id_p)
        if not p:
            print("Producto no encontrado.")
            return
        try:
            cant = int(input(f"Cuantas unidades salen de '{p['nombre']}' (hay {p['cantidad']}): "))
            if cant <= 0:
                print("La cantidad tiene que ser mayor a 0.")
                return
        except ValueError:
            print("Escribe un numero valido.")
            return
        if cant > p["cantidad"]:
            print(f"No hay suficiente stock. Solo hay {p['cantidad']} unidades.")
            return
        p["cantidad"] -= cant
        self.db.actualizar(p)
        self.db.guardar_movimiento(id_p, "SALIDA", cant)
        self.pila.push(f"Salida -{cant}: {p['nombre']}")
        if p["cantidad"] <= p["stock_minimo"]:
            self.cola.encolar(id_p)
            print(f"AVISO: '{p['nombre']}' tiene poco stock. Se agrego a la cola de resurtido.")
        print(f"Salida registrada. Existencia nueva: {p['cantidad']} unidades.")

    def stock_bajo(self):
        print("\n-- 8. Productos con Stock Bajo --")
        todos = self.db.obtener_todos()
        alertas = [p for p in todos if p["cantidad"] <= p["stock_minimo"]]
        if not alertas:
            print("Todo esta bien. Ningun producto tiene stock bajo.")
            return
        print(f"\nProductos que necesitan resurtido ({len(alertas)}):\n")
        print(f"{'ID':<10} {'Nombre':<22} {'Tiene':>7} {'Minimo':>8}")
        print("-" * 50)
        for p in alertas:
            print(f"{p['id']:<10} {p['nombre']:<22} {p['cantidad']:>7} {p['stock_minimo']:>8}")
            self.cola.encolar(p["id"])

    def reporte(self):
        print("\n-- 9. Reporte del Inventario --")
        todos = self.db.obtener_todos()
        if not todos:
            print("Sin datos.")
            return
        total_prod  = len(todos)
        total_units = sum(p["cantidad"] for p in todos)
        valor_total = sum(p["cantidad"] * p["precio"] for p in todos)
        en_alerta   = sum(1 for p in todos if p["cantidad"] <= p["stock_minimo"])

        print(f"\n  Productos registrados  : {total_prod}")
        print(f"  Unidades totales       : {total_units}")
        print(f"  Valor del inventario   : ${valor_total:.2f}")
        print(f"  Productos en alerta    : {en_alerta}")
        print(f"  Ultimo mov. (pila)     : {self.pila.ver_cima() or 'Sin movimientos en esta sesion'}")
        print(f"  En cola de resurtido   : {self.cola.tamanio()} producto(s)")

        movs = self.db.obtener_movimientos()
        if movs:
            print("\n  Ultimos 15 movimientos:")
            print(f"  {'#':<5} {'Nombre':<22} {'Tipo':<10} {'Cant':>5}  Fecha")
            print("  " + "-" * 60)
            for m in movs:
                print(f"  {m['id_mov']:<5} {m['nombre']:<22} {m['tipo']:<10} {m['cantidad']:>5}  {m['fecha']}")

    def ver_cola(self):
        print("\n-- Cola de Resurtido (FIFO) --")
        if self.cola.esta_vacia():
            print("No hay productos pendientes de resurtir.")
            return
        print(f"Productos en cola ({self.cola.tamanio()}):")
        for i, id_p in enumerate(self.cola.elementos):
            p = self.db.obtener_uno(id_p)
            nombre = p["nombre"] if p else id_p
            print(f"  {i+1}. {nombre} (ID: {id_p})")
        if input("\nMarcar el primero como atendido? (s/n): ").strip().lower() == "s":
            atendido = self.cola.desencolar()
            p = self.db.obtener_uno(atendido)
            print(f"'{p['nombre'] if p else atendido}' removido de la cola.")

    def exportar_csv(self):
        todos = self.db.obtener_todos()
        if not todos:
            print("No hay productos para exportar.")
            return
        archivo = "inventario_exportado.csv"
        campos = ["id", "nombre", "descripcion", "categoria", "precio", "cantidad", "stock_minimo"]
        with open(archivo, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            w.writerows(todos)
        print(f"Exportado a '{archivo}' ({len(todos)} productos).")

    def importar_csv(self):
        archivo = input("Nombre del archivo CSV: ").strip()
        if not os.path.exists(archivo):
            print("El archivo no existe.")
            return
        agregados = 0
        omitidos  = 0
        errores   = 0
        with open(archivo, newline="", encoding="utf-8") as f:
            for numero_fila, fila in enumerate(csv.DictReader(f), start=2):
                if self.db.obtener_uno(fila.get("id", "").strip()):
                    omitidos += 1
                    continue
                try:
                    p = {
                        "id":          fila["id"].strip(),
                        "nombre":      fila["nombre"].strip(),
                        "descripcion": fila.get("descripcion", "").strip(),
                        "categoria":   fila.get("categoria", "").strip(),
                        "precio":      float(fila["precio"]),
                        "cantidad":    int(fila["cantidad"]),
                        "stock_minimo":int(fila["stock_minimo"])
                    }
                    if not p["id"] or not p["nombre"]:
                        raise ValueError("ID o nombre vacios")
                    if p["precio"] < 0 or p["cantidad"] < 0 or p["stock_minimo"] < 0:
                        raise ValueError("Valores negativos no permitidos")
                except (ValueError, KeyError) as e:
                    print(f"  [Fila {numero_fila}] Omitida por dato invalido: {e}")
                    errores += 1
                    continue
                self.db.insertar(p)
                agregados += 1
        print(f"Importacion lista: {agregados} nuevos, {omitidos} omitidos por ID repetido, {errores} fila(s) con errores de formato.")


    def gestionar_usuarios(self):
        while True:
            print("\n-- Gestion de Usuarios --")
            print("1. Ver todos los usuarios")
            print("2. Dar de alta un usuario")
            print("3. Eliminar un usuario")
            print("0. Volver al menu")

            match input("Opcion: ").strip():
                case "1":
                    usuarios = self.db.obtener_todos_usuarios()
                    if not usuarios:
                        print("No hay usuarios registrados.")
                    else:
                        print(f"\n{'Usuario':<15} {'Rol':<20}")
                        print("-" * 35)
                        for u in usuarios:
                            print(f"{u['usuario']:<15} {u['rol']:<20}")

                case "2":
                    nuevo = input("Nombre de usuario: ").strip()
                    if not nuevo:
                        print("El nombre no puede estar vacio.")
                        continue
                    if self.db.obtener_usuario(nuevo):
                        print("Ese usuario ya existe.")
                        continue
                    password = input("Contrasena: ").strip()
                    if not password:
                        print("La contrasena no puede estar vacia.")
                        continue
                    print("Roles disponibles:")
                    print("  1. Gerente")
                    print("  2. Almacen")
                    print("  3. Administrador")
                    match input("Rol (1/2/3): ").strip():
                        case "1": rol = "Gerente"
                        case "2": rol = "Almacen"
                        case "3": rol = "Administrador"
                        case _:
                            print("Rol no valido, se asigno Administrador por defecto.")
                            rol = "Administrador"
                    self.db.insertar_usuario({"usuario": nuevo, "password": password, "rol": rol})
                    print(f"Usuario '{nuevo}' creado con rol {rol}.")

                case "3":
                    usuario = input("Nombre del usuario a eliminar: ").strip()
                    if usuario in ("gerente", "almacen", "admin"):
                        print("No se pueden eliminar los usuarios del sistema.")
                        continue
                    if not self.db.obtener_usuario(usuario):
                        print("Ese usuario no existe.")
                        continue
                    if input(f"Eliminar al usuario '{usuario}'? (s/n): ").lower() == "s":
                        self.db.eliminar_usuario(usuario)
                        print("Usuario eliminado.")

                case "0":
                    break
                case _:
                    print("Opcion no valida.")
