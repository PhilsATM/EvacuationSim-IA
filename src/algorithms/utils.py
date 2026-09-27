from src.config import possibleMoves

def getExit(matrix):
	# buscar la celda marcada como salida
	for row in matrix:
		for cell in row:
			if cell.cellType == "E":
				return cell.x, cell.y

def validateStart(matrix, start):
	# comprobar que el inicio este dentro del mapa y sea transitable
	startX, startY = start
	if not (0 <= startY < len(matrix) and 0 <= startX < len(matrix[startY])):
		raise ValueError(f"ERROR: posicion inicial fuera del mapa: {start}")
	if not matrix[startY][startX].isWalkable():
		raise ValueError(f"ERROR: la posicion inicial no es transitable: {start}")

def getNeighbors(matrix, position):
	# obtener las celulas transitables vecinas de la posicion acutual 
	currentX, currentY = position
	rows = len(matrix)
	columns = len(matrix[0])

	# obtener los adyacentes
	for deltaX, deltaY in possibleMoves:
		nextX = currentX + deltaX
		nextY = currentY + deltaY
		if 0 <= nextX < columns and 0 <= nextY < rows: # si esta dentro del mapa
			targetCell = matrix[nextY][nextX]
			if targetCell.isWalkable(): # si es transitable 
				yield nextX, nextY

def reconstructPath(cameFrom, position):
	# reconstruir la ruta desde la pos final a la inicial
	path = [position]
	while position in cameFrom:
		position = cameFrom[position]
		path.append(position)
	path.reverse()
	return path
