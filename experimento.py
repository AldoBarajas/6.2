"""Ejecutar: python codigo/experimento.py --salida datos

Reproducible (semillas fijas); no requiere paquetes externos.
El código instrumenta cada comparación/iteración y mide tiempo de CPU.
"""
import argparse
import csv
import math
import random
import statistics
import time
from pathlib import Path
from busquedas import (busqueda_secuencial, busqueda_binaria,
                       TablaHashEncadenamiento)

SEEDS = (6051, 6052, 6053)
METODOS = ('Secuencial', 'Binaria', 'Hash encadenada')


def primo_siguiente(n: int) -> int:
    n = max(n, 2)
    while True:
        limite = math.isqrt(n)
        if all(n % d != 0 for d in range(2, limite + 1)):
            return n
        n += 1


def guardar_csv(destino: Path, registros: list[dict], columnas: list[str]) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open('w', newline='', encoding='utf-8-sig') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(registros)


def medir_consultas(funcion, claves, debe_existir):
    inicio = time.process_time_ns()
    comps = iters = cubetas = 0
    for clave in claves:
        r = funcion(clave)
        if r.encontrado != debe_existir:
            raise AssertionError(f'Respuesta incorrecta para {clave}')
        comps += r.comparaciones
        iters += r.iteraciones
        cubetas += r.accesos_cubeta
    cpu_us = (time.process_time_ns() - inicio) / 1000.0
    return comps, iters, cubetas, cpu_us


def ejecutar(tamanos, consultas_por_clase, semillas, salida):
    resultado = []
    preparacion = []
    for n in tamanos:
        for seed in semillas:
            rng = random.Random(seed * 1000003 + n)
            datos = rng.sample(range(1, 10**9), n)
            positivas = rng.sample(datos, consultas_por_clase)
            negativas = [-rng.randint(1, 10**9) for _ in range(consultas_por_clase)]

            t0 = time.process_time_ns()
            ordenados = sorted(datos)
            sort_us = (time.process_time_ns() - t0) / 1000
            m = primo_siguiente(math.ceil(n / 0.75))
            t0 = time.process_time_ns()
            tabla = TablaHashEncadenamiento(m)
            for clave in datos:
                tabla.insertar(clave)
            hash_us = (time.process_time_ns() - t0) / 1000
            if tabla.tamano != n:
                raise AssertionError('El generador debe producir claves únicas')
            est = tabla.estadisticas()
            preparacion.append({'N': n, 'semilla': seed, 'ordenacion_cpu_ms': round(sort_us/1000, 4),
                                'hash_construccion_cpu_ms': round(hash_us/1000, 4),
                                'capacidad_hash': m, 'factor_carga': round(est['factor_carga'], 5),
                                'colisiones_insercion': est['colisiones_insercion'],
                                'max_cadena': est['longitud_maxima_cadena'],
                                'cubetas_ocupadas': est['cubetas_ocupadas']})
            funciones = {'Secuencial': lambda k: busqueda_secuencial(datos, k),
                         'Binaria': lambda k: busqueda_binaria(ordenados, k),
                         'Hash encadenada': tabla.buscar}
            for metodo, fn in funciones.items():
                for condicion, claves, encontrada in [('Exitosa', positivas, True),
                                                       ('Fallida', negativas, False)]:
                    comps, iters, acceso, cpu = medir_consultas(fn, claves, encontrada)
                    resultado.append({'N': n, 'semilla': seed, 'metodo': metodo,
                                      'resultado': condicion, 'consultas': len(claves),
                                      'comparaciones_totales': comps, 'iteraciones_totales': iters,
                                      'accesos_cubeta_totales': acceso,
                                      'cpu_total_ms': round(cpu/1000, 6)})
        print(f'N={n:,}: completo ({len(semillas)*consultas_por_clase*2} consultas por método)')

    columnas = list(resultado[0])
    guardar_csv(salida/'mediciones_por_semilla.csv', resultado, columnas)
    guardar_csv(salida/'preparacion.csv', preparacion, list(preparacion[0]))
    resumen = []
    for n in tamanos:
        for metodo in METODOS:
            for condicion in ('Exitosa', 'Fallida'):
                filas = [r for r in resultado if r['N']==n and r['metodo']==metodo and r['resultado']==condicion]
                q = sum(r['consultas'] for r in filas)
                resumen.append({'N': n, 'metodo': metodo, 'resultado': condicion,
                                'consultas': q,
                                'comparaciones_promedio': round(sum(r['comparaciones_totales'] for r in filas)/q, 3),
                                'iteraciones_promedio': round(sum(r['iteraciones_totales'] for r in filas)/q, 3),
                                'accesos_cubeta_promedio': round(sum(r['accesos_cubeta_totales'] for r in filas)/q, 3),
                                'cpu_medio_por_consulta_us': round(sum(r['cpu_total_ms'] for r in filas)*1000/q, 4),
                                'cpu_mediana_por_consulta_us': round(statistics.median(r['cpu_total_ms']*1000/r['consultas'] for r in filas), 4)})
    guardar_csv(salida/'resumen.csv', resumen, list(resumen[0]))

    # Efecto de la carga en el HASH, mismo conjunto y mismas consultas para comparar.
    cargas = []
    n = min(50000, max(tamanos))
    rng = random.Random(61998)
    datos = rng.sample(range(1, 10**9), n)
    presentes = rng.sample(datos, consultas_por_clase*2)
    ausentes = [-rng.randint(1, 10**9) for _ in range(consultas_por_clase*2)]
    for carga_deseada in (0.50, 0.75, 1.00, 1.50, 2.00):
        m = primo_siguiente(math.ceil(n / carga_deseada))
        tabla = TablaHashEncadenamiento(m)
        for d in datos:
            tabla.insertar(d)
        estad = tabla.estadisticas()
        for condicion, claves, esperado in [('Exitosa', presentes, True), ('Fallida', ausentes, False)]:
            c, i, _, cpu = medir_consultas(tabla.buscar, claves, esperado)
            cargas.append({'N': n, 'carga_objetivo': carga_deseada,
                           'carga_real': round(estad['factor_carga'], 4),
                           'condicion': condicion, 'consultas': len(claves),
                           'comparaciones_promedio': round(c/len(claves), 3),
                           'iteraciones_promedio': round(i/len(claves), 3),
                           'cpu_medio_us': round(cpu/len(claves), 4),
                           'colisiones_insercion': estad['colisiones_insercion'],
                           'max_cadena': estad['longitud_maxima_cadena']})
    guardar_csv(salida/'cargas_hash.csv', cargas, list(cargas[0]))

    # Caso patológico controlado: 500 claves distintas con idéntico residuo.
    m = 1009
    tabla = TablaHashEncadenamiento(m)
    for i in range(500):
        tabla.insertar(7 + i*m)
    colisiones = []
    for nombre, key in [('Primera insertada', 7),
                        ('Última insertada', 7+499*m),
                        ('Ausente mismo índice', 7+700*m),
                        ('Ausente cubeta vacía', 8)]:
        res = tabla.buscar(key)
        colisiones.append({'caso': nombre, 'clave': key,
                           'h_clave': tabla.dispersar(key),
                           'encontrado': res.encontrado,
                           'comparaciones': res.comparaciones,
                           'iteraciones': res.iteraciones})
    guardar_csv(salida/'colisiones_forzadas.csv', colisiones, list(colisiones[0]))
    print('Prueba de colisiones forzadas: ', [(r['caso'], r['comparaciones']) for r in colisiones])
    return resumen, preparacion, cargas, colisiones


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--tamanos', type=int, nargs='+', default=[10000, 50000, 100000])
    cli.add_argument('--consultas', type=int, default=100, help='Consultas exitosas y fallidas por semilla')
    cli.add_argument('--semillas', type=int, nargs='+', default=list(SEEDS))
    cli.add_argument('--salida', type=Path, default=Path('datos'))
    args = cli.parse_args()
    if min(args.tamanos) < args.consultas or args.consultas < 1:
        cli.error('Cada tamaño debe ser mayor o igual a --consultas, que debe ser positiva.')
    ejecutar(args.tamanos, args.consultas, args.semillas, args.salida)
