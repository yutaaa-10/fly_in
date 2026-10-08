class Router:
    def assign_drones(
        self,
        drone_quantity: int,
        paths: list[list[str]],
        path_costs: list[int],
    ) -> list[list[int]]:
        assignments: list[list[int]] = [[] for _ in paths]
        print(paths)

        for drone_id in range(1, drone_quantity + 1):
            best_path_index = 0
            best_score = path_costs[0] + len(assignments[0])

            for index in range(1, len(paths)):
                score = path_costs[index] + len(assignments[index])
                if score < best_score:
                    best_score = score
                    best_path_index = index
                assignments[best_path_index].append(drone_id)
        return assignments
