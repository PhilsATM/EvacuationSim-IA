from src.config import capacities
from src.models import Cell

def validMap(matrix, name="Mapa"):
    # que no este vacio el mapa
    if not matrix or len(matrix) == 0:
        raise ValueError(f"[{name}] ERROR: el mapa esta vacio.")

    rows = len(matrix)
    columns = len(matrix[0])

    if columns == 0:
        raise ValueError(f"[{name}] ERROR: algunas columnas estan vacias.")

    exitCount = 0

    for i, row in enumerate(matrix):
        # validar que la matriz sea un rectangulo
        if len(row) != columns:
            raise ValueError(
                f"[{name}] ERROR: el largo de las filas debe coincidir, disparidad en la fila {i}"
            )

        # validar caracteres y contar las salidas del mapa
        for j, char in enumerate(row):
            if char not in set(capacities.keys()):
                raise ValueError(
                    f"[{name}] ERROR: caracter no permitido en la posicion ({i}, {j}): '{char}'"
                )
            
            if char == 'E':
                exitCount += 1

    # validar la existencia y unicidad de la salida
    """
    tenia pensado exigir que la salida estuviera en un borde del mapa, pero como representan "pisos" asumi que la salida 
    igual puede ser una escalera u algo del estilo.
    """
    if exitCount == 0:
        raise ValueError(f"[{name}] ERROR: el mapa no tiene ninguna salida ('E')")
    elif exitCount > 1:
        raise ValueError(
            f"[{name}] ERROR: el mapa debe contener una sola salida ('E'), actualmente tiene {exitCount}"
        )

    print(f"[{name}] la matriz es valida ({rows}x{columns}) con 1 salida registrada.")
    return True

def buildMap(filePath):
    textGrid = [] # es solo una matriz con los caracteres para validarlo y seguir el principio de Fail-Fast

    # lee el txt
    with open(filePath, 'r') as fileData:
        for textLine in fileData:
            rowList = list(textLine.strip())
            if rowList:
                textGrid.append(rowList)
                
    # usamos la funcion de validacion
    validMap(textGrid, name=filePath)
    
    # creamos la matriz de celdas (la que usaremos para los algoritmos)
    matrix = []
    for y, textRow in enumerate(textGrid):
        Row = []
        for x, char in enumerate(textRow):
            capacity = capacities.get(char, 0)
            
            # creamos una instancia de celda y le hacemos append a la fila
            newCell = Cell(x, y, char, capacity)
            Row.append(newCell)
            
        matrix.append(Row) # anidamos la fila a la matriz
        
    return matrix

# imprime el mapa (debug)
def printMap(matrix):
    print("\n--- Visualizacion del Mapa Generado ---")
    for row in matrix:
        rowString = "".join([cell.cellType for cell in row])
        print(rowString)
    print("\n")