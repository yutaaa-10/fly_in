from models import Drone, MapData, Connection


class Simulator:
    def __init__(self, drones: list[Drone], map_data: MapData) -> None:
        self.drones = drones
        self.turn = 0
        self.map_data = map_data

    def run(self) -> None:
        while not self.all_arrived():
            moved_count = self.run_turn()
            if moved_count == 0:
                print("Error: simulation deadlock")
                return

    def run_turn(self) -> int:
        self.turn += 1
        print(f"Turn {self.turn}")

        move_count = 0

        occupancy = self.get_zone_occupancy()
        connection_usage = self.get_connection_usage()
        reservations = self.get_zone_reservations()
        arrived_this_turn: set[int] = set()

        # Connection上を移動中のDroneを進める
        for drone in self.drones:
            if not drone.in_transit:
                continue

            target_zone = drone.target_zone
            drone.advance_transit()

            if not drone.in_transit:
                arrived_zone = drone.current_zone()

                if target_zone is not None:
                    reservations[target_zone] -= 1

                occupancy[arrived_zone] += 1
                arrived_this_turn.add(drone.drone_id)

                move_count += 1

                print(
                    f"D{drone.drone_id}-{arrived_zone}",
                    end=" ",
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

            connection = self.get_connection(
                current_zone,
                next_zone,
            )

            if connection is None:
                continue

            edge_key: tuple[str, str]
            if current_zone <= next_zone:
                edge_key = (current_zone, next_zone)
            else:
                edge_key = (next_zone, current_zone)

            used_capacity = connection_usage.get(
                edge_key,
                0,
            )

            if used_capacity >= connection.max_link_capacity:
                continue

            if zone.max_drones is not None:
                future_occupancy = (
                    occupancy[next_zone]
                    + reservations[next_zone]
                )

                if future_occupancy >= zone.max_drones:
                    continue

            # restricted Zoneへの移動
            if zone.zone_type == "restricted":
                occupancy[current_zone] -= 1

                connection_usage[edge_key] = (
                    used_capacity + 1
                )

                reservations[next_zone] += 1

                drone.start_transit(
                    target_zone=next_zone,
                    remaining_turns=1,
                )

                move_count += 1

                print(
                    f"D{drone.drone_id}-in_transit({next_zone})",
                    end=" ",
                )

                continue

            # 通常移動
            occupancy[current_zone] -= 1
            occupancy[next_zone] += 1

            connection_usage[edge_key] = (
                used_capacity + 1
            )

            drone.move()

            move_count += 1

            print(
                f"D{drone.drone_id}-{drone.current_zone()}",
                end=" ",
            )

        print()

        return move_count

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
            if drone.in_transit:
                continue
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

    def get_connection_usage(
        self,
    ) -> dict[tuple[str, str], int]:
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
