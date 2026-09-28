from src.config import congestionPenaltyWeight


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

        if self.cellType == 'E':
            return 0

        occupancyRate = self.currentAgents / self.baseCapacity
        return baseCost + congestionPenaltyWeight * occupancyRate ** 2

class Agent:
    def __init__(self, agentId, startX, startY):
        self.agentId = agentId
        self.x = startX
        self.y = startY
        self.isEvacuated = False
        self.isDead = False
        self.isTrapped = False
        self.path = [] # lista de coordenadas (x, y)

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