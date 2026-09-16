from src.enviroment import buildMap, printMap

def main():
    filePath = "data/map_1.txt"
    
    try:
        myMap = buildMap(filePath)
        printMap(myMap)

        x = 0 
        y = 0
        for i in range (3):
            testCell = myMap[x][y]
            print(f"prueba de la celda ({x}, {y}):")
            print(f"- tipo de celda: '{testCell.cellType}'")
            print(f"- capacidad base: {testCell.baseCapacity}")
            print(f"- costo actual: {testCell.getCurrentCost()}")
            print(f"- accesible: {testCell.isWalkable()} \n")
            x += 1 
            y += 2
        
    except ValueError as error:
        print(error)

    except FileNotFoundError:
        print(f"\nERROR: no se encontro el archivo '{filePath}'")

if __name__ == "__main__":
    main()