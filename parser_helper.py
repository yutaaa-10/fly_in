import sys
from models import Zone, MapData, Connection


class ParserHelper:
    def parse_metadata(
        self,
        metadata_text: str
    ) -> dict[str, str]:
        metadata: dict[str, str] = {}

        metadata_text = metadata_text.strip()

        if not metadata_text:
            return metadata

        if (
                not metadata_text.startswith("[")
                or not metadata_text.endswith("]")
        ):
            raise ValueError("Invalid metadata format")

        content = metadata_text[1:-1].strip()

        if not content:
            return metadata

        parts = content.split()

        for part in parts:
            if "=" not in part:
                raise ValueError(
                    f"Invalid metadata entry: {part}"
                )

            key, value = part.split("=", maxsplit=1)

            if not key or not value:
                raise ValueError(
                    f"Invalid metadata entry: {part}"
                )

            if key in metadata:
                raise ValueError(
                    f"Duplicate metadata key: {key}"
                )

            metadata[key] = value

        return metadata

    def parse_zone(
            self,
            line: str,
            line_number: int,
            map_data: MapData,
            ignore_max_drones: bool = False
    ) -> Zone | None:

        parts = line.split(":", maxsplit=1)

        if len(parts) != 2:
            print(
                f"Error on line {line_number}: invalid zone format",
                file=sys.stderr,
            )
            return None

        zone_text = parts[1].strip()

        if "[" in zone_text:
            base_text, metadata_text = zone_text.split("[", maxsplit=1)
            metadata_text = "[" + metadata_text
        else:
            base_text = zone_text
            metadata_text = ""

        values = base_text.split()

        if len(values) != 3:
            print(
                f"Error on line {line_number}: invalid zone format",
                file=sys.stderr,
            )
            return None

        name = values[0]

        if "-" in name or " " in name:
            print(
                f"Error on line {line_number}: invalid zone name '{name}'",
                file=sys.stderr,
            )
            return None

        if name in map_data.zones:
            print(
                f"Error on line {line_number}: duplicate zone '{name}'",
                file=sys.stderr,
            )
            return None

        try:
            x = int(values[1])
            y = int(values[2])
        except ValueError:
            print(
                f"Error on line {line_number}: coordinates must be integers",
                file=sys.stderr,
            )
            return None

        try:
            metadata = self.parse_metadata(metadata_text)
        except ValueError as error:
            print(
                f"Error on line {line_number}: {error}",
                file=sys.stderr,
            )
            return None

        allowed_metadata = {
            "zone",
            "color",
            "max_drones",
        }

        for key in metadata:
            if key not in allowed_metadata:
                print(
                    f"Error on line {line_number}: "
                    f"invalid metadata key '{key}'",
                    file=sys.stderr,
                )
                return None

        zone_type = metadata.get("zone", "normal")
        color = metadata.get("color", "none")
        max_drones_text = metadata.get("max_drones", "1")

        valid_zone_types = {
            "normal",
            "blocked",
            "restricted",
            "priority",
        }

        if zone_type not in valid_zone_types:
            print(
                f"Error on line {line_number}: "
                f"invalid zone type '{zone_type}'",
                file=sys.stderr,
            )
            return None

        if ignore_max_drones:
            max_drones = None
        else:
            max_drones_text = metadata.get("max_drones", "1")

            try:
                max_drones = int(max_drones_text)
            except ValueError:
                print(
                    f"Error on line {line_number}: "
                    "max_drones must be an integer",
                    file=sys.stderr,
                )
                return None

            if max_drones <= 0:
                print(
                    f"Error on line {line_number}: "
                    "max_drones must be positive",
                    file=sys.stderr,
                )
                return None

        return Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
        )

    def parse_connection(
        self,
        line: str,
        line_number: int,
        map_data: MapData
    ) -> Connection | None:
        parts = line.split(":", maxsplit=1)
        if len(parts) != 2:
            print(
                f"Error on line {line_number}: invalid connection format",
                file=sys.stderr,
            )
            return None

        connection_text = parts[1].strip()

        if "[" in connection_text:
            base_text, metadata_text = connection_text.split("[", maxsplit=1)
            metadata_text = "[" + metadata_text
        else:
            base_text = connection_text
            metadata_text = ""
        base_text = base_text.strip()

        zones = base_text.split("-")
        if len(zones) != 2:
            print(
                f"Error on line {line_number}: invalid connection format",
                file=sys.stderr,
            )
            return None
        zone_a = zones[0]
        zone_b = zones[1]
        if zone_a not in map_data.zones:
            print(
                f"Error on line {line_number}: "
                f"undefined zone '{zone_a}'",
                file=sys.stderr,
            )
            return None

        if zone_b not in map_data.zones:
            print(
                f"Error on line {line_number}: "
                f"undefined zone '{zone_b}'",
                file=sys.stderr,
            )
            return None

        try:
            metadata = self.parse_metadata(metadata_text)
        except ValueError as e:
            print(
                f"Error on line {line_number}: {e}",
                file=sys.stderr,
            )
            return None
        allowed_metadata = {"max_link_capacity"}

        for key in metadata:
            if key not in allowed_metadata:
                print(
                    f"Error on line {line_number}: "
                    f"invalid connection metadata key '{key}'",
                    file=sys.stderr,
                )
                return None

        max_capacity_text = metadata.get("max_link_capacity", "1")
        try:
            max_link_capacity = int(max_capacity_text)
        except ValueError:
            print(
                f"Error on line {line_number}: "
                "max_link_capacity must be an integer",
                file=sys.stderr,
            )
            return None

        if max_link_capacity <= 0:
            print(
                f"Error on line {line_number}: "
                "max_link_capacity must be positive",
                file=sys.stderr,
            )
            return None

        for connection in map_data.connections:
            same_direction = (
                connection.zone_a == zone_a
                and connection.zone_b == zone_b
            )
            reverse_direction = (
                connection.zone_a == zone_b
                and connection.zone_b == zone_a
            )
            if same_direction or reverse_direction:
                print(
                    f"Error on line {line_number}: duplicate connection",
                    file=sys.stderr,
                )
                return None
        return Connection(
            zone_a=zone_a,
            zone_b=zone_b,
            max_link_capacity=max_link_capacity,
        )
