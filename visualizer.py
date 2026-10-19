import sys
from simulator import Simulator
import math
from models import Drone
from models import MapData, Zone
import pygame
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"


class PygameVisualizer:
    """Display and control the drone routing simulation.

    This class renders zones, connections, and drones using Pygame.
    It supports manual turn advancement and automatic playback.

    Attributes:
        map_data: Map configuration containing zones and connections.
        drones: List of drones participating in the simulation.
        simulator: Simulator responsible for updating drone states.
        width: Width of the visualization window.
        height: Height of the visualization window.
        screen: Pygame surface used for rendering.
        clock: Pygame clock used to control the frame rate.
        font: Font used to display zone names.
        playing: Whether automatic playback is enabled.
        turn_interval: Time interval between automatic turns in milliseconds.
        last_turn_time: Timestamp of the last automatic turn.
        scale: Initial scale value.
        offset_x: Initial horizontal offset value.
        offset_y: Initial vertical offset value.
    """

    def __init__(
        self,
        map_data: MapData,
        drones: list[Drone],
        simulator: Simulator,
        width: int = 1000,
        height: int = 700
    ) -> None:
        """Initialize the Pygame visualization window.

        Args:
            map_data: Map configuration containing zones and connections.
            drones: List of drones to visualize.
            simulator: Simulator used to advance the simulation.
            width: Width of the window in pixels. Defaults to 1000.
            height: Height of the window in pixels. Defaults to 700.
        """
        pygame.init()
        self.map_data = map_data
        self.drones = drones
        self.simulator = simulator
        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly_in")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 16)
        self.turn_font = pygame.font.SysFont(None, 45)

        self.playing = False
        self.turn_interval = 500
        self.last_turn_time = pygame.time.get_ticks()

        self.scale = 200
        self.offset_x = 400
        self.offset_y = 400

    def run(self) -> None:
        """Run the visualization event loop until the window is closed.

        This method processes keyboard and window events,
        advances simulation turns during automatic playback,
        renders the map and drones, and updates the display.

        Press Space to advance one turn manually.
        Press Enter to toggle automatic playback.
        """
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.playing = False
                        self.advance_turn()
                    elif event.key == pygame.K_RETURN:
                        self.playing = not self.playing
                        self.last_turn_time = pygame.time.get_ticks()
            if self.playing:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_turn_time >= self.turn_interval:
                    self.advance_turn()
                    self.last_turn_time = current_time
            self.screen.fill((30, 30, 30))
            self.draw_connections()
            self.draw_zones()
            self.draw_drones(self.drones)
            self.draw_transit_drones(self.drones)

            turn_text = self.turn_font.render(
                f"Turn: {self.simulator.turn}",
                True,
                (255, 255, 255),
            )
            self.screen.blit(turn_text, (20, 20))

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def to_screen(self, x: int, y: int) -> tuple[int, int]:
        """Convert map coordinates into screen pixel coordinates.

        This method calculates the map boundaries and determines
        a scale that fits all zones within the visualization window.

        Args:
            x: Horizontal coordinate in the map.
            y: Vertical coordinate in the map.

        Returns:
            A tuple containing the horizontal and vertical
            screen coordinates in pixels.
        """
        zones = self.map_data.zones.values()
        min_x = min(zone.x for zone in zones)
        max_x = max(zone.x for zone in zones)
        min_y = min(zone.y for zone in zones)
        max_y = max(zone.y for zone in zones)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        map_width = max(max_x - min_x, 1)
        map_height = max(max_y - min_y, 1)

        margin = 50
        scale_x = (self.width - margin * 2) / map_width
        scale_y = (self.height - margin * 2) / map_height
        scale = min(scale_x, scale_y)

        screen_x = (x - center_x) * scale + self.width / 2
        screen_y = (y - center_y) * scale + self.height / 2
        return (int(screen_x), int(screen_y))

    def draw_connections(self) -> None:
        """Draw all connections between zones.

        Each connection is rendered as a line between the
        screen coordinates of its two endpoint zones.
        """
        for connection in self.map_data.connections:
            zone_a = self.map_data.zones[connection.zone_a]
            zone_b = self.map_data.zones[connection.zone_b]

            start_pos = self.to_screen(zone_a.x, zone_a.y)
            end_pos = self.to_screen(zone_b.x, zone_b.y)
            pygame.draw.line(
                self.screen,
                (180, 180, 180),
                start_pos,
                end_pos,
                3,
            )

    def draw_zones(self) -> None:
        """Draw all zones with their configured colors and names.

        Each zone is rendered as a circle at its screen coordinates.
        The color is determined by get_zone_color(), which prioritizes
        the user-defined color over the default zone type color.

        Zone names are displayed above their corresponding circles.
        """
        for zone in self.map_data.zones.values():
            position = self.to_screen(zone.x, zone.y)

            color = self.get_zone_color(zone)

            pygame.draw.circle(
                self.screen,
                color,
                position,
                25,
            )

            text = self.font.render(
                zone.name,
                True,
                (255, 255, 255),
            )
            text_rect = text.get_rect(
                center=(position[0], position[1] - 25)
            )
            self.screen.blit(text, text_rect)

    def get_zone_color(self, zone: Zone) -> tuple[int, int, int]:
        """Determine the display color of a zone.

        If the zone has a supported custom color, its corresponding
        RGB value is returned. Otherwise, a default color is selected
        based on the zone type.

        Args:
            zone: Zone object containing its type and color attributes.

        Returns:
            A tuple of three integers representing the RGB color.
        """
        default_colors = {
            "start": (0, 200, 0),
            "end": (200, 50, 50),
            "blocked": (100, 100, 100),
            "restricted": (255, 165, 0),
            "priority": (255, 215, 0),
            "normal": (70, 130, 180),
        }

        if zone.color and zone.color != "name":
            try:
                color = pygame.Color(zone.color)
                return (color.r, color.g, color.b)
            except ValueError:
                pass

        return default_colors.get(
            zone.zone_type,
            (70, 130, 180),
        )

    def draw_drones(self, drones: list[Drone]) -> None:
        """Draw drones at their current zones.

        Drones are grouped by their current zone.
        When multiple drones share a zone, they are arranged
        in a circular pattern around the zone center.

        Args:
            drones: List of drones to render.
        """
        zone_drones: dict[str, list[Drone]] = {}

        for drone in drones:
            if drone.in_transit:
                continue
            zone_name = drone.current_zone()
            if zone_name not in zone_drones:
                zone_drones[zone_name] = []
            zone_drones[zone_name].append(drone)

        for zone_name, drone_list in zone_drones.items():
            zone = self.map_data.zones[zone_name]
            center_x, center_y = self.to_screen(zone.x, zone.y)

            count = len(drone_list)

            for index, drone in enumerate(drone_list):
                if count == 1:
                    x = float(center_x)
                    y = float(center_y)
                else:
                    angle = 2 * math.pi * index / count

                    radius = 22
                    x = center_x + math.cos(angle) * radius
                    y = center_y + math.sin(angle) * radius

                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    (int(x), int(y)),
                    6,
                )
                id_text = self.font.render(
                    f"D{drone.drone_id}",
                    True,
                    (255, 255, 255),
                )
                text_rect = id_text.get_rect(
                    center=(int(x), int(y) - 15)
                )
                self.screen.blit(id_text, text_rect)

    def draw_transit_drones(self, drones: list[Drone]) -> None:
        """Draw drones currently moving through restricted connections."""
        for drone in drones:
            if not drone.in_transit:
                continue

            current_zone_name = drone.current_zone()
            target_zone_name = drone.target_zone

            if target_zone_name is None:
                continue

            current_zone = self.map_data.zones[current_zone_name]
            target_zone = self.map_data.zones[target_zone_name]

            start_x, start_y = self.to_screen(
                current_zone.x,
                current_zone.y,
            )

            end_x, end_y = self.to_screen(
                target_zone.x,
                target_zone.y,
            )

            x = (start_x + end_x) // 2
            y = (start_y + end_y) // 2
            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                (x, y),
                8,
            )
            id_text = self.font.render(
                f"D{drone.drone_id}",
                True,
                (255, 255, 255),
            )
            text_rect = id_text.get_rect(
                center=(x, y - 18)
            )
            self.screen.blit(id_text, text_rect)

    def advance_turn(self) -> None:
        """Advance the simulation by one turn.

        This method stops playback if all drones have arrived
        or if the simulator detects a deadlock.
        """
        if self.simulator.all_arrived():
            self.playing = False
            return

        moved_count = self.simulator.run_turn()

        if moved_count == 0:
            print("Error: simulation deadlock", file=sys.stderr)
            self.playing = False
            return

        if self.simulator.all_arrived():
            self.playing = False
