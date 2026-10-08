from models import Drone, MapData, Connection


class Simulator:
    def __init__(self, drones: list[Drone], map_data: MapData) -> None:
        self.drones = drones
        self.turn = 0
        self.map_data = map_data

    def run(self) -> None:
        while not self.all_arrived():
            self.run_turn()

    def run_turn(self) -> None:
        self.turn += 1
        print(f"Turn {self.turn}")

        occupancy = self.get_zone_occupancy()
        connection_usage: dict[tuple[str, str], int] = {}

        drones = sorted(
            self.drones,
            key=lambda drone: drone.path_index,
            reverse=True,
        )

        for drone in drones:    
            if drone.has_arrived():
                continue
            current_zone = drone.current_zone()
            next_zone = drone.next_zone()
            if next_zone is None:
                continue
            zone = self.map_data.zones[next_zone]

            connection = self.get_connection(
                current_zone,
                next_zone,
            )
            if connection is None:
                continue

            edge_key = tuple(sorted(
                (current_zone, next_zone)
            ))
            used_capacity = connection_usage.get(
                edge_key,
                0,
            )
            if used_capacity >= connection.max_link_capacity:
                continue
            if zone.max_drones is not None:
                if occupancy[next_zone] >= zone.max_drones:
                    continue
            occupancy[current_zone] -= 1
            occupancy[next_zone] += 1
            connection_usage[edge_key] = used_capacity + 1
            drone.move()
            print(
                f"D{drone.drone_id}-{drone.current_zone()}",
                end=" ",
            )
        print()

    def all_arrived(self) -> bool:
        for drone in self.drones:
            if not drone.has_arrived():
                return False
        return True

    def get_zone_occupancy(self) -> dict[str, int]:
        occupancy: dict[str, int] = {}

        for zone_name in self.map_data.zones:
            occupancy[zone_name] = 0
        for drone in self.drones:
            zone_name = drone.current_zone()
            occupancy[zone_name] += 1
        return occupancy

    def get_connection(self, zone_a: str, zone_b: str) -> Connection | None:
        for connection in self.map_data.connections:
            if connection.zone_a == zone_a and connection.zone_b == zone_b:
                return connection

            if connection.zone_a == zone_b and connection.zone_b == zone_a:
                return connection
        return None

