import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import networkx as nx


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Задача коммивояжера")
        self.root.geometry("1200x600")  # Увеличили ширину окна для таблицы

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=20, pady=20)

        self.graph_frame = tk.Frame(self.main_frame)
        self.graph_frame.grid(row=0, column=0, padx=20)

        self.canvas = tk.Canvas(self.graph_frame, width=500, height=300, bg="white")
        self.canvas.grid(row=0, column=0)

        self.result_canvas = tk.Canvas(self.graph_frame, width=500, height=300, bg="white")
        self.result_canvas.grid(row=0, column=1, padx=20)

        # Таблица для отображения рёбер
        self.table_frame = tk.Frame(self.main_frame)
        self.table_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self.table_frame, columns=("From", "To", "Weight"), show="headings")
        self.tree.heading("From", text="Из")
        self.tree.heading("To", text="В")
        self.tree.heading("Weight", text="Вес")
        self.tree.pack()

        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)

        self.calc_button = tk.Button(self.control_frame, text="Найти оптимальный путь", command=self.solve_tsp)
        self.calc_button.grid(row=0, column=0, padx=5)

        self.clear_button = tk.Button(self.control_frame, text="Очистить граф", command=self.clear_graph)
        self.clear_button.grid(row=0, column=1, padx=5)

        self.undo_button = tk.Button(self.control_frame, text="Отменить", command=self.undo)
        self.undo_button.grid(row=0, column=2, padx=5)

        self.use_2opt = tk.BooleanVar()
        self.opt_checkbox = tk.Checkbutton(self.control_frame, text="Использовать 2-opt", variable=self.use_2opt)
        self.opt_checkbox.grid(row=0, column=3, padx=5)

        self.output_label = tk.Label(self.control_frame, text="Общая длина: ")
        self.output_label.grid(row=1, column=0, columnspan=4)

        self.graph = nx.DiGraph()
        self.nodes = []
        self.selected_node = None
        self.history = []  # Стек для хранения истории действий

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
        self.history.append(("add_node", node_id))  # Сохраняем действие в историю
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
                        self.history.append(("add_edge", (first_node, second_node, weight)))  # Сохраняем действие
                        self.update_table(first_node, second_node, weight)  # Обновляем таблицу
                    else:
                        old_weight = self.graph[first_node][second_node]['weight']
                        self.graph[first_node][second_node]['weight'] = weight
                        self.history.append(("update_edge", (first_node, second_node, old_weight)))  # Сохраняем действие
                        self.update_table(first_node, second_node, weight)  # Обновляем таблицу
                    self.selected_node = None
                    self.draw_graph()

    def update_table(self, from_node, to_node, weight):
        """Обновляет таблицу, добавляя новое ребро."""
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

    def undo(self):
        """Отмена последнего действия."""
        if not self.history:
            messagebox.showinfo("Информация", "Нет действий для отмены")
            return

        last_action = self.history.pop()  # Извлекаем последнее действие
        action_type, data = last_action

        if action_type == "add_node":
            node_id = data
            self.graph.remove_node(node_id)
            self.nodes.pop(node_id)
        elif action_type == "add_edge":
            first_node, second_node, weight = data
            self.graph.remove_edge(first_node, second_node)
            self.remove_from_table(first_node, second_node)  # Удаляем ребро из таблицы
        elif action_type == "update_edge":
            first_node, second_node, old_weight = data
            self.graph[first_node][second_node]['weight'] = old_weight
            self.update_table(first_node, second_node, old_weight)  # Обновляем таблицу

        self.draw_graph()

    def remove_from_table(self, from_node, to_node):
        """Удаляет ребро из таблицы."""
        for item in self.tree.get_children():
            if self.tree.item(item, "values")[:2] == (from_node, to_node):
                self.tree.delete(item)
                break

    def solve_tsp(self):
        if len(self.graph.nodes) < 2:
            messagebox.showerror("Ошибка", "Граф должен содержать хотя бы 2 вершины")
            return

        # Переменные для хранения лучшего пути и его длины
        best_path = None
        best_distance = float('inf')

        # Перебор всех вершин в качестве начальной
        for start_node in self.graph.nodes:
            path = self.nearest_neighbor(start_node)
            if path is None:
                continue  # Пропускаем, если путь невозможен

            # Вычисляем длину пути
            distance = self.calculate_path_distance(path)
            if distance < best_distance:
                best_path = path
                best_distance = distance

        # Если ни один путь не был найден
        if best_path is None:
            messagebox.showinfo("Информация", "Путей нет")
            return

        # Применение 2-opt, если выбрано
        if self.use_2opt.get():
            best_path = self.two_opt(best_path)
            best_distance = self.calculate_path_distance(best_path)

        # Вывод результата
        self.output_label.config(text=f"Общая длина: {best_distance}")
        self.draw_result(best_path)

    def nearest_neighbor(self, start_node):
        """Метод ближайшего соседа с заданной начальной вершиной."""
        path = [start_node]  # Начинаем с заданной вершины
        unvisited = set(self.graph.nodes) - {start_node}

        while unvisited:
            last_node = path[-1]
            nearest_node = None
            min_weight = float('inf')

            # Ищем ближайшую вершину
            for node in unvisited:
                edge_data = self.graph.get_edge_data(last_node, node)
                if edge_data is not None and edge_data['weight'] < min_weight:
                    nearest_node = node
                    min_weight = edge_data['weight']

            # Если ближайшая вершина не найдена, путь невозможен
            if nearest_node is None:
                return None

            path.append(nearest_node)
            unvisited.remove(nearest_node)

        # Проверяем, можно ли замкнуть цикл
        if not self.graph.has_edge(path[-1], path[0]):
            return None

        return path

    def calculate_path_distance(self, path):
        """Вычисление общей длины пути."""
        distance = 0
        for i in range(len(path) - 1):
            edge_data = self.graph.get_edge_data(path[i], path[i + 1])
            if edge_data is None:
                return float('inf')  # Если ребра нет, путь невозможен
            distance += edge_data['weight']
        # Замыкание цикла
        edge_data = self.graph.get_edge_data(path[-1], path[0])
        if edge_data is None:
            return float('inf')  # Если ребра нет, путь невозможен
        distance += edge_data['weight']
        return distance

    def two_opt(self, path):
        """Модификация 2-opt для улучшения маршрута."""
        best_path = path
        best_distance = self.calculate_path_distance(path)
        improved = True

        while improved:
            improved = False
            for i in range(1, len(path) - 2):
                for j in range(i + 1, len(path)):
                    if j - i == 1:
                        continue  # Пропускаем соседние рёбра
                    new_path = path[:i] + path[i:j][::-1] + path[j:]
                    new_distance = self.calculate_path_distance(new_path)
                    if new_distance < best_distance:
                        best_path = new_path
                        best_distance = new_distance
                        improved = True
            path = best_path

        return best_path

    def draw_result(self, path):
        """Отрисовка итогового пути."""
        self.result_canvas.delete("all")
        pos = nx.get_node_attributes(self.graph, 'pos')

        # Отрисовка рёбер итогового пути
        for i in range(len(path) - 1):
            x1, y1 = pos[path[i]]
            x2, y2 = pos[path[i + 1]]
            dx, dy = (x2 - x1), (y2 - y1)
            length = (dx ** 2 + dy ** 2) ** 0.5
            unit_dx, unit_dy = dx / length, dy / length

            arrow_dx, arrow_dy = unit_dx * 15, unit_dy * 15
            text_dx, text_dy = unit_dx * 20, unit_dy * 20

            self.result_canvas.create_line(
                x1 + arrow_dx, y1 + arrow_dy, x2 - arrow_dx, y2 - arrow_dy,
                fill="green", width=3, arrow=tk.LAST
            )

            text_x = (x1 + x2) / 2 + text_dx
            text_y = (y1 + y2) / 2 + text_dy

            if abs(dx) > abs(dy):
                text_y += 15 if dy > 0 else -15
            else:
                text_x += 15 if dx > 0 else -15

            self.result_canvas.create_text(
                text_x, text_y, text=str(self.graph.get_edge_data(path[i], path[i + 1])['weight']),
                fill="red", font=("Helvetica", 10, "bold")
            )

        # Замыкание цикла
        x1, y1 = pos[path[-1]]
        x2, y2 = pos[path[0]]
        dx, dy = (x2 - x1), (y2 - y1)
        length = (dx ** 2 + dy ** 2) ** 0.5
        unit_dx, unit_dy = dx / length, dy / length

        arrow_dx, arrow_dy = unit_dx * 15, unit_dy * 15
        text_dx, text_dy = unit_dx * 20, unit_dy * 20

        self.result_canvas.create_line(
            x1 + arrow_dx, y1 + arrow_dy, x2 - arrow_dx, y2 - arrow_dy,
            fill="green", width=3, arrow=tk.LAST
        )

        text_x = (x1 + x2) / 2 + text_dx
        text_y = (y1 + y2) / 2 + text_dy

        if abs(dx) > abs(dy):
            text_y += 15 if dy > 0 else -15
        else:
            text_x += 15 if dx > 0 else -15

        self.result_canvas.create_text(
            text_x, text_y, text=str(self.graph.get_edge_data(path[-1], path[0])['weight']),
            fill="red", font=("Helvetica", 10, "bold")
        )

        # Отрисовка вершин
        for node, (x, y) in pos.items():
            self.result_canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="orange")
            self.result_canvas.create_text(x, y, text=str(node), fill="black")

    def clear_graph(self):
        self.graph.clear()
        self.nodes = []
        self.selected_node = None
        self.history = []  # Очищаем историю
        self.canvas.delete("all")
        self.result_canvas.delete("all")
        self.output_label.config(text="Общая длина: ")
        self.tree.delete(*self.tree.get_children())  # Очищаем таблицу


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()








