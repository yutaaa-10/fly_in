from graph import Graph


class Router:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    @staticmethod
    def edge_key(zone_a: str, zone_b: str) -> tuple[str, str]:
        if zone_a <= zone_b:
            return (zone_a, zone_b)
        return (zone_b, zone_a)

    def assign_drones(
        self,
        drone_quantity: int,
        paths: list[list[str]],
        path_costs: list[int],
    ) -> list[list[int]]:
        assignments: list[list[int]] = [[] for _ in paths]

        path_edges: list[list[tuple[str, str]]] = [
            [
                self.edge_key(zone_a, zone_b)
                for zone_a, zone_b in zip(path, path[1:])
            ]
            for path in paths
        ]

        connection_capacities: dict[tuple[str, str], int] = {
            self.edge_key(
                connection.zone_a,
                connection.zone_b,
            ): connection.max_link_capacity
            for connection in self.graph.map_data.connections
        }

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

                    move_cost = self.graph.get_move_cost(
                        path[step_index]
                    )

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
