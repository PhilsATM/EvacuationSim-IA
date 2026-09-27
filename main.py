from src.map_parser import buildMap, printMap
from src.algorithms.blinds import breadthFirstSearch, uniformCostSearch

def main():

    """
    actualmente calculan la misma ruta al no tener congestion lol
    """

    filePath = "data/map_1.txt"
    filePath2 = "data/map_2.txt"
    start = (1, 1)
    
    try:
        myMap = buildMap(filePath)
        myMap2 = buildMap(filePath2)
        printMap(myMap, "Mapa 1")
        printMap(myMap2, "Mapa 2")

        algorithms = {
            "BFS": breadthFirstSearch,
            "UCS": uniformCostSearch,
        }
        for name, algorithm in algorithms.items():
            path = algorithm(myMap, start)
            path2 = algorithm(myMap2, start)

            if path:
                print(f"\n{name} map 1: {path}")
                print(f"movimientos: {len(path) - 1}")
            else:
                print(f"\n{name} map 1: no se encontro una ruta")

            if path2:
                print(f"\n{name} map 2: {path2}")
                print(f"movimientos: {len(path2) - 1}")
            else:
                print(f"\n{name} map 2: no se encontro una ruta")

    except ValueError as error:
        print(error)
    except FileNotFoundError:
        print(f"\nERROR: no se encontro el archivo '{filePath}'.")

if __name__ == "__main__":
    main()