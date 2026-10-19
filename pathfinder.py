from graph import Graph


class PathFinder:
    """Find available paths and evaluate their movement costs.

    This class uses depth-first search (DFS) to find all simple
    paths between two zones. It calculates movement costs and
    prioritizes paths based on cost and priority zone count.

    Attributes:
        graph: Graph containing zone connections and movement costs.
    """

    def __init__(self, graph: Graph) -> None:
        """Initialize the path finder with a graph.

        Args:
            graph: Graph used for path exploration and cost calculation.
        """
        self.graph = graph

    def find_all_paths(self, start: str, goal: str) -> list[list[str]]:
        """Find all simple paths between two zones using DFS.

        Args:
            start: Name of the starting zone.
            goal: Name of the destination zone.

        Returns:
            A list of paths, where each path is a list of zone names.
            Returns an empty list if no path exists.
        """
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
        """Recursively explore all simple paths using DFS.

        This method explores neighboring zones while avoiding
        cycles and blocked zones. When the goal is reached,
        a copy of the current path is added to all_paths.

        Args:
            current: Name of the zone currently being explored.
            goal: Name of the destination zone.
            current_path: List of zones in the current search path.
            all_paths: List used to collect discovered paths.
        """
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
        """Calculate the total movement cost of a path.

        The starting zone is excluded from the cost calculation.
        Each subsequent zone contributes its movement cost.

        Args:
            paths: Ordered list of zone names representing a path.

        Returns:
            Total movement cost of the path, or -1 if the path
            contains a blocked or unsupported zone.
        """
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
        """Count the number of priority zones in a path.

        The starting zone is excluded from the count.

        Args:
            path: Ordered list of zone names representing a path.

        Returns:
            Number of priority zones contained in the path.
        """
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
        """Sort paths by movement cost and priority zone count.

        Paths are sorted by ascending movement cost. When paths
        have equal costs, paths containing more priority zones
        are ranked first.

        Args:
            paths: List of paths to evaluate and sort.

        Returns:
            A tuple containing the sorted paths and their
            corresponding movement costs.
        """
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
