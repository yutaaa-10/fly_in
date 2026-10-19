"""Define data models for maps, zones, connections, and drones."""


class MapData:
    """Store the map configuration for the drone routing simulation.

    Attributes:
        drone_quantity: Total number of drones in the simulation.
        zones: Dictionary mapping zone names to Zone objects.
        connections: List of connections between zones.
        start_zone: Name of the starting zone.
        end_zone: Name of the destination zone.
    """

    def __init__(self) -> None:
        """Initialize an empty map configuration."""
        self.drone_quantity = 0
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.start_zone: str | None = None
        self.end_zone: str | None = None


class Connection:
    """Represent a bidirectional connection between two zones.

    Attributes:
        zone_a: Name of the first connected zone.
        zone_b: Name of the second connected zone.
        max_link_capacity: Maximum number of drones allowed on the connection.
    """

    def __init__(
        self,
        zone_a: str,
        zone_b: str,
        max_link_capacity: int = 1,
    ) -> None:
        """Initialize a connection between two zones.

        Args:
            zone_a: Name of the first zone.
            zone_b: Name of the second zone.
            max_link_capacity: Maximum number of drones allowed
                on the connection. Defaults to 1.
        """
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity


class Zone:
    """Represent a zone in the drone routing network.

    Attributes:
        name: Unique name of the zone.
        x: Horizontal coordinate of the zone.
        y: Vertical coordinate of the zone.
        zone_type: Type of zone (normal, priority, restricted, or blocked).
        color: Color used for visual representation.
        max_drones: Maximum number of drones allowed in the zone.
            None indicates unlimited capacity.
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        color: str = "none",
        max_drones: int | None = 1,
    ) -> None:
        """Initialize a zone with its properties.

        Args:
            name: Unique name of the zone.
            x: Horizontal coordinate of the zone.
            y: Vertical coordinate of the zone.
            zone_type: Type of zone. Defaults to "normal".
            color: Color used for visualization. Defaults to "none".
            max_drones: Maximum number of drones allowed in the zone.
                Defaults to 1. None indicates unlimited capacity.
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones


class Drone:
    """Represent a drone moving along an assigned path.

    Attributes:
        drone_id: Unique identifier of the drone.
        path: List of zone names forming the assigned route.
        path_index: Index of the current zone in the path.
        in_transit: Whether the drone is moving through a connection.
        remaining_turns: Number of turns remaining before arrival.
        target_zone: Destination zone during transit, or None.
    """

    def __init__(
        self,
        drone_id: int,
        path: list[str],
    ) -> None:
        """Initialize a drone with an identifier and assigned path.

        Args:
            drone_id: Unique identifier of the drone.
            path: Ordered list of zone names representing the route.
        """
        self.drone_id = drone_id
        self.path = path
        self.path_index = 0
        self.in_transit = False
        self.remaining_turns = 0
        self.target_zone: str | None = None

    def current_zone(self) -> str:
        """Return the current zone name based on the path index.

        Returns:
            Name of the current zone in the assigned path.
        """
        return self.path[self.path_index]

    def next_zone(self) -> str | None:
        """Get the next zone in the assigned path.

        Returns:
            Name of the next zone, or None if the drone is at
            the end of its path.
        """
        if self.path_index + 1 >= len(self.path):
            return None
        return self.path[self.path_index + 1]

    def move(self) -> None:
        """Advance the drone to the next zone in its assigned path."""
        if self.next_zone() is not None:
            self.path_index += 1

    def start_transit(self, target_zone: str, remaining_turns: int) -> None:
        """Start a multi-turn movement toward a target zone.

        Args:
            target_zone: Name of the destination zone.
            remaining_turns: Number of turns until arrival.
        """
        self.in_transit = True
        self.target_zone = target_zone
        self.remaining_turns = remaining_turns

    def advance_transit(self) -> None:
        """Advance an ongoing multi-turn movement by one turn.

        Decrease the remaining turn count. When the count reaches
        zero, update the path index and clear the transit state.
        """
        if not self.in_transit:
            return
        self.remaining_turns -= 1
        if self.remaining_turns <= 0:
            self.path_index += 1
            self.in_transit = False
            self.target_zone = None

    def has_arrived(self) -> bool:
        """Check whether the drone has reached the end of its path.

        Returns:
            True if the drone is at the last zone in its path,
            otherwise False.
        """
        return self.path_index == len(self.path) - 1
