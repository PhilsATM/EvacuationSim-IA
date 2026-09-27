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
]