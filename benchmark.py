import argparse
import csv
from functools import partial
from pathlib import Path
from random import Random

from src.algorithms.blinds import breadthFirstSearch, uniformCostSearch
from src.algorithms.genetics import geneticSearch
from src.algorithms.heuristics import aStarSearch, greedyBestFirstSearch
from src.config import (
	agentCount,
	agentPositions as configuredAgentPositions,
	benchmarkIterations,
	initialFireCount,
	initialFirePositions as configuredFirePositions,
	mapFiles,
	simulationSeed,
)
from src.map_parser import buildMap
from src.simulation import createRandomAgentPositions, createRandomFirePositions, runSimulation


def runBenchmark(iterations=benchmarkIterations, benchmarkSeed=simulationSeed, progressCallback=None):
	if iterations <= 0:
		raise ValueError("ERROR: el benchmark debe ejecutar al menos una iteracion")

	if benchmarkSeed is None:
		benchmarkSeed = Random().randrange(0, 2**32)

	seedGenerator = Random(benchmarkSeed)
	algorithmRegistry = {
		"BFS": breadthFirstSearch,
		"UCS": uniformCostSearch,
		"A*": partial(aStarSearch, heuristicType="manhattan"),
		"Greedy": partial(greedyBestFirstSearch, heuristicType="manhattan"),
		"Genetico": geneticSearch,
	}
	runs = []

	for mapName, filePath in mapFiles.items():
		for iteration in range(1, iterations + 1):
			scenarioSeed = seedGenerator.randrange(0, 2**32)
			scenarioMap = buildMap(filePath)
			initialFirePositions = createRandomFirePositions(scenarioMap, initialFireCount, scenarioSeed) + (configuredFirePositions or [])
			agentPositions = createRandomAgentPositions(scenarioMap, agentCount, scenarioSeed, initialFirePositions) + (configuredAgentPositions or [])

			for algorithmName, algorithm in algorithmRegistry.items():
				simulationMap = buildMap(filePath)
				runAlgorithm = partial(algorithm, randomSeed=scenarioSeed) if algorithmName == "Genetico" else algorithm
				result = runSimulation(simulationMap, agentPositions, runAlgorithm, initialFirePositions, randomSeed=scenarioSeed)
				runs.append(
					{
						"map": mapName,
						"algorithm": algorithmName,
						"iteration": iteration,
						"agents_total": len(agentPositions),
						"agents_evacuated": result["evacuated"],
						"evacuation_time_turns": result["evacuationTime"],
					}
				)

			if progressCallback is not None:
				progressCallback(mapName, iteration, iterations)

	return {
		"iterations": iterations,
		"seed": benchmarkSeed,
		"runs": runs,
	}

def saveBenchmarkCsv(results, outputPath="benchmark_results.csv"):
	fieldnames = (
		"map",
		"algorithm",
		"iteration",
		"agents_total",
		"agents_evacuated",
		"evacuation_time_turns",
	)
	outputPath = Path(outputPath)
	outputPath.parent.mkdir(parents=True, exist_ok=True)

	with outputPath.open("w", newline="", encoding="utf-8-sig") as csvFile:
		writer = csv.DictWriter(csvFile, fieldnames=fieldnames, delimiter=";")
		writer.writeheader()
		writer.writerows(results["runs"])

	return outputPath

def _printResults(results):
	print(f"Corridas guardadas: {len(results['runs'])}")

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--iterations", type=int, default=benchmarkIterations, help="iteraciones por mapa y algoritmo")
	parser.add_argument("--seed", type=int, default=simulationSeed,	help="semilla para reproducir el benchmark")
	parser.add_argument("--output", default="benchmark_results.csv", help="ruta del archivo CSV de resultados")
	arguments = parser.parse_args()
	benchmarkSeed = arguments.seed
	if benchmarkSeed is None:
		benchmarkSeed = Random().randrange(0, 2**32)

	try:
		print(f"Benchmark: {arguments.iterations} iteraciones por mapa y algoritmo; semilla {benchmarkSeed}")
		results = runBenchmark(arguments.iterations, benchmarkSeed, _showProgress)
		_printResults(results)
		outputPath = saveBenchmarkCsv(results, arguments.output)
		print(f"\nResultados guardados en: {outputPath}")
	except ValueError as error:
		print(error)
	except FileNotFoundError as error:
		print(f"\nERROR: no se encontro el archivo '{error.filename}'.")

def _showProgress(mapName, iteration, totalIterations):
	if iteration == 1 or iteration % 10 == 0 or iteration == totalIterations:
		print(f"{mapName}: iteracion {iteration}/{totalIterations}", flush=True)

if __name__ == "__main__":
	main()