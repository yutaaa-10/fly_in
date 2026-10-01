import argparse
import sys


class MapData:
    def __init__(self) -> None:
        self.drone_quantity = 0
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.start_zone: str | None = None
        self.end_zone: str | None = None

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




def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Drone routiong simulation"
    )

    parser.add_argument(
        "map_file",
        help="Path to the map file"
    )

    return parser.parse_args()


def open_file(map_file: str) -> str | None:
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


def parse_metadata(metadata_text: str) -> dict[str, str]:
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
        metadata = parse_metadata(metadata_text)
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


def parse_input_file(input_text: str) -> MapData | None:
    map_data = MapData()

    lines = input_text.splitlines()
    has_drones_quantity = False

    for line_number, line in enumerate(lines, start=1):
        line = line.strip()

        if not line:
            continue
        if line.startswith("#"):
            continue


        if line.startswith("nb_drones:"):

            if has_drones_quantity:
                print(
                    f"Error on line {line_number}: duplicate nb_drones",
                    file=sys.stderr,
                )
                return None

            parts = line.split(":", maxsplit=1)

            if len(parts) != 2:
                print(
                    f"Error on line {line_number}: invalid nb_drones format",
                    file=sys.stderr,
                )
                return None

            value = parts[1].strip()
            try:
                drone_quantity = int (value)
            except ValueError:
                print(
                    f"Error on line {line_number}: invalid nb_drones format",
                    file=sys.stderr,
                )
                return None

            if drone_quantity <= 0:
                print(
                    f"Error on line {line_number}: nb_droes must be positive",
                    file=sys.stderr,
                )
                return None
            map_data.drone_quantity = drone_quantity


        elif line.startswith("start_hub:"):
            if map_data.start_zone is not None:
                print(
                    f"Error on line {line_number}: duplicate start_hub",
                    file=sys.stderr,
                )
                return None

            zone = parse_zone(
                line,
                line_number,
                map_data,
                ignore_max_drones=True,
            )

            if zone is None:
                return None

            map_data.zones[zone.name] = zone
            map_data.start_zone = zone.name


        elif line.startswith("end_hub:"):
            if map_data.end_zone is not None:
                print(
                    f"Error on line {line_number}: duplicate end_hub",
                    file=sys.stderr,
                )
                return None

            zone = parse_zone(
                line,
                line_number,
                map_data,
                ignore_max_drones=True,
            )

            if zone is None:
                return None

            map_data.zones[zone.name] = zone
            map_data.end_zone = zone.name

        elif line.startswith("hub:"):
            zone = parse_zone(line, line_number, map_data)
            if zone is None:
                return None
            map_data.zones[zone.name] = zone
      


        # elif line.startswith("connection:"):
        #     ...
        #     map_data.connections.append(connection)

        # else:
        #     # parsing error
        #     return None

    return map_data


def main() -> int:
    args = parse_arguments()

    input_text = open_file(args.map_file)
    if input_text is None:
        return 1

    if not parse_input_file(input_text):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
