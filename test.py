from PIL import Image
import heapq

class PuzzleNode:
    def __init__(self, state, parent=None, move=None, cost=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.cost = cost
        self.heuristic = self.calculate_heuristic()

    def calculate_heuristic(self):
        # You need to implement your own heuristic function.
        # This can involve calculating the Manhattan distance, Euclidean distance, or any other suitable metric.
        # For simplicity, let's use the Manhattan distance as an example.
        goal_state = [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14], [15, 16, 17, 18, 19], [20, 21, 22, 23, 24]]
        heuristic = 0
        for i in range(5):
            for j in range(5):
                value = self.state[i][j]
                goal_position = divmod(value, 5)
                heuristic += abs(i - goal_position[0]) + abs(j - goal_position[1])
        return heuristic

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

def get_neighbors(node):
    neighbors = []
    empty_pos = [(i, j) for i in range(5) for j in range(5) if node.state[i][j] == 0][0]
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for move in moves:
        new_pos = (empty_pos[0] + move[0], empty_pos[1] + move[1])
        if 0 <= new_pos[0] < 5 and 0 <= new_pos[1] < 5:
            new_state = [row.copy() for row in node.state]
            new_state[empty_pos[0]][empty_pos[1]] = node.state[new_pos[0]][new_pos[1]]
            new_state[new_pos[0]][new_pos[1]] = 0
            neighbors.append(PuzzleNode(new_state, node, move, node.cost + 1))
    
    return neighbors

def a_star(initial_state):
    start_node = PuzzleNode(initial_state)
    open_set = [start_node]
    closed_set = set()

    while open_set:
        current_node = heapq.heappop(open_set)

        if current_node.state == [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14], [15, 16, 17, 18, 19], [20, 21, 22, 23, 24]]:
            path = []
            while current_node:
                path.insert(0, current_node.move)
                current_node = current_node.parent
            return path

        closed_set.add(tuple(map(tuple, current_node.state)))

        neighbors = get_neighbors(current_node)
        for neighbor in neighbors:
            if tuple(map(tuple, neighbor.state)) not in closed_set:
                heapq.heappush(open_set, neighbor)

    return None  # No solution found

def display_solution(initial_state, solution):
    current_state = initial_state
    print("Initial State:")
    print_state(current_state)

    for move in solution:
        current_state = make_move(current_state, move)
        print(f"\nMove: {move}")
        print_state(current_state)

def make_move(state, move):
    empty_pos = [(i, j) for i in range(5) for j in range(5) if state[i][j] == 0][0]
    new_pos = (empty_pos[0] - move[0], empty_pos[1] - move[1])
    state[empty_pos[0]][empty_pos[1]] = state[new_pos[0]][new_pos[1]]
    state[new_pos[0]][new_pos[1]] = 0
    return state

def print_state(state):
    for row in state:
        print(row)
    print()

def main():
    # Load the image and convert it to a 5x5 puzzle
    image_path = "gambar.png"
    image = Image.open(image_path)
    image = image.resize((5, 5))
    initial_state = [[i + j * 5 for i in range(5)] for j in range(5)]

    solution = a_star(initial_state)

    if solution:
        display_solution(initial_state, solution)
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
