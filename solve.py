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
# This is the Tiles class. It is responsible for storing the tiles in a list, and most manipulations that happen, happen here.


class Tiles(Label):
    def __init__(self, grid):
        self.tiles = []
        self.grid = grid
        self.gap = None
        self.moves = 0

    def toList(self):
        mylys = []
        for tile in self.tiles:
            mylys.append(tile.listNum)
        return mylys

    def add(self, tile):
        self.tiles.append(tile)

    def getTile(self, pos):
        for tile in self.tiles:
            if tile.pos == pos:
                return tile

    def getTileAroundGap(self):
        gRow, gCol = self.gap.pos
        return (
            self.getTile((gRow, gCol - 1)),
            self.getTile((gRow - 1, gCol)),
            self.getTile((gRow, gCol + 1)),
            self.getTile((gRow + 1, gCol)),
        )

    def changeGap(self, tile):
        gPos = self.gap.pos
        self.gap.pos = tile.pos
        tile.pos = gPos
        self.moves += 1
        a, b = self.tiles.index(self.gap), self.tiles.index(tile)
        self.tiles[b], self.tiles[a] = self.tiles[a], self.tiles[b]

    def slide(self, pos):
        left, top, down, right = self.getTileAroundGap()
        currentTile = self.getTile(pos)
        if currentTile == left or currentTile == top or currentTile == down or currentTile == right:
            self.changeGap(currentTile)
        self.show()

    def setGap(self, index):
        self.gap = self.tiles[index]
        self.show()

    def isCorrect(self):
        for tile in self.tiles:
            if not tile.isCorrectPos():
                return False
        return True

    def shuffle(self):
        random.shuffle(self.tiles)
        i = 0
        for row in range(self.grid):
            for col in range(self.grid):
                self.tiles[i].pos = (row, col)
                i += 1
        if not self.isSolvable(self.toList()):
            self.shuffle()

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

    def show(self):
        for tile in self.tiles:
            if self.gap != tile:
                tile.show()

    def getInvCount(self, arr):
        tmp = arr.index(self.grid * self.grid)
        arr[tmp] = 0
        inv_count = 0
        for i in range(self.grid * self.grid - 1):
            for j in range(i + 1, self.grid * self.grid):
                if arr[j] and arr[i] and arr[i] > arr[j]:
                    inv_count += 1
        return inv_count

    def isSolvable(self, arr):
        inversionCount = self.getInvCount(arr)
        return (inversionCount % 2 == 0)


# ====================================================================================================================================================================================================================
# This is the Tile class. It is responsible to show the picture on the puzzle. The picture is divided into 9 Tiles.


class Tile(Label):
    def __init__(self, parent, image, pos, listNum):
        Label.__init__(self, parent, image=image)
        self.bind("<Button-1>", self.click)
        self.parent = parent
        self.image = image
        self.pos = pos
        self.ogPos = pos
        self.listNum = listNum

    def click(self, event):
        self.parent.slideIt(self.pos)

    def show(self):
        self.grid(row=self.pos[0], column=self.pos[1])

    def isCorrectPos(self):
        return self.pos == self.ogPos


# ===================================================================================================================================================================================================================
# Board class. The tiles are shown on a grid on the board. This is the parent class.


class Node:
    def __init__(self, state, parent=None, g=0, h=0):
        self.state = state
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        return self.f < other.f


class Board(Frame):
    MAX_SIZE = 500

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
        ).grid(row=6, column=1)

        self.label = Label(
            self, text="0 moves", font=("Times New Roman", 20)
        )
        self.label.grid(row=7, column=1)
        self.image = self.openImage(image)
        self.tileSize = self.image.size[0] / self.grid
        self.tiles = self.createTiles()
        self.tiles.shuffle()
        self.tiles.show()

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

    def openImage(self, image):
        image = Image.open(image)
        if (image.size[0] > 500 or image.size[1] > 500):
            image = image.resize(
                (self.MAX_SIZE, self.MAX_SIZE), Image.Resampling.LANCZOS)

        if image.size[0] != image.size[1]:
            image = image.crop((0, 0, image.size[0], image.size[0]))
        return image

    def slideIt(self, pos):
        self.tiles.slide(pos)
        movess = "{0} moves".format(self.tiles.moves)
        self.label.config(text=movess)
        if self.tiles.isCorrect():
            self.win(self.tiles.moves)

    def createTiles(self):
        tiles = Tiles(self.grid)
        i = 1
        for row in range(self.grid):
            for col in range(self.grid):
                x0 = col * self.tileSize
                y0 = row * self.tileSize
                x1 = x0 + self.tileSize
                y1 = y0 + self.tileSize
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

    def toString(self, lys):
        myString = ''
        for item in lys:
            temp = str(item)
            myString += temp
        return myString

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

    def possibleMoves(self, chosenNode):
        validMoves = []
        i = chosenNode.index('25')

        if i == 0:
            validMoves.extend([1, 5])
        elif i == 1:
            validMoves.extend([0, 2, 6])
        elif i == 2:
            validMoves.extend([1, 3, 7])
        elif i == 3:
            validMoves.extend([2, 4, 8])
        elif i == 4:
            validMoves.extend([3, 9])
        elif i == 5:
            validMoves.extend([0, 6, 10])
        elif i == 6:
            validMoves.extend([1, 5, 7, 11])
        elif i == 7:
            validMoves.extend([2, 6, 8, 12])
        elif i == 8:
            validMoves.extend([3, 7, 9, 13])
        elif i == 9:
            validMoves.extend([4, 8, 14])
        elif i == 10:
            validMoves.extend([5, 11, 15])
        elif i == 11:
            validMoves.extend([6, 10, 12, 16])
        elif i == 12:
            validMoves.extend([7, 11, 13, 17])
        elif i == 13:
            validMoves.extend([8, 12, 14, 18])
        elif i == 14:
            validMoves.extend([9, 13, 19])
        elif i == 15:
            validMoves.extend([10, 16, 20])
        elif i == 16:
            validMoves.extend([11, 15, 17, 21])
        elif i == 17:
            validMoves.extend([12, 16, 18, 22])
        elif i == 18:
            validMoves.extend([13, 17, 19, 23])
        elif i == 19:
            validMoves.extend([14, 18, 24])
        elif i == 20:
            validMoves.extend([15, 21])
        elif i == 21:
            validMoves.extend([16, 20, 22])
        elif i == 22:
            validMoves.extend([17, 21, 23])
        elif i == 23:
            validMoves.extend([18, 22, 24])
        elif i == 24:
            validMoves.extend([19, 23])

        return validMoves, i

    def calcCost(self, theStr):
        cost = 0
        goalNode = '12345678910111213141516171819202122232425'

        for a, b in zip(theStr, goalNode):
            if a != b:
                cost += 1

        return cost

    def getNode(self, current_node):
        validMoves, i = self.possibleMoves(current_node.state)
        neighbors = []

        for move in validMoves:
            new_state = self.swapTiles(
                current_node.state, i, move)
            new_node = Node(
                new_state, parent=current_node, g=current_node.g + 1, h=self.calculateHeuristic(new_state))
            neighbors.append(new_node)

        return neighbors

    def solveAStar(self):
        tic = time.perf_counter()

        initial_state = self.toString(self.tiles.toList())
        initial_node = Node(initial_state, g=0,
                            h=self.calculateHeuristic(initial_state))
        open_nodes = PriorityQueue()
        open_nodes.put(initial_node)
        closed_nodes = set()

        while not open_nodes.empty():
            current_node = open_nodes.get()

            if current_node.state == '12345678910111213141516171819202122232425':
                toc = time.perf_counter()
                msg = f'Do you want me to solve this puzzle? {current_node.g} moves from here. \nIt took {toc - tic:0.4f} seconds to solve!'
                MsgBox = tkmb.askquestion(
                    'Solution Found', msg, icon='question')
                if MsgBox == 'yes':
                    self.showSolvedPath(current_node)
                return

            closed_nodes.add(current_node.state)

            neighbor_nodes = self.getNode(current_node)

            for neighbor_node in neighbor_nodes:
                if neighbor_node.state not in closed_nodes:
                    open_nodes.put(neighbor_node)
                    closed_nodes.add(neighbor_node.state)

            print(f'Moves: {current_node.g}, State: {current_node.state}')
            self.tiles.importState(list(current_node.state))
            self.tiles.show()
            movess = "{0} moves".format(current_node.g)
            self.label.config(text=movess)
            root.update_idletasks()
            time.sleep(1)

    def calculateHeuristic(self, state):
        goal_state = '12345678910111213141516171819202122232425'

        size = int(self.grid)

        h = 0
        for i in range(size * size):
            value_to_find = str(i + 1)
            if value_to_find in state:
                current_row, current_col = divmod(
                    state.index(value_to_find), size)
                goal_row, goal_col = divmod(
                    goal_state.index(value_to_find), size)
                h += abs(current_row - goal_row) + abs(current_col - goal_col)

        return h

    def swapTiles(self, state, i, j):
        value_i = str(i + 1)
        value_j = str(j + 1)

        if value_i not in state or value_j not in state:
            return state

        state_list = list(state)
        index_i = state_list.index(value_i)
        index_j = state_list.index(value_j)

        state_list[index_i], state_list[index_j] = state_list[index_j], state_list[index_i]
        return ''.join(state_list)

    def showSolvedPath(self, final_node):
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
            time.sleep(1)
            root.update_idletasks()


class Main():
    def __init__(self, parent):
        self.parent = parent
        self.image = StringVar()
        self.winText = StringVar()
        self.createWidgets()

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
