from models import MapData


class Graph:
    """Represent the drone network as an adjacency list.

    This class builds a bidirectional graph from map data and
    provides methods to retrieve neighboring zones and movement costs.

    Attributes:
        map_data: Map data containing zones and connections.
        adjacency: Dictionary mapping each zone to its neighboring zones.
    """

    def __init__(self, map_data: MapData) -> None:
        """Initialize the graph and build its adjacency list.

        Args:
            map_data: Map data containing zones and connections.
        """
        self.map_data = map_data
        self.adjacency: dict[str, list[str]] = {}

        self.build_adjacency()

    def build_adjacency(self) -> None:
        """Build a bidirectional adjacency list from map connections.

        Returns:
            List of neighboring zone names.
        """
        for name in self.map_data.zones:
            self.adjacency[name] = []

        for connection in self.map_data.connections:
            zone_a = connection.zone_a
            zone_b = connection.zone_b
            self.adjacency[zone_a].append(zone_b)
            self.adjacency[zone_b].append(zone_a)

        return None

    def get_neighbors(self, zone_name: str) -> list[str]:
        """Retrieve the neighboring zones of a specified zone.

        Args:
            zone_name: Name of the zone.

        Returns:
            List of neighboring zone names.
        """
        return self.adjacency[zone_name]

    def get_move_cost(self, zone_name: str) -> int | None:
        """Get the movement cost of entering a specified zone.

        Args:
            zone_name: Name of the destination zone.

        Returns:
            Movement cost in turns based on the zone type.
            Returns None if the zone is blocked or has an unknown type.
        """
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
