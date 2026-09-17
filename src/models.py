class Cell:
    def __init__(self, x, y, cellType, baseCapacity):
        self.x = x
        self.y = y
        self.cellType = cellType
        self.baseCapacity = baseCapacity
        
        self.currentAgents = 0
        self.hasFire = False

    def isWalkable(self):
        # bloquea el paso si es muro o si el fuego ya consumio la casilla
        if self.cellType == '#' or self.hasFire:
            return False
        return True

    def getCurrentCost(self):
        baseCost = 1
        if not self.isWalkable():
            return float('inf')
        
        # la salida no tiene costo
        if self.cellType == 'E':
            return baseCost
            
        # si se supera la capacidad fisica de la celda tiene penalizacion
        if self.currentAgents >= self.baseCapacity:
            # la penalizacion es cuadratica
            penalty = (self.currentAgents - self.baseCapacity + 1) ** 2
            return baseCost + penalty
            
        return baseCost

class Agent:
    def __init__(self, agentId, startX, startY):
        self.agentId = agentId
        self.x = startX
        self.y = startY
        self.isEvacuated = False
        self.path = [] # lista de coordenadas (x, y)

    def getValidActions(self, matrix):
        # si ya evacuo no necesita moverse
        if self.isEvacuated:
            return []

        validActions = []
        rows = len(matrix)
        columns = len(matrix[0])

        # posibles movimientos
        possibleMoves = [
            (0, -1), # arriba
            (0, 1),  # abajo
            (-1, 0), # izquierda
            (1, 0)   # derecha
        ]

        # evaluar adyacentes
        for dx, dy in possibleMoves:
            nextX = self.x + dx
            nextY = self.y + dy

            # posicion dentro de los limites
            if 0 <= nextX < columns and 0 <= nextY < rows:
                targetCell = matrix[nextY][nextX]
                
                # es valido si se puede acceder (no tiene fueno ni es muro)
                if targetCell.isWalkable():
                    validActions.append((nextX, nextY))

        # puede tambien esperar en la misma celda
        validActions.append((self.x, self.y))

        return validActions

    def moveTo(self, newX, newY, matrix):
        # si el agente se mueve (y no espera)
        if (newX, newY) != (self.x, self.y):
            # libera la celda en la que estaba
            currentCell = matrix[self.y][self.x]
            if currentCell.currentAgents > 0:
                currentCell.currentAgents -= 1

            # se actualizan las coordenadas
            self.x = newX
            self.y = newY

            # aumenta el numero de agentes en la nueva celda
            targetCell = matrix[self.y][self.x]
            targetCell.currentAgents += 1

            # si se mueve a la salida se evacua
            if targetCell.cellType == 'E':
                self.isEvacuated = True
                targetCell.currentAgents -= 1 