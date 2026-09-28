from heapq import heappop, heappush
from itertools import count
from math import hypot, inf

from .utils import getExit, getNeighbors, reconstructPath, validateStart


def getHeuristic(position, goal, heuristicType="manhattan"):
	x, y = position
	goalX, goalY = goal
	deltaX = abs(x - goalX)
	deltaY = abs(y - goalY)

	# calcular las heuristicas
	if heuristicType == "manhattan":
		distance = deltaX + deltaY
	elif heuristicType == "euclidean":
		distance = hypot(deltaX, deltaY)
	elif heuristicType == "chebyshev":
		distance = max(deltaX, deltaY)
	else:
		raise ValueError(f"ERROR: heuristica no reconocida: {heuristicType}")

	return max(distance - 1, 0) # restamos 1 porque la salida no deberia tener costo


def aStarSearch(matrix, start, heuristicType="manhattan"):
	validateStart(matrix, start)
	goal = getExit(matrix)
	sequence = count() # para manejar el desempate en la cola de prioridad
	frontier = [(getHeuristic(start, goal, heuristicType), next(sequence), 0, start)] # prioridad, desempate, costo acumulado y posicion
	cameFrom = {} # para reconstruir el path
	costs = {start: 0} # menor costo acumulado hasta el momento

	while frontier:
		_, _, currentCost, position = heappop(frontier) # el elemento con la menor prioridad del heap
		if currentCost != costs.get(position):   # si no coincide con el costo minimo conocido salta ignora 
			continue
		if position == goal:
			return reconstructPath(cameFrom, position) # si se encuentra la salida se termina y se reconstruye el path

		for nextPosition in getNeighbors(matrix, position): # explorar vecinos del nodo actual
			nextX, nextY = nextPosition
			newCost = currentCost + matrix[nextY][nextX].getCurrentCost()
			if newCost < costs.get(nextPosition, inf):	# si encontramos un costo menor para el vecino lo actualizamos
				costs[nextPosition] = newCost
				cameFrom[nextPosition] = position
				priority = newCost + getHeuristic(nextPosition, goal, heuristicType) # costo acumulado + heuristica 
				heappush(frontier, (priority, next(sequence), newCost, nextPosition))

	return []


def greedyBestFirstSearch(matrix, start, heuristicType="manhattan"):
	validateStart(matrix, start)
	goal = getExit(matrix)
	sequence = count()
	frontier = [(getHeuristic(start, goal, heuristicType), next(sequence), start)]
	cameFrom = {}
	visited = {start}

	while frontier:
		_, _, position = heappop(frontier)
		if position == goal:
			return reconstructPath(cameFrom, position)

		for nextPosition in getNeighbors(matrix, position):
			if nextPosition not in visited:
				visited.add(nextPosition)
				cameFrom[nextPosition] = position
				# greedy prioriza solo la distancia, no el costo acumulado.
				priority = getHeuristic(nextPosition, goal, heuristicType)
				heappush(frontier, (priority, next(sequence), nextPosition))

	return []
