import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import networkx as nx
import time
import math
import random

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Задача коммивояжера (NN + RNN)")
        self.root.geometry("1400x800")

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=20, pady=20)

        self.graph_frame = tk.Frame(self.main_frame)
        self.graph_frame.grid(row=0, column=0, padx=20)

        self.canvas = tk.Canvas(self.graph_frame, width=700, height=400, bg="white")
        self.canvas.grid(row=0, column=0)

        self.result_canvas = tk.Canvas(self.graph_frame, width=700, height=400, bg="white")
        self.result_canvas.grid(row=0, column=1, padx=20)

        self.table_frame = tk.Frame(self.main_frame)
        self.table_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self.table_frame, columns=("From", "To", "Weight"), show="headings")
        self.tree.heading("From", text="Из")
        self.tree.heading("To", text="В")
        self.tree.heading("Weight", text="Вес")
        self.tree.pack(side="left", fill="both", expand=True)

        scroll_y = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        scroll_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll_y.set)

        scroll_x = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        scroll_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=scroll_x.set)

        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)

        self.calc_button = tk.Button(self.control_frame, text="Найти оптимальный путь (NN)", command=self.run_nn)
        self.calc_button.grid(row=0, column=0, padx=5)

        self.rnn_button = tk.Button(self.control_frame, text="Запустить RNN (все вершины)", command=self.run_rnn)
        self.rnn_button.grid(row=0, column=1, padx=5)

        self.clear_button = tk.Button(self.control_frame, text="Очистить граф", command=self.clear_graph)
        self.clear_button.grid(row=0, column=2, padx=5)

        self.cencelator_button = tk.Button(self.control_frame, text="Отменить", command=self.cencelator)
        self.cencelator_button.grid(row=0, column=3, padx=5)

        self.output_label = tk.Label(self.control_frame, text="Общая длина: ")
        self.output_label.grid(row=1, column=0, columnspan=4)

        self.time_label = tk.Label(self.control_frame, text="Время выполнения: ")
        self.time_label.grid(row=2, column=0, columnspan=4)

        self.graph = nx.DiGraph()
        self.nodes = []
        self.selected_node = None
        self.history = []

        self.canvas.bind("<Button-1>", self.handle_click)

    def handle_click(self, event):
        for node, (x, y) in enumerate(self.nodes):
            if (x - event.x) ** 2 + (y - event.y) ** 2 <= 100:
                self.add_edge(node)
                return
        self.add_node(event)

    def add_node(self, event):
        node_id = len(self.nodes)
        self.nodes.append((event.x, event.y))
        self.graph.add_node(node_id, pos=(event.x, event.y))
        self.history.append(("add_node", node_id))
        self.draw_graph()

    def add_edge(self, node):
        if self.selected_node is None:
            self.selected_node = node
        else:
            if self.selected_node != node:
                first_node = self.selected_node
                second_node = node
                weight = simpledialog.askinteger("Вес ребра", "Введите вес ребра:")

                if weight is not None:
                    if not self.graph.has_edge(first_node, second_node):
                        self.graph.add_edge(first_node, second_node, weight=weight)
                        self.history.append(("add_edge", (first_node, second_node, weight)))
                        self.update_table(first_node, second_node, weight)
                    else:
                        old_weight = self.graph[first_node][second_node]['weight']
                        self.graph[first_node][second_node]['weight'] = weight
                        self.history.append(("update_edge", (first_node, second_node, old_weight)))
                        self.update_table(first_node, second_node, weight)
                    self.selected_node = None
                    self.draw_graph()

    def update_table(self, from_node, to_node, weight):
        self.tree.insert("", "end", values=(from_node, to_node, weight))

    def draw_graph(self):
        self.canvas.delete("all")
        pos = nx.get_node_attributes(self.graph, 'pos')

        for edge in self.graph.edges(data=True):
            node1, node2, data = edge
            weight = data.get('weight', 0)
            x1, y1 = pos[node1]
            x2, y2 = pos[node2]

            dx, dy = (x2 - x1), (y2 - y1)
            length = (dx ** 2 + dy ** 2) ** 0.5
            unit_dx, unit_dy = dx / length, dy / length

            arrow_dx, arrow_dy = unit_dx * 15, unit_dy * 15
            text_dx, text_dy = unit_dx * 20, unit_dy * 20

            self.canvas.create_line(
                x1 + arrow_dx, y1 + arrow_dy, x2 - arrow_dx, y2 - arrow_dy,
                fill="blue", width=2, arrow=tk.LAST
            )

            text_x = (x1 + x2) / 2 + text_dx
            text_y = (y1 + y2) / 2 + text_dy

            if abs(dx) > abs(dy):
                text_y += 15 if dy > 0 else -15
            else:
                text_x += 15 if dx > 0 else -15

            self.canvas.create_text(
                text_x, text_y, text=str(weight), fill="red", font=("Helvetica", 10, "bold")
            )

        for node, (x, y) in pos.items():
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="orange")
            self.canvas.create_text(x, y, text=str(node), fill="black")

    def cencelator(self):
        """Отмена последнего действия."""
        if not self.history:
            messagebox.showinfo("Информация", "Нет действий для отмены")
            return

        last_action = self.history.pop()
        action_type, data = last_action

        if action_type == "add_node":
            node_id = data
            self.graph.remove_node(node_id)
            self.nodes.pop(node_id)
        elif action_type == "add_edge":
            first_node, second_node, weight = data
            self.graph.remove_edge(first_node, second_node)
            self.remove_from_table(first_node, second_node)
        elif action_type == "update_edge":
            first_node, second_node, old_weight = data
            self.graph[first_node][second_node]['weight'] = old_weight
            self.update_table(first_node, second_node, old_weight)

        self.draw_graph()

    def remove_from_table(self, from_node, to_node):
        """Удаляет ребро из таблицы."""
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values and int(values[0]) == from_node and int(values[1]) == to_node:
                self.tree.delete(item)
                break

    def nearest_neighbor(self, start_node):
        """Классический алгоритм ближайшего соседа."""
        path = [start_node]
        unvisited = set(self.graph.nodes) - {start_node}

        while unvisited:
            last_node = path[-1]
            nearest_node = None
            min_weight = float('inf')

            for node in unvisited:
                if self.graph.has_edge(last_node, node):
                    weight = self.graph[last_node][node]['weight']
                    if weight < min_weight:
                        nearest_node = node
                        min_weight = weight

            if nearest_node is None:
                return None

            path.append(nearest_node)
            unvisited.remove(nearest_node)

        if not self.graph.has_edge(path[-1], path[0]):
            return None

        return path

    def run_nn(self):
        """Запуск NN со случайной начальной вершиной."""
        if len(self.graph.nodes) < 2:
            messagebox.showerror("Ошибка", "Граф должен содержать хотя бы 2 вершины")
            return

        start_time = time.perf_counter()
        start_node = random.choice(list(self.graph.nodes))  # Можно выбрать любую вершину
        path = self.nearest_neighbor(start_node)

        if path:
            distance = self.calculate_path_distance(path)
            elapsed = time.perf_counter() - start_time
            self.output_label.config(text=f"Общая длина (NN): {distance}")
            self.time_label.config(text=f"Время выполнения: {elapsed:.4f} сек")
            self.draw_result(path)
        else:
            messagebox.showinfo("Информация", "Путь не найден")

    def run_rnn(self):
        """Repetitive Nearest Neighbor: запуск NN для всех вершин."""
        if len(self.graph.nodes) < 2:
            messagebox.showerror("Ошибка", "Граф должен содержать хотя бы 2 вершины")
            return

        start_time = time.perf_counter()
        best_path = None
        best_distance = float('inf')

        for start_node in self.graph.nodes:
            path = self.nearest_neighbor(start_node)
            if path:
                distance = self.calculate_path_distance(path)
                if distance < best_distance:
                    best_path = path
                    best_distance = distance

        if best_path:
            elapsed = time.perf_counter() - start_time
            self.output_label.config(text=f"Общая длина (RNN): {best_distance}")
            self.time_label.config(text=f"Время выполнения: {elapsed:.4f} сек")
            self.draw_result(best_path)
        else:
            messagebox.showinfo("Информация", "Путей нет")

    def calculate_path_distance(self, path):
        """Вычисляет длину гамильтонова цикла."""
        distance = 0
        for i in range(len(path) - 1):
            edge_data = self.graph.get_edge_data(path[i], path[i + 1])
            if edge_data is None:
                return float('inf')
            distance += edge_data['weight']
        edge_data = self.graph.get_edge_data(path[-1], path[0])
        if edge_data is None:
            return float('inf')
        distance += edge_data['weight']
        return distance

    def draw_result(self, path):
        """Отрисовывает результат на правом холсте с направлениями стрелок."""
        self.result_canvas.delete("all")
        pos = nx.get_node_attributes(self.graph, 'pos')

        # Рисуем рёбра пути с направлениями
        for i in range(len(path)):
            x1, y1 = pos[path[i]]
            x2, y2 = pos[path[(i + 1) % len(path)]]  # Замыкаем цикл

            dx, dy = x2 - x1, y2 - y1
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length == 0:
                continue

            # Нормализуем вектор направления
            unit_dx, unit_dy = dx / length, dy / length

            # Координаты для стрелки (отступаем от узлов)
            arrow_start_x = x1 + unit_dx * 15
            arrow_start_y = y1 + unit_dy * 15
            arrow_end_x = x2 - unit_dx * 15
            arrow_end_y = y2 - unit_dy * 15

            # Рисуем линию со стрелкой
            self.result_canvas.create_line(
                arrow_start_x, arrow_start_y,
                arrow_end_x, arrow_end_y,
                fill="green", width=3, arrow=tk.LAST
            )

            # Подпись веса ребра
            text_x = (x1 + x2) / 2 + unit_dx * 20
            text_y = (y1 + y2) / 2 + unit_dy * 20

            # Смещаем текст для лучшей читаемости
            if abs(dx) > abs(dy):
                text_y += 15 if dy > 0 else -15
            else:
                text_x += 15 if dx > 0 else -15

            weight = self.graph[path[i]][path[(i + 1) % len(path)]]['weight']
            self.result_canvas.create_text(
                text_x, text_y,
                text=str(weight),
                fill="red", font=("Helvetica", 10, "bold")
            )

        # Рисуем вершины
        for node, (x, y) in pos.items():
            self.result_canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="orange")
            self.result_canvas.create_text(x, y, text=str(node), fill="black")


    def clear_graph(self):
        self.graph.clear()
        self.nodes = []
        self.selected_node = None
        self.history = []
        self.canvas.delete("all")
        self.result_canvas.delete("all")
        self.output_label.config(text="Общая длина: ")
        self.time_label.config(text="Время выполнения: ")
        self.tree.delete(*self.tree.get_children())

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()