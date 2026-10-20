*This project has been created as part of the 42 curriculum by yukurosa.*

# Fly-in

## Description

Fly-in is a pathfinding and simulation project that efficiently routes multiple drones from a start zone to a goal zone.
The map is represented as a graph consisting of zones (vertices) and connections (edges).
The objective is to minimize the total number of turns needed to deliver all drones while respecting zone capacities, connection capacities, and movement costs, rather than simply finding a shortest path.
Pygame provides a visual representation of drone movements.

### Program Structure

1. Parse command-line arguments.
2. Read the map file.
3. Parse and validate the input with `Parser`.
4. Build the `Graph`.
5. Find paths with `PathFinder`.
6. Assign drones to paths with `Router`.
7. Create `Drone` objects.
8. Start the `PygameVisualizer` event loop.
9. Advance the `Simulator` by one turn in response to keyboard input or automatic playback, then render the updated state.

### Main Classes and Responsibilities

| Class | Responsibility |
|---|---|
| Application | Coordinate the overall execution of the program |
| Parser | Parse and validate the input file |
| MapData | Store map information |
| Graph | Build the graph |
| PathFinder | Find paths |
| Router | Assign drones to paths |
| Drone | Manage an individual drone's state |
| Simulator | Simulate drone movements |
| PygameVisualizer | Display the simulation using Pygame |

## Instructions

### Requirements and Installation

Python 3.10 or later and a desktop environment capable of displaying a Pygame window are required.
Graph logic is implemented directly without graph-processing libraries such as networkx or graphlib.

From the repository root, create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

`make install` installs Pygame for visualization, along with flake8 and mypy for code checks.

### Running from the Command Line

```bash
python3 main.py <map_file>
```

### Running with the Makefile

```bash
make run
```

To select a map file:

```bash
make run MAP=maps/medium/01_dead_end_trap.txt
```

If no map is specified, `make run` uses `maps/easy/01_linear_path.txt`.
Both execution methods open a Pygame window.
The simulation starts paused. Press Space or Enter to advance it.

### Code Checks and Development Commands

```bash
make lint
make lint-strict
make debug MAP=maps/easy/01_linear_path.txt
make clean
```

- `lint`: Run flake8 and mypy with the options required by the assignment.
- `lint-strict`: Run flake8 and mypy in strict mode.
- `debug`: Start the program with Python's pdb debugger.
- `clean`: Remove Python, type-checker, and other cache files.

### Pygame Controls

| Key | Action |
|---|---|
| Space | Pause automatic playback and advance one turn |
| Enter | Toggle automatic playback and pause |

Automatic playback advances one turn every 0.5 seconds.
It stops when all drones have reached the goal.
Close the window to exit the program.

### Simulation Output

#### Terminal Output

The program prints the drone movements for each turn.
A complete input and its corresponding output are provided in the "Example Input and Expected Output" section below.

- Each turn occupies one line, with movements separated by spaces.
- Normal movements and arrivals use `D<ID>-<zone>`.
- A movement toward a restricted zone starts with `D<ID>-<connection>`. The connection name consists of its two endpoint zone names joined by a hyphen, in the order defined in the input.
- A drone reaches a restricted zone on the turn immediately after departure, and its arrival is printed using the destination zone name.
- Waiting drones are omitted. Delivered drones do not appear in subsequent movement logs.
- Error messages are printed to standard error.

#### Visualization

Pygame renders the states of zones, connections, and drones.

### Input Data

Map files define the number of drones, zones, and connections.

Zones have integer coordinates, and connections are bidirectional.
Zone names cannot contain hyphens or whitespace. Connections must reference zones defined earlier in the file.

Everything from `#` to the end of a line is ignored as a comment. Both full-line and inline comments are supported.
The first line, excluding blank lines and comments, must specify a positive integer number of drones.

```text
# Define the number of drones
nb_drones: 5 # Inline comments are also supported
```

| Metadata | Applies to | Default and Meaning |
|---|---|---|
| `zone` | Zone | `normal`; the destination zone's type |
| `color` | Zone | `none`; use the specified color if Pygame recognizes it, otherwise use the default color for the zone type |
| `max_drones` | Zone | `1`; the maximum number of drones occupying the zone simultaneously |
| `max_link_capacity` | Connection | `1`; the maximum number of drones traversing the connection simultaneously |

The start and goal zones have unlimited capacity. Their `max_drones` metadata is ignored if present.

| Zone Type | Movement Cost | Behavior |
|---|---|---|
| `normal` | 1 turn | Standard destination zone |
| `priority` | 1 turn | Prefer paths containing more priority zones when movement costs are equal |
| `restricted` | 2 turns | Handle departure onto the connection and arrival on separate turns |
| `blocked` | Inaccessible | Exclude from pathfinding and movement |

#### Example Input

See "Example Input and Expected Output" below for the output corresponding to this map.

```text
nb_drones: 5

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: dead_end 1 1 [color=red]
hub: correct_path 2 0 [color=blue]
hub: intermediate 3 0 [color=blue]
end_hub: goal 4 0 [color=green]

connection: start-junction [max_link_capacity=2]
connection: junction-dead_end
connection: junction-correct_path
connection: correct_path-intermediate
connection: intermediate-goal
```

## Additional Details: Algorithms and Implementation Strategy

### Algorithm Details

The program first parses the input file and builds a graph of zones and connections.
It then uses depth-first search (DFS) and backtracking to discover paths from the start to the goal.
The Router assigns drones based on path costs and estimated congestion.
The Simulator advances drones turn by turn while checking zone and connection capacities.

#### Pathfinding with DFS

Fly-in uses DFS and backtracking to enumerate all simple paths from the start to the goal so that multiple routes can be considered when assigning drones.

#### Search Procedure

1. Begin at the start zone.
2. Retrieve the current zone's neighbors.
3. Exclude blocked zones and zones already included in the current search path.
4. Recursively explore a neighboring zone that is not in the current path.
5. When the goal is reached, save a copy of the current path.
6. Backtrack to the previous zone and explore other paths.

#### Path Assignment with the Router

The Router assigns drones to the paths discovered by DFS.
Sending every drone along the shortest path can cause waiting because of zone and connection capacities.
Instead, a greedy algorithm assigns drones one at a time, considering both movement costs and estimated connection congestion.

#### Estimating Congestion

For each connection, estimate how many groups are needed to pass the projected number of drones through it.
Each group contains no more drones than the connection's capacity:

```text
required_waves = ceil(projected_load / capacity)
```

- `projected_load`: The projected number of drones assigned to use the connection.
- `capacity`: The connection's maximum capacity.

The movement cost of the destination zone is then used to estimate congestion pressure for the connection:

```text
pressure = required_waves * move_cost
```

The path's congestion estimate is the largest pressure among its connections:

```text
congestion = max(pressure for each connection in the path)
score = path_cost + congestion
```

`move_cost` is the cost of entering the destination zone. `path_cost` is the sum of destination zone costs along the path, excluding the start zone.
`projected_load` includes previously assigned drones plus the drone currently being assigned.
This score estimates congestion; it does not calculate the exact arrival turn.
Zone capacity is not included directly in the Router's score. The Simulator checks it when deciding whether a movement is possible.

#### Assigning Drones

1. Calculate a score for each path.
2. Select the path with the lowest score.
3. Assign one drone to that path.
4. Update the loads of the connections along the selected path.
5. Repeat until all drones have been assigned.

Considering congestion as well as movement cost helps distribute drones across paths and reduce the completion time.
This greedy assignment is a heuristic and does not guarantee a globally optimal solution.

#### Greedy Algorithm

A greedy algorithm repeatedly chooses the option considered best at the current step.
In this project, each drone is assigned to the path with the lowest score based on movement cost and estimated congestion.
After each assignment, connection loads are updated so that subsequent assignments reflect the additional traffic.
Repeating this process aims to avoid concentrating all drones on one route.
However, making the best local choice at each step does not necessarily produce the best overall solution.

#### Complexity and Limitations

Paths and their costs are calculated before the simulation starts. Paths are not recalculated every turn.
Enumerating all simple paths can produce a rapidly growing number of candidates in dense graphs, increasing both runtime and memory usage.
The usual DFS complexity of `O(V + E)` does not describe the cost of enumerating all simple paths.

Let `P` be the number of candidate paths, `L` the maximum path length, and `D` the number of drones.
Storing the paths requires `O(P * L)` memory, and the Router's assignment process takes approximately `O(D * P * L)` time.
The implementation does not guarantee a globally optimal solution or the target turn count for every possible map.

#### Movement Simulation

Once the Router has selected a path for each drone, the Simulator processes movement in discrete turns.
Drones follow their assigned paths while zone and connection capacities are checked.

#### Processing One Turn

1. Increment the turn number and calculate zone occupancy, connection usage, and destination reservations.
2. Advance drones already in transit. On arrival, update zone occupancy and reduce the destination reservation and connection usage counts.
3. Sort drones according to their progress along their paths.
4. Check whether each drone can enter its next zone.
5. Update the state of drones that can move; otherwise, leave them waiting.
6. Print the movements for the turn.

#### Restricted Zone Handling

Entering a restricted zone takes two turns instead of the single turn required for a normal zone.
Departure and arrival are handled on consecutive turns: the drone must arrive on the turn immediately after departure and cannot wait additional turns on the connection.
Drones in transit are excluded from zone occupancy and are tracked through connection usage and destination zone reservations.

##### Completion and Deadlock Detection

Once every drone reaches the goal, movement processing is complete and automatic playback stops.
The visualization window remains open until it is closed by the user.
If unfinished drones remain but no movement starts or finishes during a turn, the program reports a deadlock to standard error and stops automatic playback.

### Visual Representation

Pygame displays the map and drone movements.
The graph of zones and connections shows drone positions at each turn.
This makes routes and waiting behavior easier to understand than terminal output alone.

#### Map Visualization

Zones are drawn as circles and connections as lines, with each zone's name displayed.
If a `color` is specified and recognized by Pygame, that color takes precedence.
Otherwise, the following default colors are used according to the zone type:

| Zone Type | Color |
|---|---|
| Normal | Blue |
| Priority | Gold |
| Restricted | Orange |
| Blocked | Gray |

This helps identify the map's connections and the locations of restricted and blocked zones when the default colors are used.

The start and goal zones also prioritize their specified `color`; otherwise, they use the default for their zone type.
The parser does not restrict color names to a fixed list. Unrecognized names fall back to a default during rendering rather than causing an exception to stop the program.
For example, the Challenger map's `rainbow` value is not recognized as a Pygame color name, so the default color is used instead of a rainbow effect.

#### Drone Visualization

Drones are drawn as small white circles labeled with their IDs.
When multiple drones share a zone, sine and cosine are used to distribute them evenly around a circle.
This reduces overlap and makes the number of drones at a zone easier to see.

Drones moving toward a restricted zone are displayed at the midpoint of the connection.
This distinguishes normal zone movements from the two-turn transit required to enter restricted zones.
Delivered drones are excluded from further movement processing but remain visible at the goal.

#### Simulation Controls

Keyboard input controls simulation progress.

| Key | Action |
|---|---|
| Space | Advance one turn |
| Enter | Toggle automatic playback and pause |

Automatic playback advances one turn every 0.5 seconds.
Manual stepping allows movements and waiting behavior to be inspected turn by turn, while automatic playback shows the overall flow.
Playback stops when all drones have reached the goal.

#### Integration with the Simulator

The Simulator updates drone movement states, and the PygameVisualizer renders those states.
Separating simulation logic from rendering allows the display to be improved without changing the movement logic.

### Example Input and Expected Output

#### Input

`maps/medium/01_dead_end_trap.txt`

```text
nb_drones: 5

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: dead_end 1 1 [color=red]
hub: correct_path 2 0 [color=blue]
hub: intermediate 3 0 [color=blue]
end_hub: goal 4 0 [color=green]

connection: start-junction [max_link_capacity=2]
connection: junction-dead_end
connection: junction-correct_path
connection: correct_path-intermediate
connection: intermediate-goal
```

#### Command

```bash
python3 main.py maps/medium/01_dead_end_trap.txt
```

#### Expected Output

Press Space to advance manually or Enter to start automatic playback. The Simulator prints each turn's movements to standard output.
With the current implementation, all five drones reach the goal in eight turns:

```text
D1-junction D2-junction
D1-correct_path D3-junction
D1-intermediate D2-correct_path D4-junction
D1-goal D2-intermediate D3-correct_path D5-junction
D2-goal D3-intermediate D4-correct_path
D3-goal D4-intermediate D5-correct_path
D4-goal D5-intermediate
D5-goal
```

The Pygame window also displays the map and drone positions.
Space advances one turn, and Enter toggles automatic playback and pause.

## Resources

The following resources were consulted during implementation. Some are in Japanese.

### Command-Line Argument Parsing

- [A Brief Guide to ArgumentParser (Japanese)](https://qiita.com/kzkadc/items/e4fc7bc9c003de1eb6d0)
- [Python argparse Documentation (Japanese)](https://docs.python.org/ja/3/library/argparse.html)

### Algorithms

- [PyQ: Graph Optimization (Japanese)](https://docs.pyq.jp/python/math_opt/graph)
- [Theory and Practice of DFS and BFS in Python (Japanese)](https://zero2one.jp/learningblog/breadth-first-depth-first-search/?srsltid=AU7gw4UmsaIwrzV8fixIU20hT-osCfaz6tZBSUozQiHoeyNk8h4p-Akn)
- [Greedy Algorithms with Python Examples (Japanese)](https://tech.aru-zakki.com/greedy-algolithm/)
- [An Introduction to Optimization with Python (Japanese)](https://techplay.jp/column/1576)
- [Python heapq Documentation](https://docs.python.org/3/library/heapq.html)

### Visualization

- [An Introduction to Game Development with Pygame (Japanese)](https://qiita.com/nagamie/items/0f7f3e2ea029855a16a1)
- [Pygame Functions, Methods, and Classes (Japanese)](https://programming-mondai.com/top/pygame/yougo/)
- [Pygame Keyboard Documentation](https://www.pygame.org/docs/ref/key.html)

### Use of AI

AI was primarily used to support learning and design in the following areas:

- Understanding graph theory.
- Understanding BFS, DFS, and Dijkstra's algorithm.
- Organizing the object-oriented design.
- Designing parser validation.
- Investigating errors and bugs.
- Understanding the Python standard library.

AI assistance focused on checking the meaning of algorithms and code rather than copying generated output directly.
AI was also used to review the README's structure, compare it with assignment requirements and the implementation, and proofread, revise, and translate the text.
