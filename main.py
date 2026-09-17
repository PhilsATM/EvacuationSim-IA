from src.map_parser import buildMap, printMap
from src.models import Agent

def main():
    filePath = "data/map_1.txt"
    
    try:
        myMap = buildMap(filePath)
        printMap(myMap)
        
        # agente id=1 en la posicion (1, 1)
        testAgent = Agent(1, 1, 1)
        print(f"\nagente id={testAgent.agentId} creado en la posicion: ({testAgent.x}, {testAgent.y})")
        
        # sacamos sus movimientos validos
        validMoves = testAgent.getValidActions(myMap)
        print(f"movimientos validos disponibles: {validMoves}")
        
        # usa el primer movimiento valido (despues dependera del algoritmo)
        if validMoves:
            nextX, nextY = validMoves[0]
            testAgent.moveTo(nextX, nextY, myMap)
            print(f"nueva posicion del agente: ({testAgent.x}, {testAgent.y})")
        
        # de nuevo los movimientos validos
        validMoves = testAgent.getValidActions(myMap)
        print(f"movimientos validos disponibles: {validMoves}")
            
    except ValueError as error:
        print(error)
    except FileNotFoundError:
        print(f"\nERROR: no se encontro el archivo '{filePath}'.")

if __name__ == "__main__":
    main()