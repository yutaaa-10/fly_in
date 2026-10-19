from graph import Graph


class Router:
    """Assign drones to paths while considering connection congestion.

    This class evaluates available paths using their movement costs
    and estimated connection loads. Drones are assigned one by one
    to the path with the lowest estimated score.

    Attributes:
        graph: Graph containing zone and connection information.
    """

    def __init__(self, graph: Graph) -> None:
        """Initialize the router with a graph.

        Args:
            graph: Graph used to access connections and movement costs.
        """
        self.graph = graph

    @staticmethod
    def edge_key(zone_a: str, zone_b: str) -> tuple[str, str]:
        """Create a consistent key for a bidirectional connection.

        The zone names are sorted lexicographically so that
        connections A-B and B-A produce the same key.

        Args:
            zone_a: Name of the first zone.
            zone_b: Name of the second zone.

        Returns:
            A tuple containing the two zone names in sorted order.
        """
        if zone_a <= zone_b:
            return (zone_a, zone_b)
        return (zone_b, zone_a)

    def assign_drones(
        self,
        drone_quantity: int,
        paths: list[list[str]],
        path_costs: list[int],
    ) -> list[list[int]]:
        """Assign drones to paths using estimated congestion scores.

        This method assigns drones sequentially to the path with
        the lowest estimated score. Each score combines the path's
        movement cost with a congestion estimate based on connection
        capacities, projected loads, and zone movement costs.

        Args:
            drone_quantity: Total number of drones to assign.
            paths: List of available paths represented by zone names.
            path_costs: Movement costs corresponding to each path.

        Returns:
            A list of drone ID lists, where each inner list contains
            the drones assigned to the corresponding path.
        """
        assignments: list[list[int]] = [[] for _ in paths]

        path_edges = []
        for path in paths:
            edges = []
            for zone_a, zone_b in zip(path, path[1:]):
                edge = self.edge_key(zone_a, zone_b)
                edges.append(edge)
            path_edges.append(edges)

        connection_capacities = {}
        for connection in self.graph.map_data.connections:
            edge = self.edge_key(
                connection.zone_a,
                connection.zone_b,
            )
            capacity = connection.max_link_capacity
            connection_capacities[edge] = capacity

        edge_loads: dict[tuple[str, str], int] = {}
        for drone_id in range(1, drone_quantity + 1):
            best_path_index = 0
            best_score: int | None = None

            for path_index, path in enumerate(paths):
                congestion = 0

                for step_index, edge in enumerate(
                    path_edges[path_index],
                    start=1,
                ):
                    capacity = connection_capacities[edge]
                    projected_load = edge_loads.get(edge, 0) + 1
                    move_cost = self.graph.get_move_cost(path[step_index])

                    if move_cost is None:
                        continue

                    required_waves = (
                        projected_load + capacity - 1
                    ) // capacity
                    pressure = required_waves * move_cost
                    congestion = max(congestion, pressure)

                score = path_costs[path_index] + congestion
                if best_score is None or score < best_score:
                    best_score = score
                    best_path_index = path_index

            assignments[best_path_index].append(drone_id)
            for edge in path_edges[best_path_index]:
                edge_loads[edge] = edge_loads.get(edge, 0) + 1

        return assignments
