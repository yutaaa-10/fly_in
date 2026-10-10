
class MapData:
    def __init__(self) -> None:
        self.drone_quantity = 0
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.start_zone: str | None = None
        self.end_zone: str | None = None


class Connection:
    def __init__(
        self,
        zone_a: str,
        zone_b: str,
        max_link_capacity: int = 1,
    ) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity


class Zone:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        color: str = "none",
        max_drones: int | None = 1,
    ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones


class Drone:
    def __init__(
        self,
        drone_id: int,
        path: list[str],
    ) -> None:
        self.drone_id = drone_id
        self.path = path
        self.path_index = 0
        self.in_transit = False
        self.remaining_turns = 0
        self.target_zone: str | None = None

    def current_zone(self) -> str:
        return self.path[self.path_index]

    def next_zone(self) -> str | None:
        if self.path_index + 1 >= len(self.path):
            return None
        return self.path[self.path_index + 1]

    def move(self) -> None:
        if self.next_zone() is not None:
            self.path_index += 1

    def start_transit(
        self,
        target_zone: str,
        remaining_turns: int,
    ) -> None:
        self.in_transit = True
        self.target_zone = target_zone
        self.remaining_turns = remaining_turns

    def advance_transit(self) -> None:
        if not self.in_transit:
            return
        self.remaining_turns -= 1
        if self.remaining_turns <= 0:
            self.path_index += 1
            self.in_transit = False
            self.target_zone = None

    def has_arrived(self) -> bool:
        return self.path_index == len(self.path) - 1
