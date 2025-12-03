# clique_app.py - Алгоритмические функции и работа с БД

import sqlite3
import json
import time
from datetime import datetime
from typing import List, Optional, Tuple


def is_clique(graph, vertices):
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            if graph[vertices[i]][vertices[j]] == 0:
                return False
    return True


def backtracking_clique_search(
    graph, k, current_set, start_index, step_count, log_function=None
):

    step_count[0] += 1

    if log_function:
        log_function(
            f"Шаг {step_count[0]}: Текущее множество: {current_set}, start_index: {start_index}\n"
        )

    if len(current_set) == k:
        if is_clique(graph, current_set):
            if log_function:
                log_function(f"✓ НАЙДЕНА КЛИКА: {current_set}\n\n", "success")
            return True, step_count[0], current_set.copy()
        else:
            if log_function:
                log_function(f"✗ Множество {current_set} не является кликой\n\n")
            return False, step_count[0], []

    for i in range(start_index, len(graph)):
        can_add = True
        for vertex in current_set:
            if graph[i][vertex] == 0:
                can_add = False
                break

        if can_add:
            if log_function:
                log_function(f"  Добавляем вершину {i} в {current_set}\n")

            current_set.append(i)
            found, steps, clique = backtracking_clique_search(
                graph, k, current_set, i + 1, step_count, log_function
            )

            if found:
                return True, steps, clique

            if log_function:
                log_function(f"  BACKTRACK: убираем вершину {i} из {current_set}\n")
            current_set.pop()

    return False, step_count[0], []


class CliqueDatabase:

    def __init__(self, db_path="clique_results.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS search_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                graph_vertices INTEGER NOT NULL,
                target_k INTEGER NOT NULL,
                found_clique BOOLEAN NOT NULL,
                clique_vertices TEXT,
                steps INTEGER NOT NULL,
                execution_time REAL NOT NULL,
                graph_matrix TEXT NOT NULL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                step_count INTEGER,
                memory_usage INTEGER,
                FOREIGN KEY (session_id) REFERENCES search_sessions (id)
            )
        """
        )

        conn.commit()
        conn.close()

    def save_search_result(
        self, graph, k, found, clique_vertices, steps, execution_time
    ):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        graph_json = json.dumps(graph)
        clique_json = json.dumps(clique_vertices) if clique_vertices else None

        cursor.execute(
            """
            INSERT INTO search_sessions 
            (graph_vertices, target_k, found_clique, clique_vertices, steps, execution_time, graph_matrix)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (len(graph), k, found, clique_json, steps, execution_time, graph_json),
        )

        session_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return session_id

    def get_all_sessions(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, timestamp, graph_vertices, target_k, found_clique, clique_vertices, steps, execution_time
            FROM search_sessions 
            ORDER BY timestamp DESC
        """
        )

        sessions = []
        for row in cursor.fetchall():
            session = {
                "id": row[0],
                "timestamp": row[1],
                "graph_vertices": row[2],
                "target_k": row[3],
                "found_clique": bool(row[4]),
                "clique_vertices": json.loads(row[5]) if row[5] else [],
                "steps": row[6],
                "execution_time": row[7],
            }
            sessions.append(session)

        conn.close()
        return sessions

    def get_session_by_id(self, session_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, timestamp, graph_vertices, target_k, found_clique, clique_vertices, steps, execution_time, graph_matrix
            FROM search_sessions 
            WHERE id = ?
        """,
            (session_id,),
        )

        row = cursor.fetchone()
        if row:
            session = {
                "id": row[0],
                "timestamp": row[1],
                "graph_vertices": row[2],
                "target_k": row[3],
                "found_clique": bool(row[4]),
                "clique_vertices": json.loads(row[5]) if row[5] else [],
                "steps": row[6],
                "execution_time": row[7],
                "graph_matrix": json.loads(row[8]) if row[8] else [],
            }
            conn.close()
            return session
        else:
            conn.close()
            return None

    def get_statistics(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM search_sessions")
        total_searches = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM search_sessions WHERE found_clique = 1")
        successful_searches = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(steps), AVG(execution_time) FROM search_sessions")
        avg_steps, avg_time = cursor.fetchone()

        cursor.execute("SELECT MAX(steps), MAX(execution_time) FROM search_sessions")
        max_steps, max_time = cursor.fetchone()

        conn.close()

        return {
            "total_searches": total_searches,
            "successful_searches": successful_searches,
            "success_rate": (
                successful_searches / total_searches if total_searches > 0 else 0
            ),
            "avg_steps": avg_steps or 0,
            "avg_time": avg_time or 0,
            "max_steps": max_steps or 0,
            "max_time": max_time or 0,
        }

    def clear_all_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM search_sessions")
        cursor.execute("DELETE FROM performance_stats")

        conn.commit()
        conn.close()


db = CliqueDatabase()
