from abc import ABC, abstractmethod
from models import Estudiante, Docente, Materia, Matricula
from shared.json_manager import GestorJSON


class CrudBase(ABC):
    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


class EstudianteController(CrudBase):
    def __init__(self, archivo="data/estudiantes.json"):
        self.nombre = "estudiante"
        self.campos = Estudiante.CAMPOS
        self.gestor = GestorJSON(archivo)
        self.lista = [Estudiante.desde_diccionario(d) for d in self.gestor.leer()]

    def guardar(self):
        self.gestor.guardar([e.a_diccionario() for e in self.lista])

    def obtener(self, id_reg):
        return next((e for e in self.lista if e.id == id_reg), None)

    def leer(self):
        return self.lista

    def buscar(self, texto):
        t = texto.strip().lower()
        if not t:
            return []
        return [e for e in self.lista if t in e.nombre.lower() or t in e.apellido.lower() or t in e.email or t in e.carnet.lower()]

    def siguiente(self):
        return (max((e.id for e in self.lista), default=0)) + 1

    def crear(self, datos):
        carnet = str(datos.get("carnet", "")).strip().upper()
        email = str(datos.get("email", "")).strip().lower()
        for e in self.lista:
            if e.carnet == carnet:
                return False, f"El carnet {carnet} ya está registrado"
            if e.email == email:
                return False, f"El email {email} ya está registrado"
        try:
            est = Estudiante(
                self.siguiente(),
                datos.get("nombre", ""),
                datos.get("apellido", ""),
                email,
                carnet,
            )
        except ValueError as err:
            return False, str(err)
        self.lista.append(est)
        self.guardar()
        return True, f"Estudiante creado: {est.etiqueta()}"

    def actualizar(self, id_reg, datos):
        est = self.obtener(id_reg)
        if not est:
            return False, f"No existe estudiante con id {id_reg}"
        
        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            for otro in self.lista:
                if otro.email == email and otro.id != id_reg:
                    return False, "Ese email ya está registrado"

        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().upper()
            for otro in self.lista:
                if otro.carnet == carnet and otro.id != id_reg:
                    return False, "Ese carnet ya está registrado"

        try:
            nuevo = Estudiante(
                est.id,
                datos.get("nombre", est.nombre),
                datos.get("apellido", est.apellido),
                datos.get("email", est.email),
                datos.get("carnet", est.carnet),
            )
        except ValueError as err:
            return False, str(err)
        pos = self.lista.index(est)
        self.lista[pos] = nuevo
        self.guardar()
        return True, f"Estudiante {id_reg} actualizado"

    def eliminar(self, id_reg):
        est = self.obtener(id_reg)
        if not est:
            return False, f"No existe estudiante con id {id_reg}"
        self.lista.remove(est)
        self.guardar()
        return True, f"Estudiante {id_reg} eliminado"


class DocenteController(CrudBase):
    def __init__(self, archivo="data/docentes.json"):
        self.nombre = "docente"
        self.campos = Docente.CAMPOS
        self.gestor = GestorJSON(archivo)
        self.lista = [Docente.desde_diccionario(d) for d in self.gestor.leer()]

    def guardar(self):
        self.gestor.guardar([d.a_diccionario() for d in self.lista])

    def obtener(self, id_reg):
        return next((d for d in self.lista if d.id == id_reg), None)

    def leer(self):
        return self.lista

    def buscar(self, texto):
        t = texto.strip().lower()
        if not t:
            return []
        return [d for d in self.lista if t in d.nombre.lower() or t in d.apellido.lower() or t in d.email or t in d.especialidad.lower()]

    def siguiente(self):
        return (max((d.id for d in self.lista), default=0)) + 1

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = [c for c in Docente.OBLIGATORIOS if not str(datos.get(c, "")).strip()]
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"
        
        email = str(datos.get("email", "")).strip().lower()
        if email:
            for otro in self.lista:
                if otro.email == email and otro.id != id_actual:
                    return "Ese email ya está registrado"
        return None

    def crear(self, datos):
        error_val = self.validar(datos)
        if error_val:
            return False, error_val

        email = str(datos.get("email", "")).strip().lower()
        try:
            doc = Docente(
                self.siguiente(),
                datos.get("nombre", ""),
                datos.get("apellido", ""),
                email,
                datos.get("titulo", ""),
                datos.get("especialidad", ""),
            )
        except ValueError as err:
            return False, str(err)
        self.lista.append(doc)
        self.guardar()
        return True, f"Docente creado: {doc.etiqueta()}"

    def actualizar(self, id_reg, datos):
        doc = self.obtener(id_reg)
        if not doc:
            return False, f"No existe docente con id {id_reg}"

        error_val = self.validar(datos, id_actual=id_reg)
        if error_val:
            return False, error_val

        try:
            nuevo = Docente(
                doc.id,
                datos.get("nombre", doc.nombre),
                datos.get("apellido", doc.apellido),
                datos.get("email", doc.email),
                datos.get("titulo", doc.titulo),
                datos.get("especialidad", doc.especialidad),
            )
        except ValueError as err:
            return False, str(err)
        pos = self.lista.index(doc)
        self.lista[pos] = nuevo
        self.guardar()
        return True, f"Docente {id_reg} actualizado"

    def eliminar(self, id_reg):
        doc = self.obtener(id_reg)
        if not doc:
            return False, f"No existe docente con id {id_reg}"
        self.lista.remove(doc)
        self.guardar()
        return True, f"Docente {id_reg} eliminado"


class MateriaController(CrudBase):
    def __init__(self, docentes=None, archivo="data/materias.json"):
        self.nombre = "materia"
        self.campos = Materia.CAMPOS
        self.gestor = GestorJSON(archivo)
        self.docentes = docentes or DocenteController()
        self.lista = [Materia.desde_diccionario(d) for d in self.gestor.leer()]

    def guardar(self):
        self.gestor.guardar([m.a_diccionario() for m in self.lista])

    def obtener(self, id_reg):
        return next((m for m in self.lista if m.id == id_reg), None)

    def leer(self):
        return self.lista

    def buscar(self, texto):
        t = texto.strip().lower()
        if not t:
            return []
        return [m for m in self.lista if t in m.nombre.lower() or t in m.codigo.lower()]

    def siguiente(self):
        return (max((m.id for m in self.lista), default=0)) + 1

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = [c for c in Materia.OBLIGATORIOS if not str(datos.get(c, "")).strip()]
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        codigo = str(datos.get("codigo", "")).strip().upper()
        if codigo:
            for otro in self.lista:
                if otro.codigo == codigo and otro.id != id_actual:
                    return f"Ya existe una materia con el código {codigo}"

        doc_id = datos.get("docente_id")
        if doc_id not in (None, "", "0"):
            try:
                doc_id_int = int(doc_id)
                if not self.docentes.obtener(doc_id_int):
                    return f"El docente con ID {doc_id_int} no existe"
            except ValueError:
                return "El ID del docente debe ser numérico"
        return None

    def crear(self, datos):
        error_val = self.validar(datos)
        if error_val:
            return False, error_val

        try:
            mat = Materia(
                self.siguiente(),
                datos.get("nombre", ""),
                datos.get("codigo", ""),
                datos.get("creditos", 0),
                datos.get("docente_id"),
            )
        except ValueError as err:
            return False, str(err)
        self.lista.append(mat)
        self.guardar()
        return True, f"Materia creada: {mat.etiqueta()}"

    def actualizar(self, id_reg, datos):
        mat = self.obtener(id_reg)
        if not mat:
            return False, f"No existe materia con id {id_reg}"

        error_val = self.validar(datos, id_actual=id_reg)
        if error_val:
            return False, error_val

        try:
            nuevo = Materia(
                mat.id,
                datos.get("nombre", mat.nombre),
                datos.get("codigo", mat.codigo),
                datos.get("creditos", mat.creditos),
                datos.get("docente_id", mat.docente_id),
            )
        except ValueError as err:
            return False, str(err)
        pos = self.lista.index(mat)
        self.lista[pos] = nuevo
        self.guardar()
        return True, f"Materia {id_reg} actualizada"

    def eliminar(self, id_reg):
        mat = self.obtener(id_reg)
        if not mat:
            return False, f"No existe materia con id {id_reg}"
        self.lista.remove(mat)
        self.guardar()
        return True, f"Materia {id_reg} eliminada"


class MatriculaController(CrudBase):
    def __init__(self, estudiantes=None, materias=None, archivo="data/matriculas.json"):
        self.nombre = "matrícula"
        self.campos = Matricula.CAMPOS
        self.gestor = GestorJSON(archivo)
        self.estudiantes = estudiantes or EstudianteController()
        self.materias = materias or MateriaController()
        self.lista = [Matricula.desde_diccionario(d) for d in self.gestor.leer()]

    def guardar(self):
        self.gestor.guardar([mat.a_diccionario() for mat in self.lista])

    def obtener(self, id_reg):
        return next((mat for mat in self.lista if mat.id == id_reg), None)

    def leer(self):
        return self.lista

    def buscar(self, texto):
        t = texto.strip()
        if not t:
            return []
        return [mat for mat in self.lista if t in mat.periodo]

    def siguiente(self):
        return (max((mat.id for mat in self.lista), default=0)) + 1

    def validar(self, datos, id_actual=None):
        try:
            est_id = int(datos.get("estudiante_id", 0))
            mat_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "El estudiante_id y materia_id deben ser numéricos"

        if not self.estudiantes.obtener(est_id):
            return f"El estudiante con ID {est_id} no existe"
        if not self.materias.obtener(mat_id):
            return f"La materia con ID {mat_id} no existe"

        periodo = str(datos.get("periodo", "2026-1")).strip()
        for mat in self.lista:
            if mat.estudiante_id == est_id and mat.materia_id == mat_id and mat.periodo == periodo and mat.id != id_actual:
                return "El estudiante ya está matriculado en esta materia para el mismo periodo"
        return None

    def crear(self, datos):
        error_val = self.validar(datos)
        if error_val:
            return False, error_val

        try:
            matricula = Matricula(
                self.siguiente(),
                int(datos.get("estudiante_id")),
                int(datos.get("materia_id")),
                datos.get("periodo", "2026-1")
            )
        except ValueError as err:
            return False, str(err)

        self.lista.append(matricula)
        self.guardar()
        return True, f"Matrícula #{matricula.id} registrada con éxito"

    def actualizar(self, id_reg, datos):
        return False, "Las matrículas registradas no se pueden modificar directamente"

    def eliminar(self, id_reg):
        mat = self.obtener(id_reg)
        if not mat:
            return False, f"No existe la matrícula con id {id_reg}"
        self.lista.remove(mat)
        self.guardar()
        return True, f"Matrícula {id_reg} eliminada"

    def agregar_nota(self, matricula_id, tipo, valor, peso=1):
        mat = self.obtener(matricula_id)
        if not mat:
            return False, f"No existe la matrícula con ID {matricula_id}"
        try:
            mat.agregar_nota(tipo, valor, peso)
        except ValueError as err:
            return False, str(err)
        self.guardar()
        return True, f"Nota agregada con éxito. Promedio actual: {mat.promedio}"

    def boletin(self, estudiante_id):
        est = self.estudiantes.obtener(estudiante_id)
        if not est:
            return None

        mats = [m for m in self.lista if m.estudiante_id == estudiante_id]
        texto = f"BOLETÍN ACADÉMICO - ESTUDIANTE: {est.nombre_completo} (Carnet: {est.carnet})\n"
        texto += "-" * 58 + "\n"

        if not mats:
            texto += "  El estudiante no registra matrículas activas.\n"
        else:
            promedios = []
            for m in mats:
                materia = self.materias.obtener(m.materia_id)
                nom_mat = materia.nombre if materia else "Materia desconocida"
                texto += f"• Materia: {nom_mat} [Periodo: {m.periodo}]\n"
                for nota in m.notas:
                    texto += f"   - {nota}\n"
                texto += f"   ➔ Promedio Parcial: {m.promedio} ({m.estado})\n"
                texto += "-" * 58 + "\n"
                promedios.append(m.promedio)

            if promedios:
                prom_gen = round(sum(promedios) / len(promedios), 2)
                texto += f"  PROMEDIO GENERAL ACUMULADO: {prom_gen}\n"
        return texto