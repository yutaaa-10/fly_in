import argparse
import sys


class MapData:
    def __init__(self) -> None:
        self.drone_quantity = 0
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.atart_zone: str | None = None
        self.end_zone: str | None = None

class Zone:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        color: str = "none",
        max_drones: int = 1,
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




        # if not has_drone_quantity and line.startswith("nb_drones:"):
        #     parts = line.split(":", maxsplit=1)
        #     drone_quantity = int(parts[1].strip())
        #     has_drone_quantity = True



def parse_input_file(input_text: str) -> MapData | None:
    map_data = MapData()

    lines = input_text.splitlines()

    for line_number, line in enumerate(lines, start=1):
        line = line.strip()

        if not line:
            continue
        if line.startswith("#"):
            continue

        if line.startswith("nb_drones:"):
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

        # elif line.startswith("start_hub:"):
        #     ...
        #     map_data.zones[name] = zone
        #     map_data.start_zone = name

        # elif line.startswith("hub:"):
        #     ...
        #     map_data.zones[name] = zone

        # elif line.startswith("end_hub:"):
        #     ...
        #     map_data.zones[name] = zone
        #     map_data.end_zone = name

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
