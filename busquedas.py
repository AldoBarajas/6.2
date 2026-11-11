"""Algoritmos educativos de búsqueda y métricas verificables.

Una comparación = una evaluación explícita de igualdad (<==>) o de orden (<).
Una iteración = un elemento/candidato examinado; las operaciones de control del
bucle no se cuentan. Las tres técnicas devuelven una decisión de pertenencia.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Resultado:
    encontrado: bool
    comparaciones: int
    iteraciones: int
    accesos_cubeta: int = 0


def busqueda_secuencial(datos: list[int], objetivo: int) -> Resultado:
    comparaciones = 0
    iteraciones = 0
    for valor in datos:
        iteraciones += 1
        comparaciones += 1
        if valor == objetivo:
            return Resultado(True, comparaciones, iteraciones)
    return Resultado(False, comparaciones, iteraciones)


def busqueda_binaria(datos_ordenados: list[int], objetivo: int) -> Resultado:
    """Requiere datos ordenados no decrecientemente; no verifica ese requisito."""
    izquierda, derecha = 0, len(datos_ordenados) - 1
    comparaciones = iteraciones = 0
    while izquierda <= derecha:
        mitad = izquierda + (derecha - izquierda) // 2
        valor = datos_ordenados[mitad]
        iteraciones += 1
        comparaciones += 1  # valor == objetivo
        if valor == objetivo:
            return Resultado(True, comparaciones, iteraciones)
        comparaciones += 1  # valor < objetivo
        if valor < objetivo:
            izquierda = mitad + 1
        else:
            derecha = mitad - 1
    return Resultado(False, comparaciones, iteraciones)


class TablaHashEncadenamiento:
    """Tabla HASH de enteros con h(k)=k mod m y encadenamiento separado.

    No usa dict/set de Python para almacenar/buscar los elementos.
    m puede ser elegido por el experimento; el constructor la deja vacía.
    """
    def __init__(self, capacidad: int):
        if capacidad < 1:
            raise ValueError('La capacidad debe ser positiva')
        self.capacidad = capacidad
        self.cubetas: list[list[int]] = [[] for _ in range(capacidad)]
        self.tamano = 0
        self.colisiones_insercion = 0
        self.duplicados_omitidos = 0

    def dispersar(self, clave: int) -> int:
        return clave % self.capacidad

    def insertar(self, clave: int) -> bool:
        cubeta = self.cubetas[self.dispersar(clave)]
        for existente in cubeta:
            if existente == clave:
                self.duplicados_omitidos += 1
                return False
        if cubeta:
            self.colisiones_insercion += 1
        cubeta.append(clave)
        self.tamano += 1
        return True

    def buscar(self, objetivo: int) -> Resultado:
        cubeta = self.cubetas[self.dispersar(objetivo)]
        comparaciones = iteraciones = 0
        for clave in cubeta:
            iteraciones += 1
            comparaciones += 1
            if clave == objetivo:
                return Resultado(True, comparaciones, iteraciones, 1)
        return Resultado(False, comparaciones, iteraciones, 1)

    def estadisticas(self) -> dict:
        ocupadas = sum(bool(c) for c in self.cubetas)
        return {
            'capacidad': self.capacidad,
            'elementos': self.tamano,
            'factor_carga': self.tamano / self.capacidad,
            'cubetas_ocupadas': ocupadas,
            'cubetas_vacias': self.capacidad - ocupadas,
            'longitud_maxima_cadena': max(map(len, self.cubetas), default=0),
            'colisiones_insercion': self.colisiones_insercion,
            'duplicados_omitidos': self.duplicados_omitidos,
        }
