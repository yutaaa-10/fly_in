import sys
from models import MapData
from parser_helper import ParserHelper



class Parser:
    def __init__(self) -> None:
        self.helper = ParserHelper()
    def parse(
            self,
            input_text: str,
    ) -> MapData | None:
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
                    drone_quantity = int(value)
                except ValueError:
                    print(
                        f"Error on line {line_number}: invalid nb_drones format",
                        file=sys.stderr,
                    )
                    return None

                if drone_quantity <= 0:
                    print(
                        f"Error on line {line_number}: "
                        "nb_drones must be positive",
                        file=sys.stderr,
                    )
                    return None

                map_data.drone_quantity = drone_quantity
                has_drones_quantity = True

            elif line.startswith("start_hub:"):
                if map_data.start_zone is not None:
                    print(
                        f"Error on line {line_number}: duplicate start_hub",
                        file=sys.stderr,
                    )
                    return None

                zone = self.helper.parse_zone(
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

                zone = self.helper.parse_zone(
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
                zone = self.helper.parse_zone(
                    line,
                    line_number,
                    map_data,
                )

                if zone is None:
                    return None

                map_data.zones[zone.name] = zone


            elif line.startswith("connection:"):
                connection = self.helper.parse_connection(
                    line,
                    line_number,
                    map_data,
                )

                if connection is None:
                    return None

                map_data.connections.append(connection)

            else:
                print(
                    f"Error on line {line_number}: invalid syntax",
                    file=sys.stderr,
                )
                return None

        if not has_drones_quantity:
            print(
                "Error: nb_drones is missing",
                file=sys.stderr,
            )
            return None

        if map_data.start_zone is None:
            print(
                "Error: start_hub is missing",
                file=sys.stderr,
            )
            return None

        if map_data.end_zone is None:
            print(
                "Error: end_hub is missing",
                file=sys.stderr,
            )
            return None

        return map_data
