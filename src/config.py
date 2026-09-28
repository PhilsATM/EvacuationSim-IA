capacities = {
    '#': 0,           # muro, capacidad 0
    '.': 3,           # espacio amplio, capacidad 3
    '=': 2,           # pasillo normal, capacidad 2
    '-': 1,           # pasillo angosto, capacidad 1
    ';': 1,           # Puerta, capacidad 1
    'E': float('inf') # Salida de evacuacion (sin limite)
}

possibleMoves = [
		(0, -1), # arriba
		(0, 1),  # abajo
		(-1, 0), # izquierda
		(1, 0),  # derecha

        # diagonales (opcional) es mejor usar heuristica euclidiana o chebyshev si los activan
        # (-1, -1), # diagonal superior izquierda
        # (-1, 1),  # diagonal inferior izquierda
        # (1, -1),  # diagonal superior derecha
        # (1, 1)    # diagonal inferior derecha
]

mapFiles = {
    # "Mapa 0": "data/map_0.txt"
    "Mapa 1": "data/map_1.txt",
    # "Mapa 2": "data/map_2.txt",
    # "Mapa 3": "data/map_3.txt",
}

agentCount = 200                # cantidad de agentes (se generan de forma aleatoria)
agentPositions = None           # posiciones iniciales manuales de los agentes
congestionPenaltyWeight = 5.0   # peso de la penalizacion
initialFireCount = 1            # cantidad de focos de incendio (se generan de forma aleatoria)
initialFirePositions = None     # posiciones iniciales manuales de los fuegos
fireSpreadInterval = 1          # cada cuantos turnos se puede propagar el fuego
fireSpreadProbability = 0.5     # probabilidad de que el fuego se propague en cada intento
maxSimulationTurns = None       # maximo de turnos de la simulacion, None: sin limite, cualquier otro valor: limite fijo
simulationSeed = None           # semilla que define la posicion inicial de los agentes y de los focos, None: aleatoria, cualquier otro valor: semilla fija
heuristicType = "manhattan"     # tipo de heuristica: "manhattan", "euclidean", "chebyshev"