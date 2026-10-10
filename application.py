import argparse
import sys
from parser import Parser
from graph import Graph
from pathfinder import PathFinder
from router import Router
from simulator import Simulator
from models import Drone


class Application:
    def parse_arguments(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description="Drone routiong simulation"
        )

        parser.add_argument(
            "map_file",
            help="Path to the map file"
        )

        return parser.parse_args()

    def open_file(self, map_file: str) -> str | None:
        try:
            with open(map_file, mode="r") as file:
                input_text = file.read()
                return input_text

        except OSError as error:
            print(
                f"Error: Cannot read input file {map_file}: {error}",
                file=sys.stderr,
            )
            return None

    def run(self) -> int:
        args = self.parse_arguments()
        input_text = self.open_file(args.map_file)
        if input_text is None:
            return 1

        parser = Parser()
        map_data = parser.parse(input_text)
        if map_data is None:
            return 1

        if map_data.start_zone is None or map_data.end_zone is None:
            return 1

        graph = Graph(map_data)
        path_finder = PathFinder(graph)

        paths = path_finder.find_all_paths(
            map_data.start_zone,
            map_data.end_zone,
        )

        if not paths:
            print(
                "Error: no path from start to goal",
                file=sys.stderr,
            )
            return 1

        paths = path_finder.sort_paths_by_cost(paths)
        for path in paths:
            print(
                path_finder.get_path_cost(path),
                path_finder.get_priority_count(path),
                path,
            )

        path_costs = [
            path_finder.get_path_cost(path)
            for path in paths
        ]

        router = Router(graph)

        assignments = router.assign_drones(
            map_data.drone_quantity,
            paths,
            path_costs,
        )

        drones: list[Drone] = []
        for path_index, drone_ids in enumerate(assignments):
            path = paths[path_index]
            for drone_id in drone_ids:
                drone = Drone(
                    drone_id=drone_id,
                    path=path,
                )
                drones.append(drone)

        simulator = Simulator(drones, map_data)
        simulator.run()
        return 0
