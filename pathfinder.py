from collections import deque
from graph import Graph
import heapq


class PathFinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def bfs(self, start: str, goal: str) -> list[str] | None:
        queue: deque[str] = deque([start])
        visited: set[str] = {start}
        previous: dict[str, str | None] = {start: None}

        while queue:
            current = queue.popleft()
            if current == goal:
                return self.build_path(previous, goal)
            for neighbor in self.graph.get_neighbors(current):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                previous[neighbor] = current
                queue.append(neighbor)
        return None

    def dijkstra(
        self,
        start: str,
        goal: str
    ) -> list[str] | None:
        priority_queue: list[tuple[int, str]] = [(0, start)]
        distances: dict[str, int] = {start: 0}
        previous: dict[str, str | None] = {start: None}

        while priority_queue:

            current_distance, current = heapq.heappop(priority_queue)

            if current == goal:
                return self.build_path(previous, goal)

            for neighbor in self.graph.get_neighbors(current):
                move_cost = self.graph.get_move_cost(neighbor)

                if move_cost is None:
                    continue

                new_distance = current_distance + move_cost

                if neighbor not in distances:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current
                    heapq.heappush(priority_queue, (new_distance, neighbor))
                elif new_distance < distances[neighbor]:
                    previous[neighbor] = current
                    heapq.heappush(priority_queue, (new_distance, neighbor))

    def build_path(
        self,
        previous: dict[str, str | None],
        goal: str,
    ) -> list[str]:

        path: list[str] = []
        current: str | None = goal

        while current is not None:
            path.append(current)
            current = previous[current]

        path.reverse()
        return path

    def find_all_paths(self, start: str, goal: str) -> list[list[str]]:
        all_paths: list[list[str]] = []

        self._dfs_paths(
            current=start,
            goal=goal,
            current_path=[start],
            all_paths=all_paths,
        )
        return all_paths

    def _dfs_paths(
        self,
        current: str,
        goal: str,
        current_path: list[str],
        all_paths: list[list[str]],
    ) -> None:
        if current == goal:
            all_paths.append(current_path.copy())

        for neighbor in self.graph.get_neighbors(current):
            if neighbor in current_path:
                continue

            current_path.append(neighbor)

            self._dfs_paths(
                current=neighbor,
                goal=goal,
                current_path=current_path,
                all_paths=all_paths,
            )
            current_path.pop()

    def get_path_cost(self, path: list[str]) -> int:
        total_cost = 0

        for zone_name in path[1:]:
            move_cost = self.graph.get_move_cost(zone_name)
            if move_cost is None:
                return -1
            total_cost += move_cost
        return total_cost

    def sort_paths_by_cost(self, paths: list[list[str]]) -> list[list[str]]:
        return sorted(paths, key=self.get_path_cost)
