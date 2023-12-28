import heapq
import copy

class PuzzleState:
    def __init__(self, puzzle, cost=0, heuristic=0):
        self.puzzle = puzzle
        self.cost = cost
        self.heuristic = heuristic

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

def calculate_heuristic(puzzle):
    # Example heuristic: Manhattan distance
    total_distance = 0
    for i in range(5):
        for j in range(5):
            if puzzle[i][j] != 0:
                target_row = (puzzle[i][j] - 1) // 5
                target_col = (puzzle[i][j] - 1) % 5
                total_distance += abs(i - target_row) + abs(j - target_col)
    return total_distance

def get_neighbors(state):
    neighbors = []
    zero_row, zero_col = None, None
    for i in range(5):
        for j in range(5):
            if state.puzzle[i][j] == 0:
                zero_row, zero_col = i, j
                break

    moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for move in moves:
        new_row, new_col = zero_row + move[0], zero_col + move[1]
        if 0 <= new_row < 5 and 0 <= new_col < 5:
            new_puzzle = copy.deepcopy(state.puzzle)
            new_puzzle[zero_row][zero_col], new_puzzle[new_row][new_col] = (
                new_puzzle[new_row][new_col],
                new_puzzle[zero_row][zero_col],
            )
            neighbors.append(
                PuzzleState(
                    new_puzzle,
                    cost=state.cost + 1,
                    heuristic=calculate_heuristic(new_puzzle),
                )
            )

    return neighbors

def a_star_solver(initial_state):
    priority_queue = [initial_state]
    visited = set()

    while priority_queue:
        current_state = heapq.heappop(priority_queue)

        if current_state.puzzle == goal_state:
            return current_state.puzzle

        if tuple(map(tuple, current_state.puzzle)) in visited:
            continue

        visited.add(tuple(map(tuple, current_state.puzzle)))

        neighbors = get_neighbors(current_state)
        for neighbor in neighbors:
            if tuple(map(tuple, neighbor.puzzle)) not in visited:
                heapq.heappush(priority_queue, neighbor)

    return None

# Example initial and goal states
initial_state = [
    [1, 2, 3, 4, 0],
    [6, 7, 8, 5, 10],
    [11, 12, 13, 9, 15],
    [16, 17, 18, 14, 20],
    [21, 22, 23, 19, 24],
]

goal_state = [
    [1, 2, 3, 4, 5],
    [6, 7, 8, 9, 10],
    [11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20],
    [21, 22, 23, 24, 0],
]

initial_state = PuzzleState(initial_state, heuristic=calculate_heuristic(initial_state))

solution = a_star_solver(initial_state)

if solution:
    print("Solution found:")
    for row in solution:
        print(row)
else:
    print("No solution found.")
