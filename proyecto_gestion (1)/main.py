#CRUD ESTUDIANTE ,DOCENTE 
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import (
    EstudianteController, DocenteController, MateriaController, MatriculaController
)


class MenuAcademico:
    def __init__(self):
        self.estudiantes = EstudianteController()
        self.docentes = DocenteController()
        self.materias = MateriaController(self.docentes)
        self.matriculas = MatriculaController(self.estudiantes, self.materias)

    def pausa(self):
        input("\nPresione Enter para continuar...")

    def pedir_entero(self, texto):
        try:
            return int(input(texto))
        except ValueError:
            return None

    def mostrar_resultado(self, exito, mensaje):
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)

    def ejecutar(self):
        while True:
            imprimir_titulo("SISTEMA DE GESTIÓN ACADÉMICA")
            print("  1. Estudiantes")
            print("  2. Docentes")
            print("  3. Materias")
            print("  4. Matrículas y Notas")
            print("  0. Salir\n")
            opcion = input("Opción: ").strip()

            if opcion == "1":
                self.menu_crud(self.estudiantes)
            elif opcion == "2":
                self.menu_crud(self.docentes)
            elif opcion == "3":
                self.menu_crud(self.materias)
            elif opcion == "4":
                self.menu_matriculas()
            elif opcion == "0":
                imprimir_info("¡Hasta luego! 👋")
                break
            else:
                imprimir_error("Opción no válida")
                self.pausa()

    def menu_crud(self, controlador):
        titulo = controlador.nombre.upper() + "S"
        while True:
            imprimir_titulo(titulo)
            print(f"  1. Crear {controlador.nombre}")
            print("  2. Ver todos")
            print("  3. Buscar")
            print("  4. Ver por id")
            print("  5. Actualizar")
            print("  6. Eliminar")
            print("  0. Volver\n")
            opcion = input("Opción: ").strip()

            if opcion == "1":
                self.crear(controlador)
            elif opcion == "2":
                self.ver_todos(controlador)
            elif opcion == "3":
                self.buscar(controlador)
            elif opcion == "4":
                self.ver_por_id(controlador)
            elif opcion == "5":
                self.actualizar(controlador)
            elif opcion == "6":
                self.eliminar(controlador)
            elif opcion == "0":
                break
            else:
                imprimir_error("Opción no válida")
                self.pausa()

    def crear(self, controlador):
        imprimir_titulo(f"CREAR {controlador.nombre.upper()}")
        print("Escribe 'cancelar' en cualquier campo para salir.\n")
        
        datos = {}
        for campo in controlador.campos:
            while True:
                valor = input(f"{campo.capitalize()}: ").strip()
                
                # Opción para cancelar y salir de la operación en curso
                if valor.lower() == "cancelar":
                    imprimir_info("Operación cancelada.")
                    self.pausa()
                    return

                # Validaciones específicas campo por campo
                try:
                    if campo in ("nombre", "apellido"):
                        if not valor:
                            imprimir_error(f"El {campo} es obligatorio. Intente de nuevo.")
                            continue
                        # Validar que no contenga números
                        if any(char.isdigit() for char in valor):
                            imprimir_error(f"El {campo} no puede contener números. Intente de nuevo.")
                            continue
                    elif campo == "email":
                        from models import Persona
                        if not Persona.es_email_valido(valor):
                            imprimir_error(f"Email inválido: '{valor}'. Intente de nuevo.")
                            continue
                    elif campo == "carnet":
                        if len(str(valor).strip()) < 4:
                            imprimir_error("El carnet debe tener al menos 4 caracteres. Intente de nuevo.")
                            continue

                    datos[campo] = valor
                    break
                except ValueError as err:
                    imprimir_error(str(err))

        exito, mensaje = controlador.crear(datos)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def ver_todos(self, controlador):
        imprimir_titulo(controlador.nombre.upper() + "S")
        lista = controlador.leer()
        if not lista:
            imprimir_info("No hay registros todavía.")
        else:
            for obj in lista:
                print(f"  {obj}")
            imprimir_info(f"Total: {len(lista)}")
        self.pausa()

    def buscar(self, controlador):
        imprimir_titulo(f"BUSCAR {controlador.nombre.upper()}")
        texto = input("Buscar: ")
        encontrados = controlador.buscar(texto)
        if not encontrados:
            imprimir_info(f"Sin coincidencias para '{texto}'.")
        else:
            for obj in encontrados:
                print(f"  {obj}")
        self.pausa()

    def ver_por_id(self, controlador):
        imprimir_titulo(f"VER {controlador.nombre.upper()}")
        id_reg = self.pedir_entero("Id: ")
        obj = controlador.obtener(id_reg)
        if not obj:
            imprimir_error("No encontrado")
        else:
            for clave, valor in obj.a_diccionario().items():
                print(f"  {clave.capitalize()}: {valor}")
        self.pausa()

    def actualizar(self, controlador):
        imprimir_titulo(f"ACTUALIZAR {controlador.nombre.upper()}")
        id_reg = self.pedir_entero("Id: ")
        obj = controlador.obtener(id_reg)
        if not obj:
            imprimir_error("No encontrado")
            self.pausa()
            return

        imprimir_info(f"Editando: {obj.etiqueta()}")
        print("Deje en blanco lo que no quiera cambiar (escriba 'cancelar' para salir).\n")
        cambios = {}
        for campo in controlador.campos:
            actual = getattr(obj, campo, "")
            nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
            if nuevo.lower() == "cancelar":
                imprimir_info("Operación cancelada.")
                self.pausa()
                return
            if nuevo != "":
                # Validación si actualiza nombre o apellido para que no lleven números
                if campo in ("nombre", "apellido") and any(char.isdigit() for char in nuevo):
                    imprimir_error(f"El {campo} no puede contener números. Se mantiene el valor anterior.")
                    continue
                cambios[campo] = nuevo

        exito, mensaje = controlador.actualizar(id_reg, cambios)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def eliminar(self, controlador):
        imprimir_titulo(f"ELIMINAR {controlador.nombre.upper()}")
        id_reg = self.pedir_entero("Id: ")
        obj = controlador.obtener(id_reg)
        if not obj:
            imprimir_error("No encontrado")
            self.pausa()
            return

        imprimir_info(f"Se eliminará: {obj.etiqueta()}")
        if confirmar("¿Confirma?"):
            exito, mensaje = controlador.eliminar(id_reg)
            self.mostrar_resultado(exito, mensaje)
        else:
            imprimir_info("Operación cancelada")
        self.pausa()

    def menu_matriculas(self):
        while True:
            imprimir_titulo("MATRÍCULAS Y CALIFICACIONES")
            print("  1. Registrar matrícula")
            print("  2. Ver todas las matrículas")
            print("  3. Agregar nota a una matrícula")
            print("  4. Ver boletín de estudiante")
            print("  5. Eliminar matrícula")
            print("  0. Volver\n")
            opcion = input("Opción: ").strip()

            if opcion == "1":
                self.crear_matricula()
            elif opcion == "2":
                self.ver_todos(self.matriculas)
            elif opcion == "3":
                self.agregar_nota_menu()
            elif opcion == "4":
                self.ver_boletin_menu()
            elif opcion == "5":
                self.eliminar(self.matriculas)
            elif opcion == "0":
                break
            else:
                imprimir_error("Opción no válida")
                self.pausa()

    def crear_matricula(self):
        imprimir_titulo("REGISTRAR MATRÍCULA")
        est_id = self.pedir_entero("Id del estudiante (o 0 para cancelar): ")
        if not est_id or est_id == 0:
            return
        mat_id = self.pedir_entero("Id de la materia (o 0 para cancelar): ")
        if not mat_id or mat_id == 0:
            return
        periodo = input("Periodo académico (ej. 2026-1): ").strip()
        
        exito, mensaje = self.matriculas.crear({
            "estudiante_id": est_id,
            "materia_id": mat_id,
            "periodo": periodo
        })
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def agregar_nota_menu(self):
        imprimir_titulo("AGREGAR CALIFICACIÓN")
        mat_id = self.pedir_entero("Id de la matrícula: ")
        if not mat_id:
            return
        print("Tipos permitidos: deber, lección, examen")
        tipo = input("Tipo de nota: ").strip()
        valor = input("Valor (0 a 20): ").strip()
        peso = input("Peso (por defecto 1): ").strip() or 1

        exito, mensaje = self.matriculas.agregar_nota(mat_id, tipo, valor, peso)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def ver_boletin_menu(self):
        imprimir_titulo("BOLETÍN DE CALIFICACIONES")
        est_id = self.pedir_entero("Id del estudiante: ")
        if not est_id:
            return
        boletin = self.matriculas.boletin(est_id)
        if not boletin:
            imprimir_error("Estudiante no encontrado o sin registros")
        else:
            print(boletin)
        self.pausa()


if __name__ == "__main__":
    try:
        MenuAcademico().ejecutar()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")