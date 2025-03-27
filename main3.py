import tkinter as tk
from tkinter import simpledialog, messagebox
import networkx as nx


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Задача коммивояжера")
        self.root.geometry("1000x600")

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=20, pady=20)

        self.graph_frame = tk.Frame(self.main_frame)
        self.graph_frame.grid(row=0, column=0, padx=20)

        self.canvas = tk.Canvas(self.graph_frame, width=500, height=300, bg="white")
        self.canvas.grid(row=0, column=0)

        self.result_canvas = tk.Canvas(self.graph_frame, width=500, height=300, bg="white")
        self.result_canvas.grid(row=0, column=1, padx=20)

        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)

        self.nn_button = tk.Button(self.control_frame, text="Найти путь (метод ближайшего соседа)", command=lambda: self.solve_tsp(method="nearest_neighbor"))
        self.nn_button.grid(row=0, column=0, padx=5)

        self.mst_button = tk.Button(self.control_frame, text="Построить минимальный остов", command=lambda: self.solve_tsp(method="mst"))
        self.mst_button.grid(row=0, column=1, padx=5)

        self.clear_button = tk.Button(self.control_frame, text="Очистить граф", command=self.clear_graph)
        self.clear_button.grid(row=0, column=2, padx=5)

        self.output_label = tk.Label(self.control_frame, text="Общая длина: ")
        self.output_label.grid(row=1, column=0, columnspan=3)

        self.graph = nx.DiGraph()
        self.nodes = []
        self.selected_node = None

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
        self.draw_graph()

    def add_edge(self, node):
        if self.selected_node is None:
            self.selected_node = node
        else:
            if self.selected_node != node:
                first_node = self.selected_node
                second_node = node
                weight = simpledialog.askinteger("Вес ребра", "Введите вес ребра:")

                if weight is not None and weight > 0:
                    if not self.graph.has_edge(first_node, second_node):
                        self.graph.add_edge(first_node, second_node, weight=weight)
                    else:
                        messagebox.showinfo("Информация", "Это ребро уже существует, обновляем вес.")
                        self.graph[first_node][second_node]['weight'] = weight

                self.selected_node = None
                self.draw_graph()

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

    def nearest_neighbor_tsp(self, start_node):
        """
        Метод ближайшего соседа для решения задачи коммивояжера.
        """
        unvisited = set(self.graph.nodes)
        unvisited.remove(start_node)
        path = [start_node]
        current_node = start_node
        total_distance = 0

        while unvisited:
            nearest_node = None
            min_distance = float('inf')

            # Ищем ближайшего соседа
            for neighbor in self.graph.neighbors(current_node):
                if neighbor in unvisited:
                    distance = self.graph[current_node][neighbor]['weight']
                    if distance < min_distance:
                        min_distance = distance
                        nearest_node = neighbor

            if nearest_node is None:
                # Если нет доступных соседей, возвращаемся в начальную точку
                if self.graph.has_edge(current_node, start_node):
                    total_distance += self.graph[current_node][start_node]['weight']
                    path.append(start_node)
                break

            path.append(nearest_node)
            unvisited.remove(nearest_node)
            total_distance += min_distance
            current_node = nearest_node

        return path, total_distance

    def minimum_spanning_tree(self):
        """
        Построение минимального остовного дерева (MST) с помощью алгоритма Крускала.
        """
        # Преобразуем ориентированный граф в неориентированный для MST
        undirected_graph = self.graph.to_undirected()
        mst = nx.minimum_spanning_tree(undirected_graph)
        return mst

    def solve_tsp(self, method="nearest_neighbor"):
        if len(self.graph.nodes) < 2:
            messagebox.showerror("Ошибка", "Граф должен содержать хотя бы 2 вершины")
            return

        if method == "nearest_neighbor":
            # Метод ближайшего соседа
            start_node = 0  # Начинаем с первой вершины
            shortest_path, min_distance = self.nearest_neighbor_tsp(start_node)

            if not shortest_path:
                messagebox.showerror("Ошибка", "Не удалось найти путь методом ближайшего соседа")
                return

        elif method == "mst":
            # Минимальный остов
            mst = self.minimum_spanning_tree()
            self.output_label.config(text="Минимальный остов построен")
            self.draw_mst(mst)
            return

        self.output_label.config(text=f"Общая длина: {min_distance}")
        self.result_canvas.delete("all")
        pos = nx.get_node_attributes(self.graph, 'pos')

        # Отображение оптимального пути на result_canvas
        for i in range(len(shortest_path) - 1):
            x1, y1 = pos[shortest_path[i]]
            x2, y2 = pos[shortest_path[i + 1]]
            dx, dy = (x2 - x1) * 0.1, (y2 - y1) * 0.1
            self.result_canvas.create_line(x1 + dx, y1 + dy, x2 - dx, y2 - dy, fill="green", width=3, arrow=tk.LAST)
            self.result_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=str(
                self.graph.get_edge_data(shortest_path[i], shortest_path[i + 1])['weight']), fill="red")

        # Показать путь обратно к начальной точке
        x1, y1 = pos[shortest_path[-1]]
        x2, y2 = pos[shortest_path[0]]
        dx, dy = (x2 - x1) * 0.1, (y2 - y1) * 0.1
        self.result_canvas.create_line(x1 + dx, y1 + dy, x2 - dx, y2 - dy, fill="green", width=3, arrow=tk.LAST)
        self.result_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=str(
            self.graph.get_edge_data(shortest_path[-1], shortest_path[0])['weight']), fill="red")

        # Отображаем вершины на итоговом графе
        for node, (x, y) in pos.items():
            self.result_canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="orange")
            self.result_canvas.create_text(x, y, text=str(node), fill="black")

    def draw_mst(self, mst):
        """
        Отображение минимального остовного дерева на result_canvas.
        """
        self.result_canvas.delete("all")
        pos = nx.get_node_attributes(self.graph, 'pos')

        for edge in mst.edges(data=True):
            node1, node2, data = edge
            weight = data.get('weight', 0)
            x1, y1 = pos[node1]
            x2, y2 = pos[node2]

            dx, dy = (x2 - x1), (y2 - y1)
            length = (dx ** 2 + dy ** 2) ** 0.5
            unit_dx, unit_dy = dx / length, dy / length

            arrow_dx, arrow_dy = unit_dx * 15, unit_dy * 15
            text_dx, text_dy = unit_dx * 20, unit_dy * 20

            self.result_canvas.create_line(
                x1 + arrow_dx, y1 + arrow_dy, x2 - arrow_dx, y2 - arrow_dy,
                fill="green", width=2
            )

            text_x = (x1 + x2) / 2 + text_dx
            text_y = (y1 + y2) / 2 + text_dy

            if abs(dx) > abs(dy):
                text_y += 15 if dy > 0 else -15
            else:
                text_x += 15 if dx > 0 else -15

            self.result_canvas.create_text(
                text_x, text_y, text=str(weight), fill="red", font=("Helvetica", 10, "bold")
            )

        for node, (x, y) in pos.items():
            self.result_canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="orange")
            self.result_canvas.create_text(x, y, text=str(node), fill="black")

    def clear_graph(self):
        self.graph.clear()
        self.nodes = []
        self.selected_node = None
        self.canvas.delete("all")
        self.result_canvas.delete("all")
        self.output_label.config(text="Общая длина: ")


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()



