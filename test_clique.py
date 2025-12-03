import pytest
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clique_app import backtracking_clique_search, is_clique


class TestCliqueAlgorithm:

    def test_is_clique_positive(self):
        graph = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
        vertices = [0, 1, 2]
        assert is_clique(graph, vertices) == True

    def test_is_clique_negative(self):
        graph = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
        vertices = [0, 1, 2]
        assert is_clique(graph, vertices) == False

    def test_is_clique_single_vertex(self):
        graph = [[0]]
        vertices = [0]
        assert is_clique(graph, vertices) == True

    def test_is_clique_empty(self):
        graph = [[0, 1], [1, 0]]
        vertices = []
        assert is_clique(graph, vertices) == True

    def test_backtracking_complete_graph(self):
        graph = [[0, 1, 1, 1], [1, 0, 1, 1], [1, 1, 0, 1], [1, 1, 1, 0]]
        k = 3
        current_set = []
        start_index = 0
        step_count = [0]

        found, steps, clique = backtracking_clique_search(
            graph, k, current_set, start_index, step_count
        )

        assert found == True
        assert len(clique) == k
        assert is_clique(graph, clique)

    def test_backtracking_no_clique(self):
        graph = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]
        k = 3
        current_set = []
        start_index = 0
        step_count = [0]

        found, steps, clique = backtracking_clique_search(
            graph, k, current_set, start_index, step_count
        )

        assert found == False
        assert clique == []

    def test_backtracking_star_graph(self):
        graph = [
            [0, 1, 1, 1],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
        ]
        k = 2
        current_set = []
        start_index = 0
        step_count = [0]

        found, steps, clique = backtracking_clique_search(
            graph, k, current_set, start_index, step_count
        )

        assert found == True
        assert len(clique) == k
        assert 0 in clique
        assert is_clique(graph, clique)

    def test_backtracking_specific_clique(self):
        """Тест поиска конкретной клики"""
        graph = [
            [0, 1, 1, 0, 0],
            [1, 0, 1, 0, 0],
            [1, 1, 0, 1, 0],
            [0, 0, 1, 0, 1],
            [0, 0, 0, 1, 0],
        ]
        k = 3
        current_set = []
        start_index = 0
        step_count = [0]

        found, steps, clique = backtracking_clique_search(
            graph, k, current_set, start_index, step_count
        )

        assert found == True
        assert set(clique) == {0, 1, 2}
        assert is_clique(graph, clique)

    def test_backtracking_k_equals_1(self):
        graph = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        k = 1
        current_set = []
        start_index = 0
        step_count = [0]

        found, steps, clique = backtracking_clique_search(
            graph, k, current_set, start_index, step_count
        )

        assert found == True
        assert len(clique) == 1

    def test_backtracking_k_larger_than_graph(self):
        graph = [[0, 1], [1, 0]]
        k = 5
        current_set = []
        start_index = 0
        step_count = [0]

        found, steps, clique = backtracking_clique_search(
            graph, k, current_set, start_index, step_count
        )

        assert found == False

    def test_backtracking_empty_graph(self):
        graph = []
        k = 1
        current_set = []
        start_index = 0
        step_count = [0]

        found, steps, clique = backtracking_clique_search(
            graph, k, current_set, start_index, step_count
        )

        assert found == False

    def test_backtracking_step_count(self):
        graph = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
        k = 2
        current_set = []
        start_index = 0
        step_count = [0]

        found, steps, clique = backtracking_clique_search(
            graph, k, current_set, start_index, step_count
        )

        assert found == True
        assert steps > 0

    @pytest.mark.parametrize(
        "k,expected",
        [
            (1, True),
            (2, True),
            (3, True),
            (4, False),
        ],
    )
    def test_backtracking_parameterized(self, k, expected):
        graph = [[0, 1, 1, 0], [1, 0, 1, 0], [1, 1, 0, 1], [0, 0, 1, 0]]
        current_set = []
        start_index = 0
        step_count = [0]

        found, steps, clique = backtracking_clique_search(
            graph, k, current_set, start_index, step_count
        )

        assert found == expected
        if found:
            assert len(clique) == k
            assert is_clique(graph, clique)


class TestEdgeCases:

    def test_single_vertex_graph(self):
        graph = [[0]]

        found, steps, clique = backtracking_clique_search(graph, 1, [], 0, [0])
        assert found == True
        assert clique == [0]

        found, steps, clique = backtracking_clique_search(graph, 2, [], 0, [0])
        assert found == False

    def test_disconnected_graph(self):
        """Тест несвязного графа"""
        graph = [
            [0, 1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
        ]

        found, steps, clique = backtracking_clique_search(graph, 2, [], 0, [0])
        assert found == True
        assert len(clique) == 2
        assert is_clique(graph, clique)

        found, steps, clique = backtracking_clique_search(graph, 3, [], 0, [0])
        assert found == False

    def test_complete_bipartite(self):
        graph = [[0, 0, 1, 1], [0, 0, 1, 1], [1, 1, 0, 0], [1, 1, 0, 0]]

        found, steps, clique = backtracking_clique_search(graph, 2, [], 0, [0])
        assert found == True

        found, steps, clique = backtracking_clique_search(graph, 3, [], 0, [0])
        assert found == False


def test_performance_small_graph():
    import time

    graph = [
        [0, 1, 1, 0, 0],
        [1, 0, 1, 1, 0],
        [1, 1, 0, 1, 1],
        [0, 1, 1, 0, 1],
        [0, 0, 1, 1, 0],
    ]

    start_time = time.time()
    found, steps, clique = backtracking_clique_search(graph, 3, [], 0, [0])
    end_time = time.time()

    execution_time = end_time - start_time

    assert found == True
    assert len(clique) == 3
    assert is_clique(graph, clique)

    assert (
        execution_time < 0.1
    ), f"Алгоритм выполняется слишком долго: {execution_time:.4f} секунд"


def test_algorithm_complexity():
    small_graph = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]

    start_time = time.time()
    found1, steps1, clique1 = backtracking_clique_search(small_graph, 2, [], 0, [0])
    small_time = time.time() - start_time

    medium_graph = [
        [0, 1, 1, 0, 0],
        [1, 0, 1, 1, 0],
        [1, 1, 0, 1, 1],
        [0, 1, 1, 0, 1],
        [0, 0, 1, 1, 0],
    ]

    start_time = time.time()
    found2, steps2, clique2 = backtracking_clique_search(medium_graph, 3, [], 0, [0])
    medium_time = time.time() - start_time

    assert found1 == True
    assert found2 == True

    print(f"Маленький граф: {small_time:.6f} сек, {steps1} шагов")
    print(f"Средний граф: {medium_time:.6f} сек, {steps2} шагов")


def test_backtracking_optimization():
    graph = [[0, 1, 1, 0], [1, 0, 1, 0], [1, 1, 0, 1], [0, 0, 1, 0]]

    step_count = [0]
    found, steps, clique = backtracking_clique_search(graph, 3, [], 0, step_count)

    assert found == True
    assert len(clique) == 3
    assert steps < 20, f"Алгоритм сделал слишком много шагов: {steps}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
