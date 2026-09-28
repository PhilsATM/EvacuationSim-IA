from random import Random
from .utils import getExit, getNeighbors, validateStart

def findRandomizedPath(matrix, start, goal, randomGenerator, forbidden=()): # busca una ruta usando DFS
	forbidden = set(forbidden) # algunas celtas estan prohibidas de los paths
	# permitir siempre los extremos de la ruta
	forbidden.discard(start) 
	forbidden.discard(goal)
	if start == goal:
		return [start]

	def shuffledNeighbors(position): # obtener vecinos transitables en orden aleatorio
		neighbors = [neighbor for neighbor in getNeighbors(matrix, position) if neighbor not in forbidden] # filtrar vecinos prohibidos
		randomGenerator.shuffle(neighbors) # aleatorizar la lista
		return iter(neighbors)

	path = [start]
	visited = forbidden | {start} # marcar las posiciones prohibidas y la inicial como visitadas
	stack = [shuffledNeighbors(start)] # cada nivel guarda los vecinos pendientes de explorar
	while stack:  # mientras que haya posiciones por explorar
		neighbors = stack[-1] 
		try:
			nextPosition = next(neighbors) # intenta obtener el siguiente vecino
		except StopIteration: # si no quedan vecinos retrocede
			stack.pop()
			path.pop()
			continue

		if nextPosition in visited: # si ya fue visitada la ignora
			continue
		# si no marcar la celda como visitada y agregarla al path
		visited.add(nextPosition) 
		path.append(nextPosition)
		if nextPosition == goal: # si es el final se retorna
			return path
		stack.append(shuffledNeighbors(nextPosition)) # agregar los vecinos del siguiente nodo al stack

	return []


def isValidPath(matrix, path, start, goal): # basicamente comprueba que la ruta conecte el inicio y la salida sin repetir ni atravesar celdas no alcanzables
	if not path or path[0] != start or path[-1] != goal:
		return False
	if len(path) != len(set(path)):
		return False

	for position in path:
		x, y = position
		if not matrix[y][x].isWalkable():
			return False

	for current, following in zip(path, path[1:]):
		if abs(current[0] - following[0]) + abs(current[1] - following[1]) != 1:
			return False

	return True


def getPathCost(matrix, path): # suma el costo de las celdas recorridas sin contar la posicion inicial	
	return sum(matrix[y][x].getCurrentCost() for x, y in path[1:])


def crossover(matrix, firstParent, secondParent, start, goal, randomGenerator): # combina dos rutas compartiendo
	secondParentIndexes = {position: index for index, position in enumerate(secondParent)} 
	sharedPositions = [position for position in firstParent if position in secondParentIndexes]
	if not sharedPositions:
		return randomGenerator.choice((firstParent, secondParent)) # sin puntos de cruce conserva un padre cualquiera

	crossingPosition = randomGenerator.choice(sharedPositions)
	firstIndex = firstParent.index(crossingPosition)
	secondIndex = secondParentIndexes[crossingPosition]
	child = firstParent[:firstIndex] + secondParent[secondIndex:]
	if isValidPath(matrix, child, start, goal):
		return child
	return randomGenerator.choice((firstParent, secondParent)) # descartar cruces que formen rutas invalidas


def mutate(matrix, path, start, goal, randomGenerator): # elige dos puntos y reemplaza el tramo entre ellos por otro camino
	if len(path) < 3:
		return path

	startIndex = randomGenerator.randrange(len(path) - 2)
	endIndex = randomGenerator.randrange(startIndex + 2, len(path))
	forbidden = set(path[:startIndex]) | set(path[endIndex + 1:]) # prohibe lo demas para que no se crucen y se creen ciclos
	segment = findRandomizedPath(matrix, path[startIndex], path[endIndex], randomGenerator, forbidden) # intenta crear el camino
	if not segment:
		return path # si no se pudo conectar el tramo conserva el original

	mutatedPath = path[:startIndex] + segment + path[endIndex + 1:]
	if isValidPath(matrix, mutatedPath, start, goal):
		return mutatedPath
	return path # conservar la ruta original si la mutacion no es valida


def selectParent(population, matrix, randomGenerator):  # compara hasta tres y elige el de menor costo
	tournament = randomGenerator.sample(population, min(3, len(population)))
	return min(tournament, key=lambda path: getPathCost(matrix, path))


def geneticSearch(matrix, start, populationSize=12, generations=8, mutationRate=0.35, randomSeed=None, previousPath=None):
	if populationSize < 2:
		raise ValueError("ERROR: el tamano de la poblacion debe ser al menos 2")
	if generations < 0:
		raise ValueError("ERROR: el numero de generaciones no puede ser negativo")
	if not 0 <= mutationRate <= 1:
		raise ValueError("ERROR: la tasa de mutacion debe estar entre 0 y 1")

	validateStart(matrix, start)
	goal = getExit(matrix)
	if goal is None:
		return []

	randomGenerator = Random(randomSeed)
	neighbors = list(getNeighbors(matrix, start))
	randomGenerator.shuffle(neighbors) # para variar el orden
	population = []
	if previousPath: 
		try:
			currentIndex = previousPath.index(start)
			remainingPath = previousPath[currentIndex:]
			if isValidPath(matrix, remainingPath, start, goal):
				population.append(remainingPath) # conservar como candidato el plan previo si sigue vigente
		except ValueError:
			pass

	for nextPosition in neighbors[:populationSize]: # crear rutas desde vecinos iniciales diferentes
		if len(population) >= populationSize:
			break
		remainingPath = findRandomizedPath(matrix, nextPosition, goal, randomGenerator, {start})
		if remainingPath:
			population.append([start] + remainingPath) # agrega la ruta de un vecino a la poblacion

	
	while len(population) < populationSize: # si no hay suficientes rutas se generan nuevas aleatorias hasta alcanzar el tamaño que le pasamos
		candidate = findRandomizedPath(matrix, start, goal, randomGenerator)
		if not candidate:
			return []
		population.append(candidate)

	for _ in range(generations): 
		population.sort(key=lambda path: getPathCost(matrix, path)) # ordenar por costo del path
		eliteCount = max(1, populationSize // 5) # conservar el 20% mejor
		nextGeneration = population[:eliteCount] # conservar los mejores sin cambios

		while len(nextGeneration) < populationSize: # llena la siguiente generacion hasta su tamaño configurado
			firstParent = selectParent(population, matrix, randomGenerator)
			secondParent = selectParent(population, matrix, randomGenerator)
			child = crossover(matrix, firstParent, secondParent, start, goal, randomGenerator)
			if randomGenerator.random() < mutationRate:
				child = mutate(matrix, child, start, goal, randomGenerator)
			nextGeneration.append(child)

		population = nextGeneration

	# devolver la ruta de menor costo de la ultima generacion, osea la mejor ruta encontrada
	return min(population, key=lambda path: getPathCost(matrix, path))
