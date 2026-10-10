from models import MapData


class Graph:
    def __init__(self, map_data: MapData) -> None:
        self.map_data = map_data
        self.adjacency: dict[str, list[str]] = {}

        self.build_adjacency()

    def build_adjacency(self) -> None:
        for name in self.map_data.zones:
            self.adjacency[name] = []

        for connection in self.map_data.connections:
            zone_a = connection.zone_a
            zone_b = connection.zone_b
            self.adjacency[zone_a].append(zone_b)
            self.adjacency[zone_b].append(zone_a)

    def get_neighbors(self, zone_name: str) -> list[str]:
        return self.adjacency[zone_name]

    def get_move_cost(self, zone_name: str) -> int:
        zone = self.map_data.zones[zone_name]

        if zone.zone_type == "normal":
            return 1
        if zone.zone_type == "priority":
            return 1
        if zone.zone_type == "restricted":
            return 2
        if zone.zone_type == "blocked":
            return None

        return None
