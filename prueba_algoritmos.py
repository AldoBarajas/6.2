"""Ejecutar: python -m unittest discover -s codigo -p 'prueba_*.py' -v"""
import random
import unittest
from busquedas import busqueda_secuencial, busqueda_binaria, TablaHashEncadenamiento


class AlgoritmosBusquedaTests(unittest.TestCase):
    def test_vacios(self):
        self.assertFalse(busqueda_secuencial([], 1).encontrado)
        self.assertFalse(busqueda_binaria([], 1).encontrado)
        self.assertFalse(TablaHashEncadenamiento(3).buscar(1).encontrado)

    def test_valores_positivos_negativos_y_duplicados(self):
        datos = [7, -10, 7, 0, 9, -3, 9]
        tabla = TablaHashEncadenamiento(7)
        for d in datos:
            tabla.insertar(d)
        self.assertEqual(tabla.tamano, len(set(datos)))
        self.assertEqual(tabla.duplicados_omitidos, 2)
        for valor in (7, -10, 0, 9, -3):
            self.assertTrue(busqueda_secuencial(datos, valor).encontrado)
            self.assertTrue(busqueda_binaria(sorted(datos), valor).encontrado)
            self.assertTrue(tabla.buscar(valor).encontrado)
        for valor in (5, 12, -1):
            self.assertFalse(busqueda_secuencial(datos, valor).encontrado)
            self.assertFalse(busqueda_binaria(sorted(datos), valor).encontrado)
            self.assertFalse(tabla.buscar(valor).encontrado)

    def test_colisiones(self):
        tabla = TablaHashEncadenamiento(7)
        for d in (3, 10, 17, 24):
            tabla.insertar(d)
        self.assertEqual(tabla.colisiones_insercion, 3)
        self.assertEqual(tabla.estadisticas()['longitud_maxima_cadena'], 4)
        self.assertEqual(tabla.buscar(24).comparaciones, 4)
        self.assertEqual(tabla.buscar(31).comparaciones, 4)
        self.assertEqual(tabla.buscar(0).comparaciones, 0)

    def test_randomizados_y_metrica(self):
        for seed in range(4):
            rng = random.Random(seed)
            data = rng.sample(range(-10000, 10000), 200)
            tabla = TablaHashEncadenamiento(269)
            for d in data:
                tabla.insertar(d)
            conjunto = set(data)
            for k in rng.sample(range(-15000, 15000), 100):
                esperado = k in conjunto
                for fn in (lambda x: busqueda_secuencial(data, x),
                           lambda x: busqueda_binaria(sorted(data), x),
                           tabla.buscar):
                    r = fn(k)
                    self.assertEqual(r.encontrado, esperado)
                    self.assertGreaterEqual(r.comparaciones, r.iteraciones)
                    self.assertGreaterEqual(r.iteraciones, 0)

    def test_binaria_acota_iteraciones(self):
        datos = list(range(100001))
        for clave in (-1, 0, 100000, 100001, 34751):
            r = busqueda_binaria(datos, clave)
            self.assertLessEqual(r.iteraciones, 17)


if __name__ == '__main__':
    unittest.main()
