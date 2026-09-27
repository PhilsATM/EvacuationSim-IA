from collections import deque
from itertools import count
from heapq import heappop, heappush

from .utils import getExit, getNeighbors, reconstructPath, validateStart

def breadthFirstSearch(matrix, start):
	validateStart(matrix, start)
	"""
	se obtiene la posicion de la salida solo para verificar si la alcanzamos, no para calcular costos,
	otra opcion era comparar en cada iteracion: position.cellType == "E", pero era un poco menos eficiente
	"""
	exit = getExit(matrix) 
	frontier = deque([start])  # cola FIFO 
	cameFrom = {}  # diccionario de predecesores
	visited = {start}  # posiciones visitadas

	while frontier:  # mientras haya posiciones por explorar
		position = frontier.popleft() 
		if position == exit: 
			return reconstructPath(cameFrom, position) # si alcanzamos la salida retornamos la ruta

		for nextPosition in getNeighbors(matrix, position):   # para cada celda vecina transitable y no visitada
			if nextPosition not in visited:
				visited.add(nextPosition) # marcar como visitada
				cameFrom[nextPosition] = position # registra el actual como predecesor de la celda vecina
				frontier.append(nextPosition) # agrega la celda vecina a la cola 
	return []

def uniformCostSearch(matrix, start):
	validateStart(matrix, start)
	exit = getExit(matrix)
	sequence = count()  # lo uso para manejar los empates de costos
	frontier = [(0, next(sequence), start)]  # costo, desempate y posicion
	cameFrom = {}  
	costs = {start: 0}  # costo minimo para cada posicion

	while frontier:
		currentCost, _, position = heappop(frontier) # menor costo en el heap
		if currentCost != costs.get(position): # si no coincide con el costo minimo conocido salta ignora 
			continue
		if position == exit:
			return reconstructPath(cameFrom, position)

		for nextPosition in getNeighbors(matrix, position):
			newCost = currentCost + matrix[nextPosition[1]][nextPosition[0]].getCurrentCost()
			if newCost < costs.get(nextPosition, float("inf")): # se actualiza solo si el costo es menos de lo que ya tenemos
				costs[nextPosition] = newCost
				cameFrom[nextPosition] = position
				heappush(frontier, (newCost, next(sequence), nextPosition))
	return []