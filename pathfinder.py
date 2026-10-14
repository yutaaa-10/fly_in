from graph import Graph


class PathFinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

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
            return None

        for neighbor in self.graph.get_neighbors(current):
            if neighbor in current_path:
                continue
            if self.graph.get_move_cost(neighbor) is None:
                continue
            current_path.append(neighbor)
            self._dfs_paths(
                current=neighbor,
                goal=goal,
                current_path=current_path,
                all_paths=all_paths,
            )
            current_path.pop()
        return None

    def get_path_cost(
            self,
            paths: list[str],
    ) -> int:
        total_cost = 0
        for zone_name in paths[1:]:
            move_cost = self.graph.get_move_cost(zone_name)
            if move_cost is None:
                return -1
            total_cost += move_cost
        return total_cost

    def get_priority_count(
            self,
            path: list[str],
    ) -> int:
        priority_count = 0

        for zone_name in path[1:]:
            zone = self.graph.map_data.zones[zone_name]
            if zone.zone_type == "priority":
                priority_count += 1
        return priority_count

    def sort_paths_by_cost(
        self,
        paths: list[list[str]],
    ) -> tuple[list[list[str]], list[int]]:
        path_data = []

        for path in paths:
            cost = self.get_path_cost(path)
            priority_count = self.get_priority_count(path)
            path_data.append((path, cost, priority_count))

        path_data.sort(
            key=lambda item: (item[1], -item[2])
        )

        sorted_paths = []
        path_costs = []

        for path, cost, _ in path_data:
            sorted_paths.append(path)
            path_costs.append(cost)

        return sorted_paths, path_costs
