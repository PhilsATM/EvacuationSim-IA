# EvacuationSim-IA

Simulador multi-agente de evacuación ante un incendio; El sistema de navegación y toma de decisiones de los agentes trabaja con 5 algoritmos IA diferente para buscar la evacuacion, minimizando las perdidas y mitigando la congestión. 

## Autor

- Felipe Tilleria Morales

## Ejecución

Se requiere Python 3.8 o superior. No se necesitan paquetes externos.

Desde la carpeta del proyecto, ejecuta una simulación:

```bash
python main.py
```

Para ejecutar el benchmark y guardar los resultados en `benchmark_results.csv`:

```bash
python benchmark.py
```

El benchmark ejecuta 100 iteraciones por mapa y algoritmo de forma predeterminada. Puedes cambiar la cantidad de iteraciones, la semilla y el archivo de salida:

```bash
python benchmark.py --iterations 200 --seed 42 --output benchmark_results.csv
```
O directamente cambiarlos en el archivo `src/config.py`, este también permite cambiar algunos otros parámetros del proyecto como: 

- La cantidad y las posiciones iniciales de los agentes y los focos de fuego.
- La frecuencia y probabilidad de propagación del fuego.
- La penalización por congestión y el límite de turnos.
- La semilla aleatoria, la heurística y los movimientos permitidos.
- La capacidad de cada tipo de celda y los mapas activos (es posible agregar nuevos siempre y cuando sean rectángulos, tengan una única salida y estén compuestos por los caracteres permitidos)

El benchmark guarda los datos por iteración en un CSV; estos permiten calcular la tasa de supervivencia y los estadísticos descriptivos del tiempo de evacuación.

## Algoritmos

- **BFS:** busca una ruta con menos pasos.
- **UCS:** busca una ruta de menor costo.
- **A\*:** combina el costo de la ruta con una heurística de distancia.
- **Greedy:** prioriza la cercanía a la salida.
- **Genético:** evoluciona rutas mediante selección, cruce y mutación.
