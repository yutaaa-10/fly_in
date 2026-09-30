import argparse
import sys


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


def parse_input_file(input_text: str) -> bool:

    has_drone_quantity = False
    drone_quantity = 0

    lines = input_text.splitlines()

    for line_number, line in enumerate(lines, start=1):
        line = line.strip()

        if not line:
            continue
        if line.startswith('#'):
            continue

        if not has_drone_quantity and line.startswith("nb_drones:"):
            parts = line.split(":", maxsplit=1)
            drone_quantity = int(parts[1].strip())
            has_drone_quantity = True
    return False


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
