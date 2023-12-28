from tkinter import *
from tkinter import filedialog
import tkinter.messagebox as tkmb
from PIL import Image, ImageTk
import random
import os
import csv
from pathlib import Path
from queue import PriorityQueue
import networkx as nx
import time

# ===================================================================================================================================================================================================================
# This is the Tiles class. It is resposible for storing the tiles in a list, and most manupulation that happens, happens here.

class Tiles(Label):
    def __init__(self, grid):
        self.tiles = []
        self.grid = grid
        self.gap = None
        self.moves = 0

    # Tiles into int list
    def toList(self):
        mylys = []
        for tile in self.tiles:
            mylys.append(tile.listNum)
        return mylys

    # This function adds a tile to the list
    def add(self, tile):
        self.tiles.append(tile)

    # Get the tile object at the specific position
    def getTile(self, pos):
        for tile in self.tiles:
            if tile.pos == pos:
                return tile

    # Get the tile objects around the gap. This is the tiles that can be moved.
    def getTileAroundGap(self):
        gRow, gCol = self.gap.pos
        return (
            self.getTile((gRow, gCol - 1)),
            self.getTile((gRow - 1, gCol)),
            self.getTile((gRow, gCol + 1)),
            self.getTile((gRow + 1, gCol)),
        )
        # return self.getTile((gRow, gCol-1)), self.getTile((gRow-1, gCol)), self.getTile((gRow, gCol+1)), self.getTile((gRow+1, gCol))

# Change the gap with the tile that was clicked
    def changeGap(self, tile):
        gPos = self.gap.pos
        self.gap.pos = tile.pos
        tile.pos = gPos
        self.moves += 1
        a, b = self.tiles.index(self.gap), self.tiles.index(tile)
        self.tiles[b], self.tiles[a] = self.tiles[a], self.tiles[b]

# Function that uses the getgetTileAroundGap() function to determin if the move is valid
# Function then use the changeGap() function to switch the tile and the gap (make the move)
    def slide(self, pos):
        left, top, down, right = self.getTileAroundGap()
        currentTile = self.getTile(pos)
        if currentTile == left or currentTile == top or currentTile == down or currentTile == right:
            self.changeGap(currentTile)
        self.show()

    # Set the gap in the puzzle
    def setGap(self, index):
        self.gap = self.tiles[index]
        self.show()

    # Check to see if the tiles are in the correct order
    def isCorrect(self):
        for tile in self.tiles:
            if not tile.isCorrectPos():
                return False
        return True

    # Shuffle the tiles
    def shuffle(self):
        random.shuffle(self.tiles)
        i = 0
        for row in range(self.grid):
            for col in range(self.grid):
                self.tiles[i].pos = (row, col)
                i += 1
        if not self.isSolvable(self.toList()):
            self.shuffle()

# Change the state of the puzzle
    def importState(self, stateList):
        i = 0
        j = 0
        self.moves += 1
        tempAr = []
        for row in range(self.grid):
            for col in range(self.grid):
                j = 0
                for tile in self.tiles:
                    if tile.listNum == int(stateList[i]):
                        self.tiles[j].pos = (row, col)
                        tempAr.append(self.tiles[j])
                    j += 1
                i += 1
        self.tiles = tempAr
        self.show()

# Def to show the tiles, excluding the gap
    def show(self):
        for tile in self.tiles:
            if self.gap != tile:
                tile.show()

# Get inversion count
    def getInvCount(self, arr):
        tmp = arr.index(self.grid * self.grid)
        arr[tmp] = 0
        inv_count = 0
        for i in range(self.grid * self.grid - 1):
            for j in range(i + 1, self.grid * self.grid):
                if arr[j] and arr[i] and arr[i] > arr[j]:
                    inv_count += 1
        return inv_count

# Check if puzzle is solvable
    def isSolvable(self, arr):
        inversionCount = self.getInvCount(arr)
        print(arr)
        print(inversionCount)
        return (inversionCount % 2 == 0)


# ====================================================================================================================================================================================================================
# This is the Tile class. It is responsible to show the picture on the puzzle. The picture are devided into 9 Tiles.

class Tile(Label):
    def __init__(self, parent, image, pos, listNum):
        Label.__init__(self, parent, image=image)
        self.bind("<Button-1>", self.click)
        # Save reference to parent
        self.parent = parent
        self.image = image
        self.pos = pos
        # Original Position (1,2,3,4,5,6,7,8,9)
        self.ogPos = pos
        self.listNum = listNum

# Click detection, then calls slideIt() function from the Board class
    def click(self, event):
        # Call method on parent
        self.parent.slideIt(self.pos)

# Function to show the tile in the grid
    def show(self):
        self.grid(row=self.pos[0], column=self.pos[1])

# Check if the tile is in the correct position. It compares the
    def isCorrectPos(self):
        return self.pos == self.ogPos


# ===================================================================================================================================================================================================================
# Board class. The tiles are shown on a grid on the board. This is the parent class.
class Node:
    def __init__(self, state, parent=None, g=0, h=0):
        self.state = state
        self.parent = parent
        self.g = g  # Cost from the start node to this node
        self.h = h  # Heuristic cost from this node to the goal
        self.f = g + h  # Total cost (f = g + h)

    def __lt__(self, other):
        return self.f < other.f


class Board(Frame):
    MAX_SIZE = 450

    def __init__(self, parent, image, grid, win, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.grid = grid
        self.win = win
        
        Button(
            self,
            text="A* Algorithm",
            command=lambda: self.solveAStar(),
            font=("Times New Roman", 12),
        ).grid(row=6, column=1)  # Adjusted button position
        
        self.label = Label(
            self, text="0 moves", font=("Times New Roman", 20)
        )
        self.label.grid(row=7, column=1)  # Adjusted label position
        self.image = self.openImage(image)
        self.tileSize = self.image.size[0] / self.grid
        self.tiles = self.createTiles()
        self.tiles.shuffle()
        self.tiles.show()

# Function to open a CSV file
    def openCSV(self):
        script_location = Path(__file__).absolute().parent
        file_location = script_location / 'Solusi.csv'
        with open(file_location, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            next(csv_reader)

            for line in csv_reader:
                stateList = line

            self.tiles.importState(stateList)
            self.tiles.show()
            movess = "{0} moves".format(self.tiles.moves)
            self.label.config(text=movess)

# Function to open and crop the image to fit into a sqaure
    def openImage(self, image):
        image = Image.open(image)

        if (image.size[0] > 450 or image.size[1] > 450):
            image = image.resize(
                (self.MAX_SIZE, self.MAX_SIZE), Image.Resampling.LANCZOS)

        if image.size[0] != image.size[1]:
            image = image.crop((0, 0, image.size[0], image.size[0]))
        return image

# Function called when clicked on a tile.  Update the moves and calls the slide function from Tiles. Also checks if goal state is reached.
    def slideIt(self, pos):
        self.tiles.slide(pos)
        movess = "{0} moves".format(self.tiles.moves)
        self.label.config(text=movess)
        if self.tiles.isCorrect():
            self.win(self.tiles.moves)

# Creates the tiles and the gap. Automatically crops the image into 9 pieces
    def createTiles(self):
        tiles = Tiles(self.grid)
        i = 1
        for row in range(self.grid):
            for col in range(self.grid):
                x0 = col*self.tileSize
                y0 = row*self.tileSize
                x1 = x0+self.tileSize
                y1 = y0+self.tileSize
                tileImage = ImageTk.PhotoImage(
                    self.image.crop((x0, y0, x1, y1)))
                if col == 2 and row == 2:
                    tile = Tile(self, None, (row, col), i)
                    tiles.add(tile)
                    tiles.setGap(-1)
                    tiles.show()
                else:
                    tile = Tile(self, tileImage, (row, col), i)
                    tiles.add(tile)
                    tiles.show()
                i += 1
        return tiles

    # Converts list to string for BFS
    def toString(self, lys):
        myString = ''
        for item in lys:
            temp = str(item)
            myString += temp
        return myString

    # Show how search solve
    def solveIt(self, statelist):
        for state in statelist:
            self.tiles.importState((list(state)))
            self.tiles.show()
            movess = "{0} moves".format(self.tiles.moves)
            self.label.config(text=movess)
            time.sleep(1)
            root.update()
        time.sleep(2)
        if self.tiles.isCorrect():
            self.win(self.tiles.moves)


    # Checks for possible moves for search function
    def possibleMoves(self, chosenNode):
        validMoves = []
        i = chosenNode.index('9')
        if i == 0:
            validMoves.extend([1, 3])
        elif i == 1:
            validMoves.extend([0, 2, 4])
        elif i == 2:
            validMoves.extend([1, 5])
        elif i == 3:
            validMoves.extend([0, 4, 6])
        elif i == 4:
            validMoves.extend([1, 3, 5, 7])
        elif i == 5:
            validMoves.extend([2, 4, 8])
        elif i == 6:
            validMoves.extend([3, 7])
        elif i == 7:
            validMoves.extend([4, 6, 8])
        elif i == 8:
            validMoves.extend([5, 7])

        return validMoves, i


    def calcCost(self, theStr):
        cost = 0
        goalNode = '12345678910111213141516171819202122232425'  # Adjust this for your specific goal state

        for a, b in zip(theStr, goalNode):
            if a != b:
                cost += 1

        return cost

    def getNode(self, current_node):
        validMoves, i = self.possibleMoves(current_node.state)
        neighbors = []

        for move in validMoves:
            new_state = self.swapTiles(current_node.state, i, move)
            new_node = Node(new_state, parent=current_node, g=current_node.g + 1, h=self.calculateHeuristic(new_state))
            neighbors.append(new_node)

        return neighbors
    
    def solveAStar(self):
        tic = time.perf_counter()

        # Create the initial node
        initial_state = self.toString(self.tiles.toList())
        initial_node = Node(initial_state, g=0, h=self.calculateHeuristic(initial_state))
        open_nodes = PriorityQueue()
        open_nodes.put(initial_node)
        closed_nodes = set()

        while not open_nodes.empty():
            current_node = open_nodes.get()

            if current_node.state == '12345678910111213141516171819202122232425':
                # Goal state reached
                toc = time.perf_counter()
                msg = f'Do you want me to solve this puzzle? {current_node.g} moves from here. \nIt took {toc - tic:0.4f} seconds to solve!'
                MsgBox = tkmb.askquestion('Solution Found', msg, icon='question')
                if MsgBox == 'yes':
                    self.showSolvedPath(current_node)
                return

            closed_nodes.add(current_node.state)

            # Get neighboring nodes
            neighbor_nodes = self.getNode(current_node)

            for neighbor_node in neighbor_nodes:
                if neighbor_node.state not in closed_nodes:
                    open_nodes.put(neighbor_node)
                    closed_nodes.add(neighbor_node.state)

            # Add print statements to check the state of the puzzle
            print(f'Moves: {current_node.g}, State: {current_node.state}')
            self.tiles.importState(list(current_node.state))
            self.tiles.show()
            movess = "{0} moves".format(current_node.g)
            self.label.config(text=movess)
            root.update_idletasks()
            time.sleep(1)

        print("No solution found!")

    def calculateHeuristic(self, state):
        goal_state = '12345678910111213141516171819202122232425'  # Adjust this for your specific goal state

        size = int(self.grid)

        h = 0
        for i in range(size * size):
            value_to_find = str(i + 1)
            if value_to_find in state:
                current_row, current_col = divmod(state.index(value_to_find), size)
                goal_row, goal_col = divmod(goal_state.index(value_to_find), size)
                h += abs(current_row - goal_row) + abs(current_col - goal_col)

        return h

    def swapTiles(self, state, i, j):
        # Helper function to swap tiles in a given state
        value_i = str(i + 1)
        value_j = str(j + 1)

        if value_i not in state or value_j not in state:
            # Handle the case where substrings are not found
            return state

        state_list = list(state)
        index_i = state_list.index(value_i)
        index_j = state_list.index(value_j)

        state_list[index_i], state_list[index_j] = state_list[index_j], state_list[index_i]
        return ''.join(state_list)

    def showSolvedPath(self, final_node):
        # Display the solved path on the GUI
        path = []
        current_node = final_node
        while current_node is not None:
            path.append(current_node.state)
            current_node = current_node.parent

        for state in reversed(path):
            self.tiles.importState(list(state))
            self.tiles.show()
            movess = "{0} moves".format(self.tiles.moves)
            self.label.config(text=movess)

            # Adjust sleep duration or use update_idletasks
            time.sleep(1)
            root.update_idletasks()

# ===================================================================================================================================================================================================================
# Main class. This is the main menu where you choose the image and start the game.

class Main():
    def __init__(self, parent):
        self.parent = parent
        self.image = StringVar()
        self.winText = StringVar()
        self.createWidgets()

# Creates the widgets for the starting page, win page and board page
    def createWidgets(self):
        self.mainFrame = Frame(self.parent)
        Label(self.mainFrame, text='AI Puzzle Tile', font=(
            "Montserrat-Regular", 40)).pack(padx=10, pady=10)
        frame = Frame(self.mainFrame)

        Label(frame, text='Image').grid(sticky=W)
        Entry(frame, textvariable=self.image).grid(
            row=0, column=1, padx=30, pady=30)
        Button(frame, text="Browse", command=self.browse).grid(
            row=0, column=2, padx=30, pady=30)

        frame.pack(padx=30, pady=30)
        Button(self.mainFrame, text="Start", command=self.start,
               font=("Arial", 15, "bold")).pack(padx=30, pady=30)
        self.mainFrame.pack()
        self.board = Frame(self.parent)
        self.winFrame = Frame(self.parent)
        Label(self.winFrame, textvariable=self.winText,
              font=('', 50)).pack(padx=30, pady=30)
        Button(self.winFrame, text="Play again",
               command=self.playAgain).pack(padx=30, pady=30)

    # Start button function, close main and open Board
    def start(self):
        image = self.image.get()
        if os.path.exists(image):
            self.board = Board(self.parent, image, 5, self.win)
            self.mainFrame.pack_forget()
            self.board.pack()

    # File dialog for image to use on puzzle
    def browse(self):
        self.image.set(filedialog.askopenfilename(
            title="Select Image", filetype=(("JPG File", "*.jpg"), ("PNG File", "*.png"))))

    # Win state page
    def win(self, moves):
        self.board.pack_forget()
        self.winText.set("You WON! You made {0} moves".format(moves))
        self.winFrame.pack()

    # Play again button's method
    def playAgain(self):
        self.winFrame.pack_forget()
        self.mainFrame.pack()


# Set the app root to main page
if __name__ == "__main__":
    root = Tk()
    Main(root)
    root.mainloop()