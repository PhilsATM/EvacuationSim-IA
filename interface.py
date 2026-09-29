import random
from queue import Empty, Queue
import threading
import tkinter as tk
from functools import partial
from pathlib import Path
from tkinter import messagebox, ttk

from src.algorithms.blinds import breadthFirstSearch, uniformCostSearch
from src.algorithms.genetics import geneticSearch
from src.algorithms.heuristics import aStarSearch, greedyBestFirstSearch
from src.config import (
	agentCount,
	fireSpreadInterval,
	fireSpreadProbability,
	initialFireCount,
	mapFiles,
	maxSimulationTurns,
)
from src.map_parser import buildMap
from src.simulation import (
	createRandomAgentPositions,
	createRandomFirePositions,
	runSimulation,
)


ROOT = Path(__file__).resolve().parent
PALETTE = {
	"background": "#f3f5f2",
	"panel": "#ffffff",
	"ink": "#172923",
	"muted": "#718078",
	"green": "#27745a",
	"green_light": "#e3f0e9",
	"wall": "#34433d",
	"floor": "#eef2ed",
	"aisle": "#dce7df",
	"narrow": "#d6e1db",
	"door": "#e7bc63",
	"exit": "#54a77c",
	"fire": "#df634b",
	"agent": "#286da0",
	"trapped": "#69756e",
}


class EvacuationInterface:
	def __init__(self, root):
		self.root = root
		self.root.title("EvacuationSim | Centro de control")
		self.root.geometry("1320x860")
		self.root.minsize(1080, 720)
		self.preview_job = None
		self.running = False
		self.completion_queue = Queue()
		self.last_results = []
		self.map_name = tk.StringVar(value=next(iter(mapFiles)))
		self.agent_count = tk.StringVar(value=str(agentCount))
		self.fire_count = tk.StringVar(value=str(initialFireCount))
		self.seed = tk.StringVar(value="")
		self.spread_interval = tk.StringVar(value=str(fireSpreadInterval))
		self.spread_probability = tk.StringVar(value=f"{fireSpreadProbability:.2f}")
		self.max_turns = tk.StringVar(
			value="" if maxSimulationTurns is None else str(maxSimulationTurns)
		)
		self.heuristic = tk.StringVar(value="manhattan")
		self.turn_delay = tk.StringVar(value="220")
		self.map_info = tk.StringVar(value="")
		self.status = tk.StringVar(value="Listo para preparar la evacuación")
		self.summary_vars = {
			"evacuated": tk.StringVar(value="—"),
			"survival": tk.StringVar(value="—"),
			"turns": tk.StringVar(value="—"),
			"leader": tk.StringVar(value="Sin resultados"),
		}
		self._configure_styles()
		self._build_layout()
		self._watch_preview_inputs()
		self.root.after(100, self.refresh_preview)
		self.root.after(50, self._process_completions)

	def _configure_styles(self):
		style = ttk.Style()
		style.theme_use("clam")
		style.configure("TFrame", background=PALETTE["background"])
		style.configure("Panel.TFrame", background=PALETTE["panel"])
		style.configure("TLabel", background=PALETTE["background"], foreground=PALETTE["ink"], font=("Segoe UI", 10))
		style.configure("Panel.TLabel", background=PALETTE["panel"], foreground=PALETTE["ink"], font=("Segoe UI", 10))
		style.configure("Muted.TLabel", background=PALETTE["panel"], foreground=PALETTE["muted"], font=("Segoe UI", 9))
		style.configure("Title.TLabel", background=PALETTE["background"], foreground=PALETTE["ink"], font=("Segoe UI", 23, "bold"))
		style.configure("Section.TLabel", background=PALETTE["panel"], foreground=PALETTE["ink"], font=("Segoe UI", 12, "bold"))
		style.configure("Metric.TLabel", background=PALETTE["panel"], foreground=PALETTE["ink"], font=("Segoe UI", 19, "bold"))
		style.configure("TButton", font=("Segoe UI", 10), padding=(11, 8))
		style.configure("Accent.TButton", background=PALETTE["green"], foreground="#ffffff", font=("Segoe UI", 10, "bold"))
		style.map("Accent.TButton", background=[("active", "#1f604a"), ("disabled", "#9daf9f")])
		style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground=PALETTE["ink"], rowheight=33, font=("Segoe UI", 10), borderwidth=0)
		style.configure("Treeview.Heading", background="#edf2ed", foreground=PALETTE["muted"], font=("Segoe UI", 9, "bold"), padding=(8, 9), borderwidth=0)
		style.map("Treeview", background=[("selected", PALETTE["green_light"])], foreground=[("selected", PALETTE["ink"])])

	def _build_layout(self):
		outer = ttk.Frame(self.root, padding=(26, 20, 26, 16))
		outer.pack(fill="both", expand=True)
		header = ttk.Frame(outer)
		header.pack(fill="x", pady=(0, 18))
		ttk.Label(header, text="CENTRO DE CONTROL   /   EVACUACIÓN", font=("Segoe UI", 9, "bold"), foreground=PALETTE["green"], background=PALETTE["background"]).pack(anchor="w")
		ttk.Label(header, text="Simulador de evacuación", style="Title.TLabel").pack(anchor="w", pady=(4, 0))

		body = ttk.Frame(outer)
		body.pack(fill="both", expand=True)
		body.columnconfigure(1, weight=1)
		body.rowconfigure(0, weight=1)
		self.controls = ttk.Frame(body, style="Panel.TFrame", padding=18, width=278)
		self.controls.grid(row=0, column=0, sticky="nsw", padx=(0, 16))
		self.controls.grid_propagate(False)
		self._build_controls()

		content = ttk.Frame(body)
		content.grid(row=0, column=1, sticky="nsew")
		content.columnconfigure(0, weight=1)
		content.rowconfigure(0, weight=3)
		content.rowconfigure(2, weight=2)
		self._build_map_panel(content)
		self._build_summary(content)
		self._build_results(content)

		footer = ttk.Frame(outer)
		footer.pack(fill="x", pady=(12, 0))
		ttk.Label(footer, textvariable=self.status, foreground=PALETTE["muted"], background=PALETTE["background"], font=("Segoe UI", 9)).pack(side="left")
		ttk.Label(footer, text="Python · Tkinter · Sin dependencias externas", foreground=PALETTE["muted"], background=PALETTE["background"], font=("Segoe UI", 9)).pack(side="right")

	def _field_label(self, parent, text):
		ttk.Label(parent, text=text, style="Muted.TLabel").pack(anchor="w", pady=(11, 4))

	def _entry(self, parent, variable, **kwargs):
		entry = ttk.Entry(parent, textvariable=variable, **kwargs)
		entry.pack(fill="x")
		return entry

	def _build_controls(self):
		ttk.Label(self.controls, text="Configuración", style="Section.TLabel").pack(anchor="w")
		self._field_label(self.controls, "Mapa")
		map_picker = ttk.Combobox(self.controls, textvariable=self.map_name, values=list(mapFiles), state="readonly")
		map_picker.pack(fill="x")
		map_picker.bind("<<ComboboxSelected>>", lambda _event: self.refresh_preview())

		self._field_label(self.controls, "Agentes")
		ttk.Spinbox(self.controls, from_=1, to=500, textvariable=self.agent_count, width=8).pack(anchor="w")
		self._field_label(self.controls, "Focos de incendio")
		ttk.Spinbox(self.controls, from_=0, to=50, textvariable=self.fire_count, width=8).pack(anchor="w")
		self._field_label(self.controls, "Semilla aleatoria")
		self._entry(self.controls, self.seed)
		ttk.Label(self.controls, text="Vacío = semilla nueva", style="Muted.TLabel").pack(anchor="w", pady=(3, 0))

		self._field_label(self.controls, "Propagación del fuego")
		fire_row = ttk.Frame(self.controls, style="Panel.TFrame")
		fire_row.pack(fill="x")
		ttk.Spinbox(fire_row, from_=1, to=100, textvariable=self.spread_interval, width=6).pack(side="left")
		ttk.Label(fire_row, text="turnos", style="Muted.TLabel").pack(side="left", padx=(5, 12))
		tk.Spinbox(fire_row, from_=0, to=1, increment=0.05, format="%.2f", textvariable=self.spread_probability, width=6).pack(side="left")
		ttk.Label(fire_row, text="prob.", style="Muted.TLabel").pack(side="left", padx=(5, 0))

		self._field_label(self.controls, "Límite de turnos")
		self._entry(self.controls, self.max_turns)
		ttk.Label(self.controls, text="Vacío = sin límite", style="Muted.TLabel").pack(anchor="w", pady=(3, 0))
		self._field_label(self.controls, "Pausa por turno (ms)")
		ttk.Spinbox(self.controls, from_=0, to=1500, increment=50, textvariable=self.turn_delay, width=8).pack(anchor="w")
		self._field_label(self.controls, "Heurística")
		ttk.Combobox(self.controls, textvariable=self.heuristic, values=("manhattan", "euclidean", "chebyshev"), state="readonly").pack(fill="x")

		ttk.Separator(self.controls).pack(fill="x", pady=16)
		self.compare_button = ttk.Button(self.controls, text="▶  Comparar algoritmos", style="Accent.TButton", command=self.run_comparison)
		self.compare_button.pack(fill="x")
		self.selected_algorithm = tk.StringVar(value="A*")
		ttk.Combobox(self.controls, textvariable=self.selected_algorithm, values=("BFS", "UCS", "A*", "Greedy", "Genético"), state="readonly").pack(fill="x", pady=(9, 7))
		self.single_button = ttk.Button(self.controls, text="Ejecutar selección", command=self.run_selected)
		self.single_button.pack(fill="x")

		ttk.Separator(self.controls).pack(fill="x", pady=16)
		ttk.Label(self.controls, text="Leyenda", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
		for symbol, color, label in (("■", PALETTE["wall"], "Muro"), ("·", PALETTE["floor"], "Espacio abierto"), ("=", PALETTE["aisle"], "Pasillo"), ("D", PALETTE["door"], "Puerta"), ("S", PALETTE["exit"], "Salida"), ("●", PALETTE["agent"], "Agentes"), ("F", PALETTE["fire"], "Fuego")):
			line = ttk.Frame(self.controls, style="Panel.TFrame")
			line.pack(fill="x", pady=2)
			ttk.Label(line, text=symbol, foreground=color, background=PALETTE["panel"], font=("Segoe UI", 12, "bold"), width=3).pack(side="left")
			ttk.Label(line, text=label, style="Muted.TLabel").pack(side="left")

	def _build_map_panel(self, parent):
		panel = ttk.Frame(parent, style="Panel.TFrame", padding=(16, 14, 16, 12))
		panel.grid(row=0, column=0, sticky="nsew")
		panel.rowconfigure(1, weight=1)
		panel.columnconfigure(0, weight=1)
		heading = ttk.Frame(panel, style="Panel.TFrame")
		heading.grid(row=0, column=0, sticky="ew", pady=(0, 10))
		ttk.Label(heading, text="Vista del mapa", style="Section.TLabel").pack(side="left")
		ttk.Label(heading, textvariable=self.map_info, style="Muted.TLabel").pack(side="right")
		self.map_canvas = tk.Canvas(panel, background="#f8faf7", highlightthickness=0, height=350)
		self.map_canvas.grid(row=1, column=0, sticky="nsew")

	def _build_summary(self, parent):
		row = ttk.Frame(parent)
		row.grid(row=1, column=0, sticky="ew", pady=12)
		for column in range(4):
			row.columnconfigure(column, weight=1)
		for column, (label, key) in enumerate((("EVACUADOS", "evacuated"), ("SUPERVIVENCIA", "survival"), ("TURNOS", "turns"), ("MEJOR RESULTADO", "leader"))):
			panel = ttk.Frame(row, style="Panel.TFrame", padding=(13, 10))
			panel.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 7, 0))
			ttk.Label(panel, text=label, style="Muted.TLabel").pack(anchor="w")
			style = "Metric.TLabel" if key != "leader" else "Panel.TLabel"
			ttk.Label(panel, textvariable=self.summary_vars[key], style=style).pack(anchor="w", pady=(4, 0))

	def _build_results(self, parent):
		panel = ttk.Frame(parent, style="Panel.TFrame", padding=(16, 13, 16, 10))
		panel.grid(row=2, column=0, sticky="nsew")
		panel.rowconfigure(1, weight=1)
		panel.columnconfigure(0, weight=1)
		ttk.Label(panel, text="Resultados por algoritmo", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 9))
		columns = ("algorithm", "evacuated", "dead", "trapped", "turns", "survival")
		self.results_table = ttk.Treeview(panel, columns=columns, show="headings", height=5)
		for column, title, width in (("algorithm", "ALGORITMO", 150), ("evacuated", "EVACUADOS", 100), ("dead", "BAJAS", 85), ("trapped", "ATRAPADOS", 95), ("turns", "TURNOS", 85), ("survival", "SUPERVIVENCIA", 120)):
			self.results_table.heading(column, text=title)
			self.results_table.column(column, width=width, anchor="w" if column == "algorithm" else "center")
		self.results_table.tag_configure("best", background=PALETTE["green_light"])
		self.results_table.grid(row=1, column=0, sticky="nsew")

	def _watch_preview_inputs(self):
		for variable in (self.agent_count, self.fire_count, self.seed):
			variable.trace_add("write", self.schedule_preview)

	def schedule_preview(self, *_args):
		if self.preview_job is not None:
			self.root.after_cancel(self.preview_job)
		self.preview_job = self.root.after(300, self.refresh_preview)

	def refresh_preview(self):
		self.preview_job = None
		try:
			matrix = self._load_map()
			seed_text = self.seed.get().strip()
			preview_seed = int(seed_text) if seed_text else 42
			fires = createRandomFirePositions(matrix, self._read_int(self.fire_count, "focos", 0), preview_seed)
			agents = createRandomAgentPositions(matrix, self._read_int(self.agent_count, "agentes", 1), preview_seed, fires)
		except (ValueError, OSError) as error:
			self.map_info.set("Revisa los parámetros")
			self.map_canvas.delete("all")
			self.map_canvas.create_text(20, 24, anchor="nw", text=str(error), fill=PALETTE["fire"], font=("Segoe UI", 10), width=700)
			return
		self._draw_map(matrix, agents, fires)
		self.map_info.set(f"{len(matrix[0])} × {len(matrix)} celdas   ·   {len(agents)} agentes   ·   {len(fires)} focos")

	def _draw_map(self, matrix, agents, fires):
		self.map_canvas.delete("all")
		self.map_canvas.update_idletasks()
		rows, columns = len(matrix), len(matrix[0])
		cell_size = max(12, min(28, (self.map_canvas.winfo_width() - 32) / columns, (self.map_canvas.winfo_height() - 28) / rows))
		map_width, map_height = columns * cell_size, rows * cell_size
		left = max(12, (self.map_canvas.winfo_width() - map_width) / 2)
		top = max(12, (self.map_canvas.winfo_height() - map_height) / 2)
		agent_counts = {}
		agent_colors = {}
		for agent in agents:
			if len(agent) == 2:
				x, y = agent
				status = "active"
			else:
				x, y, status = agent
			if status in ("dead", "evacuated"):
				continue
			position = (x, y)
			agent_counts[position] = agent_counts.get(position, 0) + 1
			agent_colors[position] = PALETTE["trapped"] if status == "trapped" else PALETTE["agent"]
		fire_positions = set(fires)
		colors = {"#": PALETTE["wall"], ".": PALETTE["floor"], "=": PALETTE["aisle"], "-": PALETTE["narrow"], ";": PALETTE["door"], "E": PALETTE["exit"]}
		for y, row in enumerate(matrix):
			for x, cell in enumerate(row):
				x1, y1 = left + x * cell_size, top + y * cell_size
				x2, y2 = x1 + cell_size, y1 + cell_size
				self.map_canvas.create_rectangle(x1, y1, x2, y2, fill=colors[cell.cellType], outline="#d4ded5", width=0.7)
				if cell.cellType == "E":
					self.map_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="S", fill="#ffffff", font=("Segoe UI", max(7, int(cell_size * 0.55)), "bold"))
				elif cell.cellType == ";":
					self.map_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="D", fill="#54411c", font=("Segoe UI", max(7, int(cell_size * 0.5)), "bold"))
				position = (x, y)
				if position in fire_positions:
					self.map_canvas.create_oval(x1 + 2, y1 + 2, x2 - 2, y2 - 2, fill=PALETTE["fire"], outline="", tags=("fire-cell",))
					self.map_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="F", fill="#ffffff", font=("Segoe UI", max(7, int(cell_size * 0.5)), "bold"))
				elif position in agent_counts:
					self.map_canvas.create_oval(x1 + 3, y1 + 3, x2 - 3, y2 - 3, fill=agent_colors[position], outline="", tags=("agent-cell",))
					if agent_counts[position] > 1:
						self.map_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=str(agent_counts[position]), fill="#ffffff", font=("Segoe UI", max(7, int(cell_size * 0.4)), "bold"))

	def _load_map(self):
		map_path = ROOT / mapFiles[self.map_name.get()]
		return buildMap(str(map_path))

	@staticmethod
	def _read_int(variable, label, minimum):
		try:
			value = int(variable.get())
		except ValueError as error:
			raise ValueError(f"El valor de {label} debe ser un número entero.") from error
		if value < minimum:
			raise ValueError(f"El valor de {label} debe ser al menos {minimum}.")
		return value

	def _get_settings(self):
		seed_text = self.seed.get().strip()
		seed = random.Random().randrange(0, 1_000_000) if not seed_text else int(seed_text)
		interval = self._read_int(self.spread_interval, "el intervalo", 1)
		probability = float(self.spread_probability.get())
		if not 0 <= probability <= 1:
			raise ValueError("La probabilidad debe estar entre 0 y 1.")
		max_turns = self.max_turns.get().strip()
		max_turns = None if not max_turns else self._read_int(self.max_turns, "el límite de turnos", 1)
		return {
			"agents": self._read_int(self.agent_count, "los agentes", 1),
			"fires": self._read_int(self.fire_count, "los focos", 0),
			"seed": seed,
			"interval": interval,
			"probability": probability,
			"max_turns": max_turns,
			"turn_delay": self._read_int(self.turn_delay, "la pausa por turno", 0),
			"heuristic": self.heuristic.get(),
		}

	def run_comparison(self):
		self._start_run(("BFS", "UCS", "A*", "Greedy", "Genético"))

	def run_selected(self):
		self._start_run((self.selected_algorithm.get(),))

	def _start_run(self, algorithm_names):
		if self.running:
			return
		try:
			settings = self._get_settings()
			matrix = self._load_map()
			fires = createRandomFirePositions(matrix, settings["fires"], settings["seed"])
			agents = createRandomAgentPositions(matrix, settings["agents"], settings["seed"], fires)
			map_path = str(ROOT / mapFiles[self.map_name.get()])
		except (ValueError, OSError, KeyError) as error:
			messagebox.showerror("Configuración no válida", str(error), parent=self.root)
			return

		self.seed.set(str(settings["seed"]))
		self.refresh_preview()
		self.running = True
		self._current_agents = len(agents)
		self._current_map = matrix
		for item in self.results_table.get_children():
			self.results_table.delete(item)
		self.summary_vars["evacuated"].set("—")
		self.summary_vars["survival"].set("—")
		self.summary_vars["turns"].set("—")
		self.summary_vars["leader"].set("En curso")
		self.compare_button.state(["disabled"])
		self.single_button.state(["disabled"])
		self.status.set("Simulando con la misma distribución inicial para cada algoritmo…")
		self.map_info.set("Preparando   ·   TURNO 0")
		thread = threading.Thread(target=self._simulate, args=(algorithm_names, settings, agents, fires, map_path), daemon=True)
		thread.start()

	def _process_completions(self):
		try:
			kind, payload, seed = self.completion_queue.get_nowait()
		except Empty:
			pass
		else:
			if kind == "turn":
				self._show_turn(payload[0], payload[1])
			elif kind == "algorithm":
				self.status.set(f"Ejecutando {payload}…")
			elif kind == "error":
				self._finish_error(payload)
			else:
				self._show_results(payload, seed)
		self.root.after(50, self._process_completions)

	def _show_turn(self, algorithm_name, snapshot):
		agents = snapshot["agents"]
		evacuees = sum(agent[2] == "evacuated" for agent in agents)
		dead = sum(agent[2] == "dead" for agent in agents)
		trapped = sum(agent[2] == "trapped" for agent in agents)
		active = sum(agent[2] == "active" for agent in agents)
		self._draw_map(self._current_map, agents, snapshot["fires"])
		self.map_info.set(f"{algorithm_name}   ·   TURNO {snapshot['turn']}")
		self.status.set(f"{algorithm_name}   ·   Activos {active}   ·   Evacuados {evacuees}   ·   Bajas {dead}   ·   Atrapados {trapped}   ·   Fuego {len(snapshot['fires'])}")

	def _simulate(self, algorithm_names, settings, agents, fires, map_path):
		registry = {
			"BFS": breadthFirstSearch,
			"UCS": uniformCostSearch,
			"A*": partial(aStarSearch, heuristicType=settings["heuristic"]),
			"Greedy": partial(greedyBestFirstSearch, heuristicType=settings["heuristic"]),
			"Genético": partial(geneticSearch, randomSeed=settings["seed"]),
		}
		results = []
		try:
			for name in algorithm_names:
				self.completion_queue.put(("algorithm", name, None))
				def report_turn(snapshot):
					self.completion_queue.put(("turn", (name, snapshot), None))
					if settings["turn_delay"]:
						threading.Event().wait(settings["turn_delay"] / 1000)

				result = runSimulation(
					buildMap(map_path),
					agents,
					registry[name],
					fires,
					fireSpreadInterval=settings["interval"],
					spreadProbability=settings["probability"],
					maxTurns=settings["max_turns"],
					randomSeed=settings["seed"],
					turnCallback=report_turn,
				)
				results.append((name, result))
		except Exception as error:
			self.completion_queue.put(("error", str(error), None))
			return
		self.completion_queue.put(("success", results, settings["seed"]))

	def _show_results(self, results, seed):
		self.running = False
		self.compare_button.state(["!disabled"])
		self.single_button.state(["!disabled"])
		self.last_results = results
		for item in self.results_table.get_children():
			self.results_table.delete(item)
		best = max((result["survivalRate"] for _, result in results), default=0)
		for name, result in results:
			tags = ("best",) if result["survivalRate"] == best else ()
			self.results_table.insert("", "end", values=(name, result["evacuated"], result["dead"], result["trapped"], result["turns"], f"{result['survivalRate']:.1f}%"), tags=tags)
		if results:
			winner, result = max(results, key=lambda item: (item[1]["survivalRate"], item[1]["evacuated"], -(item[1]["evacuationTime"] or 0)))
			total = self._current_agents
			self.summary_vars["evacuated"].set(f"{result['evacuated']} / {total}")
			self.summary_vars["survival"].set(f"{result['survivalRate']:.1f}%")
			self.summary_vars["turns"].set(str(result["turns"]))
			self.summary_vars["leader"].set(winner)
		self.status.set(f"Simulación completada   ·   semilla {seed}")

	def _finish_error(self, error):
		self.running = False
		self.compare_button.state(["!disabled"])
		self.single_button.state(["!disabled"])
		self.status.set("La simulación no pudo completarse")
		messagebox.showerror("Error en la simulación", error, parent=self.root)


def main():
	root = tk.Tk()
	EvacuationInterface(root)
	root.mainloop()


if __name__ == "__main__":
	main()