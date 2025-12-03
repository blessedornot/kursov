import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import time
from clique_app import backtracking_clique_search, is_clique, db


class CliqueFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clique Finder - Backtracking Algorithm with Database")
        self.root.geometry("1200x800")

        self.graph = []
        self.num_vertices = 0
        self.current_clique = []
        self.solution_clique = []

        self.setup_ui()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Поиск клики")

        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="История поисков")

        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Статистика")

        self.setup_search_tab()
        self.setup_history_tab()
        self.setup_stats_tab()

    def setup_search_tab(self):
        control_frame = ttk.Frame(self.search_frame, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        graph_frame = ttk.Frame(self.search_frame, padding="10")
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        result_frame = ttk.Frame(self.search_frame, padding="10")
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(control_frame, text="Количество вершин:").grid(
            row=0, column=0, padx=5, pady=5
        )
        self.vertices_entry = ttk.Entry(control_frame, width=10)
        self.vertices_entry.insert(0, "6")
        self.vertices_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(control_frame, text="Создать граф", command=self.create_graph).grid(
            row=0, column=2, padx=5, pady=5
        )

        ttk.Label(control_frame, text="Размер клики (k):").grid(
            row=0, column=3, padx=5, pady=5
        )
        self.k_entry = ttk.Entry(control_frame, width=10)
        self.k_entry.insert(0, "3")
        self.k_entry.grid(row=0, column=4, padx=5, pady=5)

        ttk.Button(control_frame, text="Найти клику", command=self.find_clique).grid(
            row=0, column=5, padx=5, pady=5
        )

        ttk.Button(control_frame, text="Очистить", command=self.clear_all).grid(
            row=0, column=6, padx=5, pady=5
        )

        ttk.Button(
            control_frame, text="Сохранить в БД", command=self.save_current_to_db
        ).grid(row=0, column=7, padx=5, pady=5)

        ttk.Label(control_frame, text="Матрица смежности:").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.W
        )
        self.matrix_frame = ttk.Frame(control_frame)
        self.matrix_frame.grid(
            row=2, column=0, columnspan=8, padx=5, pady=5, sticky=tk.W
        )

        ttk.Label(graph_frame, text="Визуализация графа").pack()
        self.figure = plt.Figure(figsize=(6, 5), dpi=100)

        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        ttk.Label(result_frame, text="Процесс поиска").pack()

        self.process_text = tk.Text(result_frame, height=15, width=40)
        self.process_text.pack(fill=tk.BOTH, expand=True, pady=5)

        scrollbar = ttk.Scrollbar(
            result_frame, orient=tk.VERTICAL, command=self.process_text.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.process_text.configure(yscrollcommand=scrollbar.set)

        ttk.Label(result_frame, text="Результат").pack()
        self.result_text = tk.Text(result_frame, height=8, width=40, bg="#090909")
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

        self.create_default_graph()

    def setup_history_tab(self):
        history_control_frame = ttk.Frame(self.history_frame, padding="10")
        history_control_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(
            history_control_frame, text="Обновить", command=self.load_history
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            history_control_frame, text="Очистить историю", command=self.clear_history
        ).pack(side=tk.LEFT, padx=5)

        columns = (
            "ID",
            "Время",
            "Вершин",
            "k",
            "Найдена",
            "Клика",
            "Шаги",
            "Время (с)",
        )
        self.history_tree = ttk.Treeview(
            self.history_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=80)

        self.history_tree.column("Время", width=150)
        self.history_tree.column("Клика", width=120)

        history_scrollbar = ttk.Scrollbar(
            self.history_frame, orient=tk.VERTICAL, command=self.history_tree.yview
        )
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)

        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        details_frame = ttk.LabelFrame(
            self.history_frame, text="Детали записи", padding="10"
        )
        details_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.details_text = tk.Text(details_frame, height=8, width=80)
        self.details_text.pack(fill=tk.BOTH, expand=True)

        self.history_tree.bind("<<TreeviewSelect>>", self.on_history_select)

        self.load_history()

    def setup_stats_tab(self):
        stats_frame = ttk.Frame(self.stats_frame, padding="20")
        stats_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            stats_frame, text="Статистика поисков клик", font=("Arial", 14, "bold")
        ).pack(pady=10)

        self.stats_text = tk.Text(stats_frame, height=15, width=60, font=("Arial", 10))
        self.stats_text.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Button(
            stats_frame, text="Обновить статистику", command=self.load_statistics
        ).pack(pady=5)

        self.load_statistics()

    def create_default_graph(self):

        self.vertices_entry.insert(0, str(self.num_vertices))

        self.graph = [
            [0, 1, 1, 0, 0, 0],
            [1, 0, 1, 0, 0, 0],
            [1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 1],
            [0, 0, 1, 1, 0, 1],
            [0, 0, 1, 1, 1, 0],
        ]

        self.update_matrix_display()
        self.visualize_graph()

    def create_graph(self):
        try:
            self.num_vertices = int(self.vertices_entry.get())
            if self.num_vertices < 1 or self.num_vertices > 10:
                messagebox.showerror(
                    "Ошибка", "Количество вершин должно быть от 1 до 10"
                )
                return

            self.graph = [
                [0 for _ in range(self.num_vertices)] for _ in range(self.num_vertices)
            ]
            self.update_matrix_display()
            self.visualize_graph()
            self.clear_results()

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число вершин")

    def update_matrix_display(self):
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()

        for i in range(self.num_vertices):
            for j in range(self.num_vertices):
                if i == j:
                    ttk.Label(
                        self.matrix_frame, text="0", width=3, background="#000000"
                    ).grid(row=i, column=j, padx=1, pady=1)
                else:
                    var = tk.IntVar(value=self.graph[i][j])
                    cb = ttk.Checkbutton(
                        self.matrix_frame,
                        variable=var,
                        command=lambda i=i, j=j, var=var: self.toggle_edge(i, j, var),
                    )
                    cb.grid(row=i, column=j, padx=1, pady=1)

    def toggle_edge(self, i, j, var):
        self.graph[i][j] = var.get()
        self.graph[j][i] = var.get()
        self.visualize_graph()
        self.clear_results()

    def visualize_graph(self):
        self.ax.clear()

        G = nx.Graph()

        for i in range(self.num_vertices):
            G.add_node(i)

        for i in range(self.num_vertices):
            for j in range(i + 1, self.num_vertices):
                if self.graph[i][j] == 1:
                    G.add_edge(i, j)

        pos = nx.spring_layout(G)

        nx.draw_networkx_nodes(
            G,
            pos,
            ax=self.ax,
            node_size=500,
            node_color="lightblue",
            edgecolors="black",
        )
        nx.draw_networkx_edges(G, pos, ax=self.ax, width=2)
        nx.draw_networkx_labels(G, pos, ax=self.ax, font_size=16, font_weight="bold")

        if self.solution_clique:
            clique_nodes = self.solution_clique
            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=clique_nodes,
                ax=self.ax,
                node_size=500,
                node_color="red",
                edgecolors="black",
            )

            clique_edges = [
                (u, v)
                for u in clique_nodes
                for v in clique_nodes
                if u < v and self.graph[u][v] == 1
            ]
            nx.draw_networkx_edges(
                G, pos, edgelist=clique_edges, ax=self.ax, width=3, edge_color="red"
            )

        self.ax.set_title(
            "Граф"
            + (
                f" - Найдена клика: {self.solution_clique}"
                if self.solution_clique
                else ""
            )
        )
        self.ax.axis("off")
        self.canvas.draw()

    def find_clique_backtracking(self, k, current_set, start_index, step_count):

        def log_function(message, tag=None):
            self.process_text.insert(tk.END, message)
            if tag:
                self.process_text.tag_add(tag, "end-2l", "end-1l")
            self.process_text.see(tk.END)
            self.root.update()

        return backtracking_clique_search(
            self.graph, k, current_set, start_index, step_count, log_function
        )

    def find_clique(self):
        try:
            k = int(self.k_entry.get())
            if k < 1 or k > self.num_vertices:
                messagebox.showerror(
                    "Ошибка", f"Размер клики должен быть от 1 до {self.num_vertices}"
                )
                return

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный размер клики")
            return

        self.clear_results()
        self.solution_clique = []

        self.process_text.insert(tk.END, f"=== ПОИСК КЛИКИ РАЗМЕРА {k} ===\n\n")

        start_time = time.time()
        step_count = [0]
        self.current_clique = []
        found, total_steps, clique = self.find_clique_backtracking(
            k, self.current_clique, 0, step_count
        )
        execution_time = time.time() - start_time

        session_id = db.save_search_result(
            graph=self.graph,
            k=k,
            found=found,
            clique_vertices=clique if found else None,
            steps=total_steps,
            execution_time=execution_time,
        )

        self.result_text.insert(tk.END, f"РЕЗУЛЬТАТ ПОИСКА:\n")
        self.result_text.insert(tk.END, f"ID в базе данных: {session_id}\n")

        self.result_text.insert(
            tk.END, f"Результат: {'КЛИКА НАЙДЕНА' if found else 'КЛИКА НЕ НАЙДЕНА'}\n"
        )

        if found:
            self.solution_clique = clique.copy()
            self.result_text.insert(tk.END, f"Вершины клики: {self.solution_clique}\n")

        self.visualize_graph()

        self.process_text.tag_configure(
            "success", foreground="green", font=("TkDefaultFont", 10, "bold")
        )

        self.load_history()

        if not hasattr(self, "current_clique") or not self.solution_clique:
            messagebox.showwarning("Предупреждение", "Сначала выполните поиск клики")
            return

        k = int(self.k_entry.get())
        session_id = db.save_search_result(
            graph=self.graph,
            k=k,
            found=bool(self.solution_clique),
            clique_vertices=self.solution_clique,
            steps=0,
            execution_time=0.0,
        )

        messagebox.showinfo("Успех", f"Результат сохранен в БД с ID: {session_id}")
        self.load_history()

        for session in sessions:
            clique_str = (
                ", ".join(map(str, session["clique_vertices"]))
                if session["clique_vertices"]
                else "Не найдена"
            )
            found_str = "Да" if session["found_clique"] else "Нет"

            self.history_tree.insert(
                "",
                "end",
                values=(
                    session["id"],
                    session["timestamp"],
                    session["graph_vertices"],
                    session["target_k"],
                    found_str,
                    clique_str,
                    session["steps"],
                    f"{session['execution_time']:.4f}",
                ),
            )

    def on_history_select(self, event):
        selection = self.history_tree.selection()
        if not selection:
            return

        item = self.history_tree.item(selection[0])
        session_id = item["values"][0]

        session = db.get_session_by_id(session_id)
        if session:
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"Детали поиска (ID: {session['id']})\n")
            self.details_text.insert(tk.END, f"Время: {session['timestamp']}\n")
            self.details_text.insert(
                tk.END, f"Граф: {session['graph_vertices']} вершин\n"
            )
            self.details_text.insert(tk.END, f"Целевой k: {session['target_k']}\n")
            self.details_text.insert(
                tk.END, f"Найдена клика: {'Да' if session['found_clique'] else 'Нет'}\n"
            )
            self.details_text.insert(
                tk.END, f"Вершины клики: {session['clique_vertices']}\n"
            )
            self.details_text.insert(tk.END, f"Шагов алгоритма: {session['steps']}\n")
            self.details_text.insert(
                tk.END, f"Время выполнения: {session['execution_time']:.4f} сек\n"
            )

    def load_statistics(self):
        stats = db.get_statistics()

        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "ОБЩАЯ СТАТИСТИКА ПОИСКОВ\n\n")
        self.stats_text.insert(tk.END, f"Всего поисков: {stats['total_searches']}\n")
        self.stats_text.insert(
            tk.END, f"Успешных поисков: {stats['successful_searches']}\n"
        )
        self.stats_text.insert(
            tk.END, f"Процент успеха: {stats['success_rate']*100:.1f}%\n\n"
        )

        self.stats_text.insert(tk.END, "СРЕДНИЕ ПОКАЗАТЕЛИ\n\n")
        self.stats_text.insert(
            tk.END, f"Среднее количество шагов: {stats['avg_steps']:.1f}\n"
        )
        self.stats_text.insert(
            tk.END, f"Среднее время выполнения: {stats['avg_time']:.4f} сек\n\n"
        )

        self.stats_text.insert(tk.END, "МАКСИМАЛЬНЫЕ ПОКАЗАТЕЛИ\n\n")
        self.stats_text.insert(
            tk.END, f"Максимальное количество шагов: {stats['max_steps']}\n"
        )
        self.stats_text.insert(
            tk.END, f"Максимальное время выполнения: {stats['max_time']:.4f} сек\n"
        )

    def clear_history(self):
        if messagebox.askyesno(
            "Подтверждение", "Вы уверены, что хотите очистить всю историю?"
        ):
            db.clear_all_data()
            self.load_history()
            self.load_statistics()
            messagebox.showinfo("Успех", "История очищена")

    def clear_results(self):
        self.process_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.current_clique = []
        self.solution_clique = []
        self.visualize_graph()

    def clear_all(self):
        self.clear_results()
        self.create_default_graph()


def main():
    root = tk.Tk()
    app = CliqueFinderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
