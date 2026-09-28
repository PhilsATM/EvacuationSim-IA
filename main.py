from functools import partial

from src.config import agentCount, agentPositions as configuredAgentPositions, initialFireCount, initialFirePositions as configuredFirePositions, mapFiles, simulationSeed
from src.map_parser import buildMap, printMap
from src.algorithms.blinds import breadthFirstSearch, uniformCostSearch
from src.algorithms.heuristics import aStarSearch, greedyBestFirstSearch
from src.simulation import createRandomAgentPositions, createRandomFirePositions, runSimulation

def main():
    algorithmRegistry = {
        "BFS": breadthFirstSearch,
        "UCS": uniformCostSearch,
        "A*": partial(aStarSearch, heuristicType="manhattan"),
        "Greedy": partial(greedyBestFirstSearch, heuristicType="manhattan")
    }

    try:
        for mapName, filePath in mapFiles.items():
            mapMatrix = buildMap(filePath)
            initialFirePositions = createRandomFirePositions(mapMatrix, initialFireCount, simulationSeed) + (configuredFirePositions or [])
            agentPositions = createRandomAgentPositions(mapMatrix, agentCount, simulationSeed, initialFirePositions) + (configuredAgentPositions or [])
            printMap(mapMatrix, mapName)
            print(f"fuego inicial: {initialFirePositions}")

            for algorithmName, algorithm in algorithmRegistry.items():
                result = runSimulation(mapMatrix, agentPositions, algorithm, initialFirePositions, randomSeed=simulationSeed)
                print(
                    f"{algorithmName}: {result['evacuated']}/{len(agentPositions)} evacuados, "
                    f"{result['dead']} bajas, {result['trapped']} atrapados, "
                    f"{result['turns']} turnos, "
                    f"ultimo evacuado en turno {result['evacuationTime']}"
                )

    except ValueError as error:
        print(error)
    except FileNotFoundError:
        print(f"\nERROR: no se encontro el archivo '{filePath}'.")

if __name__ == "__main__":
    main()