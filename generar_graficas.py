"""Gráficas PNG a partir de CSV existentes. Requiere matplotlib (opcional)."""
import argparse
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

COLORS = {'Secuencial':'#D97706', 'Binaria':'#2563EB', 'Hash encadenada':'#0F766E'}
ORDER = list(COLORS)


def load_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main(datos: Path, salida: Path):
    salida.mkdir(parents=True, exist_ok=True)
    res = load_csv(datos/'resumen.csv')
    ns = sorted({int(r['N']) for r in res})
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10, 'axes.titleweight':'bold',
                         'figure.facecolor':'white', 'axes.spines.top':False,
                         'axes.spines.right':False})
    series = [('comparaciones_promedio', 'Comparaciones de clave por consulta', 'Comparaciones'),
              ('iteraciones_promedio', 'Iteraciones por consulta', 'Iteraciones'),
              ('cpu_medio_por_consulta_us', 'Tiempo de CPU medio por consulta', 'Microsegundos (µs)')]
    for campo, titulo, eje in series:
        for condicion in ('Exitosa','Fallida'):
            fig, ax = plt.subplots(figsize=(9.6,4.5), dpi=180)
            for metodo in ORDER:
                ys = [float(next(r[campo] for r in res if int(r['N'])==n and r['metodo']==metodo and r['resultado']==condicion)) for n in ns]
                ax.plot(range(len(ns)), ys, marker='o', markersize=7, linewidth=2.4,
                        label=metodo, color=COLORS[metodo])
                for x,y in enumerate(ys):
                    label = f'{y:,.1f}' if y>=10 else f'{y:.2f}'
                    ax.annotate(label, (x,y), xytext=(0,8), textcoords='offset points',
                                ha='center', fontsize=7.7, color=COLORS[metodo])
            ax.set_yscale('symlog', linthresh=1)
            ax.set_xticks(range(len(ns)), [f'{n:,}' for n in ns])
            ax.set_xlabel('Número de registros (N)')
            ax.set_ylabel(eje+' · escala simétrica logarítmica')
            ax.set_title(titulo+' · '+condicion.lower())
            ax.grid(alpha=.20, axis='y')
            ax.legend(loc='upper left', fontsize=8, ncols=3, bbox_to_anchor=(0,1.0))
            fig.tight_layout(pad=1.4)
            name={'comparaciones_promedio':'comparaciones','iteraciones_promedio':'iteraciones',
                  'cpu_medio_por_consulta_us':'tiempo_cpu'}[campo]
            fig.savefig(salida/f'{name}_{condicion.lower()}.png', bbox_inches='tight')
            plt.close(fig)
    # Sensibilidad de las colisiones a la carga y a la estructura.
    cargas = load_csv(datos/'cargas_hash.csv')
    fig, ax = plt.subplots(figsize=(9.6,4.5),dpi=180)
    for condicion,color in [('Exitosa','#0F766E'),('Fallida','#BE123C')]:
        filas=sorted((r for r in cargas if r['condicion']==condicion),key=lambda r:float(r['carga_real']))
        ax.plot([float(r['carga_real']) for r in filas],
                [float(r['comparaciones_promedio']) for r in filas],
                linewidth=2.5,marker='o',color=color,label=condicion)
    ax.set_xlabel('Factor de carga real α = N / m')
    ax.set_ylabel('Comparaciones medias por consulta')
    ax.set_title('Tabla HASH: efecto del factor de carga (N = 50,000)')
    ax.grid(alpha=.2)
    ax.legend()
    fig.tight_layout(pad=1.5)
    fig.savefig(salida/'hash_factor_carga.png',bbox_inches='tight')
    plt.close(fig)
    print('Se generaron 7 gráficas en', salida)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--datos',type=Path,default=Path('datos'))
    parser.add_argument('--salida',type=Path,default=Path('graficas'))
    args=parser.parse_args()
    main(args.datos,args.salida)
