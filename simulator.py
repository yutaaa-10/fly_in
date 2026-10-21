import sys
from models import Drone, MapData, Connection


class Simulator:
    """Manage turn-based drone movements through the routing network.

    This class advances drones along their assigned paths while
    checking zone capacities, connection capacities, and multi-turn
    movements through restricted zones.

    Attributes:
        drones: List of drones participating in the simulation.
        turn: Current simulation turn number.
        map_data: Map data containing zones and connections.
    """

    def __init__(self, drones: list[Drone], map_data: MapData) -> None:
        """Initialize the simulator with drones and map data.

        Args:
            drones: List of drones with assigned paths.
            map_data: Map configuration containing zones and connections.
        """
        self.drones = drones
        self.turn = 0
        self.map_data = map_data

    def run(self) -> None:
        """Run the simulation until all drones arrive or a deadlock occurs.

        This method repeatedly executes simulation turns.
        If a turn makes no progress while drones remain unfinished,
        an error message is printed to standard error output.
        """
        while not self.all_arrived():
            moved_count = self.run_turn()
            if moved_count == 0:
                print("Error: simulation deadlock", file=sys.stderr)
                return

    def run_turn(self) -> int:
        """Execute one turn of the drone movement simulation.

        This method updates drones already in transit, calculates
        zone occupancy and connection usage, and attempts to move
        eligible drones along their assigned paths.

        Movements are checked against zone and connection capacities.
        Restricted zones require a multi-turn transit process.

        Returns:
            Number of drone movement actions completed or started
            during the current turn.
        """
        self.turn += 1
        move_count = 0
        movements: list[str] = []

        occupancy = self.get_zone_occupancy()
        connection_usage = self.get_connection_usage()
        reservations = self.get_zone_reservations()
        arrived_this_turn: set[int] = set()

        for drone in self.drones:
            if not drone.in_transit:
                continue

            current_zone = drone.current_zone()
            target_zone = drone.target_zone
            drone.advance_transit()
            if not drone.in_transit:
                arrived_zone = drone.current_zone()
                if target_zone is not None:
                    reservations[target_zone] -= 1

                edge_key: tuple[str, str]
                if current_zone <= target_zone:
                    edge_key = (current_zone, target_zone)
                else:
                    edge_key = (target_zone, current_zone)
                connection_usage[edge_key] -= 1

                occupancy[arrived_zone] += 1
                arrived_this_turn.add(drone.drone_id)
                move_count += 1
                movements.append(
                    f"D{drone.drone_id}-{arrived_zone}"
                )

        drones = sorted(
            self.drones,
            key=lambda drone: drone.path_index,
            reverse=True,
        )

        for drone in drones:
            if drone.drone_id in arrived_this_turn:
                continue
            if drone.has_arrived():
                continue
            if drone.in_transit:
                continue

            current_zone = drone.current_zone()
            next_zone = drone.next_zone()
            if next_zone is None:
                continue

            zone = self.map_data.zones[next_zone]
            if zone.zone_type == "blocked":
                continue

            connection = self.get_connection(current_zone, next_zone)
            if connection is None:
                continue

            if current_zone <= next_zone:
                edge_key = (current_zone, next_zone)
            else:
                edge_key = (next_zone, current_zone)

            used_capacity = connection_usage.get(edge_key, 0)
            if used_capacity >= connection.max_link_capacity:
                continue

            if zone.max_drones is not None:
                future_occupancy = (
                    occupancy[next_zone]
                    + reservations[next_zone]
                )

                if zone.zone_type == "restricted":
                    leaving_count = 0
                    for other_drone in self.drones:
                        if other_drone.in_transit:
                            continue
                        if other_drone.current_zone() != next_zone:
                            continue
                        if other_drone.next_zone() is None:
                            continue
                        leaving_count += 1
                    future_occupancy -= leaving_count
                if future_occupancy >= zone.max_drones:
                    continue

            if zone.zone_type == "restricted":
                occupancy[current_zone] -= 1
                connection_usage[edge_key] = used_capacity + 1
                reservations[next_zone] += 1
                drone.start_transit(
                    target_zone=next_zone,
                    remaining_turns=1,
                )
                move_count += 1
                connection_name = f"{connection.zone_a}-{connection.zone_b}"
                movements.append(f"D{drone.drone_id}-{connection_name}")
                continue
            occupancy[current_zone] -= 1
            occupancy[next_zone] += 1
            connection_usage[edge_key] = used_capacity + 1

            drone.move()
            move_count += 1
            movements.append(f"D{drone.drone_id}-{drone.current_zone()}")

        print(" ".join(movements))
        return move_count

    def all_arrived(self) -> bool:
        """Check whether all drones have reached their destinations.

        Returns:
            True if every drone has reached the end of its assigned
            path, otherwise False.
        """
        for drone in self.drones:
            if not drone.has_arrived():
                return False
        return True

    def get_zone_occupancy(self) -> dict[str, int]:
        """Calculate the current number of drones in each zone.

        Drones currently in transit are excluded from zone occupancy
        because they are moving between zones.

        Returns:
            A dictionary mapping zone names to the number of drones
            currently occupying each zone.
        """
        occupancy: dict[str, int] = {}

        for zone_name in self.map_data.zones:
            occupancy[zone_name] = 0
        for drone in self.drones:
            if drone.in_transit:
                continue
            zone_name = drone.current_zone()
            occupancy[zone_name] += 1
        return occupancy

    def get_connection(self, zone_a: str, zone_b: str) -> Connection | None:
        """Find the connection between two zones.

        Connections are treated as bidirectional, so the order
        of the zone names does not affect the search.

        Args:
            zone_a: Name of the first zone.
            zone_b: Name of the second zone.

        Returns:
            The Connection object linking the two zones,
            or None if no connection exists.
        """
        for connection in self.map_data.connections:
            if connection.zone_a == zone_a and connection.zone_b == zone_b:
                return connection

            if connection.zone_a == zone_b and connection.zone_b == zone_a:
                return connection
        return None

    def get_connection_usage(self) -> dict[tuple[str, str], int]:
        """Calculate connection usage by drones currently in transit.

        Each connection is represented by a tuple of zone names
        sorted lexicographically to ensure bidirectional consistency.

        Returns:
            A dictionary mapping connection keys to the number
            of drones currently in transit on each connection.
        """
        connection_usage: dict[tuple[str, str], int] = {}

        for drone in self.drones:
            if not drone.in_transit:
                continue
            if drone.target_zone is None:
                continue

            current_zone = drone.current_zone()
            edge_key: tuple[str, str]
            if current_zone <= drone.target_zone:
                edge_key = (current_zone, drone.target_zone)
            else:
                edge_key = (drone.target_zone, current_zone)

            connection_usage[edge_key] = (
                connection_usage.get(edge_key, 0) + 1
            )
        return connection_usage

    def get_zone_reservations(self) -> dict[str, int]:
        """Calculate destination zone reservations for drones in transit.

        Each drone currently moving toward a zone reserves one
        position in that destination zone.

        Returns:
            A dictionary mapping zone names to the number of
            incoming drones that have reserved space in each zone.
        """
        reservations: dict[str, int] = {}

        for zone_name in self.map_data.zones:
            reservations[zone_name] = 0

        for drone in self.drones:
            if not drone.in_transit:
                continue
            if drone.target_zone is None:
                continue
            reservations[drone.target_zone] += 1
        return reservations
