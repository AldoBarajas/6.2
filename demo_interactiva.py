"""Demostración accesible para grabar el video con cámara OBS."""
from busquedas import busqueda_secuencial, busqueda_binaria, TablaHashEncadenamiento


def mostrar(nombre, resultado):
    print(f'{nombre:13} | encontrado={str(resultado.encontrado):5} | '
          f'comparaciones={resultado.comparaciones:2} | iteraciones={resultado.iteraciones:2} | '
          f'accesos a cubeta={resultado.accesos_cubeta}')


def main():
    datos = [42, 7, 90, 15, 28, 54, 11, 35, 70]
    ordenados = sorted(datos)
    tabla = TablaHashEncadenamiento(7)
    for elemento in datos:
        tabla.insertar(elemento)
    print('Lista original:', datos)
    print('Lista ordenada:', ordenados)
    print('HASH: h(clave)=clave % 7; cubetas ocupadas:')
    for i, cubeta in enumerate(tabla.cubetas):
        if cubeta:
            print(f'    [{i}] -> ' + ' -> '.join(map(str, cubeta)))
    for clave in (28, 99):
        print(f'\nBUSCANDO {clave}:')
        mostrar('Secuencial', busqueda_secuencial(datos, clave))
        mostrar('Binaria', busqueda_binaria(ordenados, clave))
        mostrar('HASH', tabla.buscar(clave))
    print('\nEjemplo de colisión: h(7)=0 y h(28)=0 con capacidad 7.')


if __name__ == '__main__':
    main()
