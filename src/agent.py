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