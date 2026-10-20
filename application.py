import argparse
import sys
from parser import Parser
from graph import Graph
from pathfinder import PathFinder
from router import Router
from simulator import Simulator
from models import Drone
import os


class Application:
    """Manage the overall execution of the drone routing application.

    This class handles command-line arguments, input file loading,
    map parsing, pathfinding, drone assignment, and simulation startup.
    """

    def parse_arguments(self) -> argparse.Namespace:
        """Parse command-line arguments.

        Returns:
            argparse.Namespace: Parsed arguments containing the map file path.
        """
        parser = argparse.ArgumentParser(
            description="Drone routiong simulation"
        )

        parser.add_argument(
            "map_file",
            help="Path to the map file"
        )

        return parser.parse_args()

    def open_file(self, map_file: str) -> str | None:
        """Read the contents of a map file.

        Args:
            map_file (str): Path to the input map file.

        Returns:
            str | None: File contents if reading succeeds,
                or None if an error occurs.
        """
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
        """Execute the drone routing application.

        This method loads and validates the map, constructs the graph,
        finds available paths, assigns drones to routes, and starts
        the simulation with graphical visualization.

        Returns:
            int: 0 if the application completes successfully,
                or 1 if an error occurs during setup.
        """
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

        paths, path_costs = path_finder.sort_paths_by_cost(paths)

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
                drone = Drone(drone_id=drone_id, path=path)
                drones.append(drone)

        simulator = Simulator(drones, map_data)

        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
        from visualizer import PygameVisualizer
        visualizer = PygameVisualizer(map_data, drones, simulator)
        visualizer.run()

        return 0
