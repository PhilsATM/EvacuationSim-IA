from random import Random
from src.models import Agent
from src.config import (
	fireSpreadInterval,
	fireSpreadProbability,
	maxSimulationTurns,
	possibleMoves,
	simulationSeed
)

generatedSeed = None

def getRandomSeed(randomSeed): # si randomSeed es None genera una aleatoria para la simulacion
	global generatedSeed
	if randomSeed is not None:
		return randomSeed
	if generatedSeed is None:
		randomGenerator = Random()
		generatedSeed = randomGenerator.randint(0, 10000)
	return generatedSeed

def spreadFire(matrix, spreadProbability, randomGenerator): 
	newFirePositions = set()

	# itera sobre cada celda del mapa para propagar el fuego a las celdas vecinas
	for sourceY, row in enumerate(matrix):
		for sourceX, sourceCell in enumerate(row):
			if not sourceCell.hasFire:
				continue

			for deltaX, deltaY in possibleMoves:
				nextX = sourceX + deltaX
				nextY = sourceY + deltaY
				if not (0 <= nextY < len(matrix) and 0 <= nextX < len(matrix[nextY])):
					continue

				targetCell = matrix[nextY][nextX]
				if not targetCell.hasFire:
					if randomGenerator.random() <= spreadProbability: # probabilidad de que se propague el fuego
						newFirePositions.add((nextX, nextY))

	for fireX, fireY in newFirePositions: # actualizar el estado de las celdas con fuego
		matrix[fireY][fireX].hasFire = True

	return len(newFirePositions)


def killBurnedAgents(matrix, agents): #  da de baja despiadadamente a los agentes que sufrieror una lenta y dolorosa muerte por el fuego
	for agent in agents:
		if agent.isDead or agent.isEvacuated:
			continue

		currentCell = matrix[agent.y][agent.x] 
		if currentCell.hasFire:
			agent.isDead = True
			agent.isTrapped = False
			currentCell.currentAgents -= 1


def createRandomFirePositions(matrix, fireCount, randomSeed=None): # crear posiciones aleatorias para los focos de fuego
	if fireCount < 0:
		raise ValueError("ERROR: la cantidad de focos no puede ser negativa")
 
	allPositions = [ 		# todas las posiciones posibles en el mapa
		(cell.x, cell.y)
		for row in matrix
		for cell in row
	]

	if fireCount > len(allPositions):
		raise ValueError(
			f"ERROR: se solicitaron {fireCount} focos, pero el mapa solo tiene {len(allPositions)} celdas"
		)

	randomSeed = getRandomSeed(randomSeed)
	randomGenerator = Random(randomSeed)
	return randomGenerator.sample(allPositions, fireCount)  # devuelve una lista con posiciones random


def createRandomAgentPositions(matrix, agentCount, randomSeed=None, initialFirePositions=()): # crear posiciones aleatorias para los agentes
	if agentCount < 0:
		raise ValueError("ERROR: la cantidad de agentes no puede ser negativa")

	randomSeed = getRandomSeed(randomSeed)
	randomGenerator = Random(randomSeed)
	firePositions = set(initialFirePositions)
	spawnSlots = []

	for row in matrix:
		for cell in row:
			position = (cell.x, cell.y)
			if cell.cellType == "E" or position in firePositions or not cell.isWalkable():	# para todas las celdas menos la salica, los fuegos iniciales y las paredes
				continue

			# cada espacio representa un lugar disponible dentro de la capacidad
			for _ in range(int(cell.baseCapacity)):
				spawnSlots.append(position)

	if agentCount > len(spawnSlots):
		raise ValueError(
			f"ERROR: se solicitaron {agentCount} agentes, pero solo hay "
			f"{len(spawnSlots)} posiciones disponibles"
		)

	randomPositions = randomGenerator.sample(spawnSlots, agentCount)
	return randomPositions


def initializeSimulation(matrix, agentPositions, initialFirePositions):
	for row in matrix: 				# limpia el mapa
		for cell in row:
			cell.currentAgents = 0
			cell.hasFire = False

	for fireX, fireY in initialFirePositions:	# pone los fuegos iniciales en el mapa
		if not (0 <= fireY < len(matrix) and 0 <= fireX < len(matrix[fireY])):
			raise ValueError(f"ERROR: posicion inicial del fuego fuera del mapa: {(fireX, fireY)}")
		matrix[fireY][fireX].hasFire = True

	agents = [
		Agent(agentId, agentX, agentY)
		for agentId, (agentX, agentY) in enumerate(agentPositions, start=1)
	]

	for agent in agents:	# inicializa el estado de cada agente
		agent.isEvacuated = False
		agent.isDead = False
		agent.isTrapped = False
		agent.path = []

		if not (0 <= agent.y < len(matrix) and 0 <= agent.x < len(matrix[agent.y])):	
			raise ValueError(f"ERROR: posicion inicial del agente fuera del mapa: {(agent.x, agent.y)}")

		startCell = matrix[agent.y][agent.x]
		if startCell.cellType == "E":
			agent.isEvacuated = True
		elif startCell.hasFire:
			agent.isDead = True
		else:
			startCell.currentAgents += 1
			if startCell.currentAgents > startCell.baseCapacity:
				raise ValueError(
					f"ERROR: demasiados agentes en la posicion inicial {(agent.x, agent.y)}"
				)

	return agents # devuelve la lista de agentes inicializados


def runSimulation(
	matrix,
	agentPositions,
	algorithm,
	initialFirePositions=(),
	fireSpreadInterval=fireSpreadInterval,
	spreadProbability=fireSpreadProbability,
	maxTurns=maxSimulationTurns,
	randomSeed=simulationSeed,
):

	if fireSpreadInterval <= 0:
		raise ValueError("ERROR: el intervalo de propagacion debe ser mayor que cero")
	if not 0 <= spreadProbability <= 1:
		raise ValueError("ERROR: la probabilidad de propagacion debe estar entre cero y uno")
	if maxTurns is not None and maxTurns <= 0:
		raise ValueError("ERROR: el maximo de turnos debe ser mayor que cero")

	agents = initializeSimulation(matrix, agentPositions, initialFirePositions) # inicializa el estado de la simulacion
	randomSeed = getRandomSeed(randomSeed)
	randomGenerator = Random(randomSeed)
	evacuationTime = 0 if any(agent.isEvacuated for agent in agents) else None # turno del ultimo agente evacuado, si ponemos manualmente algun agente en la salida: 0 para que no explote el codigo xd 
	finished = all(agent.isEvacuated or agent.isDead for agent in agents) # verifica si la simulacion termina al inicio

	turn = 0
	while not finished and (maxTurns is None or turn < maxTurns): # mientras no haya terminado o se haya alcanzado el maximo de turnos
		turn += 1
		if turn % fireSpreadInterval == 0:	# cada ciertos turnos se intenta propagar el fuego y se eliminan los agentes quemados
			spreadFire(matrix, spreadProbability, randomGenerator)
			killBurnedAgents(matrix, agents)

		activeAgents = [ # agentes que no se han petateado
			agent
			for agent in agents
			if not agent.isEvacuated and not agent.isDead and not agent.isTrapped
		]
		proposedMoves = {} # diccionario de movimientos propuestos por cada agente (la cordenada a la que quiere moverse)

		# cada agente planea su movimiento para este turno
		for agent in activeAgents:
			path = algorithm(matrix, (agent.x, agent.y)) # calculan la ruta hacia la salida
			agent.path = path
			if not path:	# si no hay camino es que quedo atrapado
				agent.isTrapped = True
			elif len(path) > 1: 
				proposedMoves[agent] = path[1] # se guarda la siguiente celda propuestaen el path

		if activeAgents:   # va rotando los agentes activos para repartir la prioridad de movimiento entre ellos	
			priorityStart = (turn - 1) % len(activeAgents)
			orderedAgents = activeAgents[priorityStart:] + activeAgents[:priorityStart]
		else:
			orderedAgents = []

		for agent in orderedAgents:  # cada agente intenta moverse según su prioridad y los movimientos propuestos
			if agent not in proposedMoves:	# si el agente esta atrapado se salta
				continue	

			nextX, nextY = proposedMoves[agent]
			targetCell = matrix[nextY][nextX]
			if targetCell.isWalkable() and targetCell.currentAgents < targetCell.baseCapacity: # se mueve si es posible y si no espera
				agent.moveTo(nextX, nextY, matrix)
				if agent.isEvacuated:
					evacuationTime = turn # si es evacuado se registra el turno

		finished = all(	# la simulacion termina cuando todos mueren, evacuan o quedan atrapados
			agent.isEvacuated or agent.isDead or agent.isTrapped
			for agent in agents
		)

	# se retornan los resultados en forma de diccionario
	return {
		"turns": turn,
		"evacuated": sum(agent.isEvacuated for agent in agents),
		"dead": sum(agent.isDead for agent in agents),
		"trapped": sum(agent.isTrapped and not agent.isDead for agent in agents),
		"active": sum(
			not agent.isEvacuated and not agent.isDead and not agent.isTrapped
			for agent in agents
		),
		"survivalRate": 100 * sum(agent.isEvacuated for agent in agents) / len(agents),
		"evacuationTime": evacuationTime,
		"finished": finished
	}