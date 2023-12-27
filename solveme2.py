from tkinter import *
from tkinter import filedialog
import tkinter.messagebox as tkmb
from PIL import Image, ImageTk
import random
import os
import csv
from pathlib import Path
from queue import Queue, PriorityQueue
import networkx as nx
import time

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
        return self.getTile((gRow, gCol - 1)), self.getTile((gRow - 1, gCol)), self.getTile((gRow, gCol + 1)), self.getTile((gRow + 1, gCol))

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

class Board(Frame):
    MAX_SIZE = 450

    def __init__(self, parent, image, grid, win, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.grid = grid
        self.win = win
        Button(self, text="A* Algorithm", command=lambda: self.solveAStar(), font=("Times New Roman", 12)).grid(row=grid + 1, column=0)
        Button(self, text="Shuffle Puzzle", command=lambda: self.shufflePuzzle(), font=("Times New Roman", 12)).grid(row=grid + 1, column=1)
        self.label = Label(self, text="0 moves", font=("Times New Roman", 20))
        self.label.grid(row=grid + 2, column=0, columnspan=grid)
        self.image = self.openImage(image)
        self.tileSize = self.image.size[0] / self.grid
        self.tiles = self.createTiles()
        self.tiles.shuffle()
        self.tiles.show()

    def shufflePuzzle(self):
        self.tiles.shuffle()
        self.tiles.show()
        movess = "{0} moves".format(self.tiles.moves)
        self.label.config(text=movess)

    def openImage(self, image):
        image = Image.open(image)

        if (image.size[0] > self.MAX_SIZE or image.size[1] > self.MAX_SIZE):
            image = image.resize((self.MAX_SIZE, self.MAX_SIZE), Image.Resampling.LANCZOS)

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
                tileImage = ImageTk.PhotoImage(self.image.crop((x0, y0, x1, y1)))
                if col == self.grid // 2 and row == self.grid // 2:
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
        i = chosenNode.index(str(self.grid * self.grid))
        row, col = i // self.grid, i % self.grid

        if row > 0:
            validMoves.append(i - self.grid)
        if row < self.grid - 1:
            validMoves.append(i + self.grid)
        if col > 0:
            validMoves.append(i - 1)
        if col < self.grid - 1:
            validMoves.append(i + 1)

        return validMoves, i

    def calcCost(self, theStr):
        cost = 0
        goalNode = self.toString(range(1, self.grid * self.grid)) + str(self.grid * self.grid)
        for nom in range(0, len(theStr)):
            if theStr[nom] != goalNode[nom]:
                cost += 1
        return cost

    def solveBest(self):
        tic = time.perf_counter()
        g = nx.Graph()

        rootNode = self.toString(self.tiles.toList())
        goalNode = self.toString(range(1, self.grid * self.grid)) + str(self.grid * self.grid)
        rootCost = self.calcCost(rootNode)

        g.add_node(rootNode)
        parents = {}
        parents[rootNode] = None
        openNodes = PriorityQueue()
        openNodes.put((rootCost, rootNode))
        closedNodes = []
        goal = False

        while goal is False:
            if not openNodes.empty():
                cost, chosenNode = openNodes.get()
                if chosenNode == goalNode:
                    goal = True
                else:
                    validMoves, i = self.possibleMoves(chosenNode)

                    for j in range(0, len(validMoves)):
                        temp = list(chosenNode)
                        temp[i], temp[validMoves[j]] = temp[validMoves[j]], temp[i]
                        tempStr = self.toString(temp)

                        g.add_node(tempStr)
                        g.add_edge(chosenNode, tempStr, length=self.calcCost(tempStr))

                    children = g.neighbors(chosenNode)
                    closedNodes.append(chosenNode)

                    for child in children:
                        if child not in closedNodes and child not in openNodes.queue:
                            cost = self.calcCost(child)
                            parents[child] = chosenNode
                            openNodes.put((cost, child))
            else:
                break

        if goal:
            backtrackPath = []
            currentNode = goalNode
            backtrackPath.append(currentNode)
            stateList = []
            count = 0

            while currentNode is not rootNode:
                currentNode = parents[currentNode]
                backtrackPath.append(currentNode)

            print('\nPuzzle is solved!')
            print('\nSteps to solve:')
            for node in reversed(backtrackPath):
                if node != rootNode:
                    stateList.append(node)
                    count += 1

            toc = time.perf_counter()
            msg = f'Do you want me to solve this puzzle? {count} moves from here. \nIt took {toc - tic:0.4f} seconds to solve!'
            MsgBox = tkmb.askquestion('Solution Found', msg, icon='question')
            if MsgBox == 'yes':
                self.solveIt(stateList)
            else:
                print("Self solve")
        else:
            print('Not solved')

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

            if current_node.state == self.toString(range(1, self.grid * self.grid)) + str(self.grid * self.grid):
                toc = time.perf_counter()
                msg = f'Do you want me to solve this puzzle? {current_node.g} moves from here. \nIt took {toc - tic:0.4f} seconds to solve!'
                MsgBox = tkmb.askquestion('Solution Found', msg, icon='question')
                if MsgBox == 'yes':
                    self.showSolvedPath(current_node)
                return

            closed_nodes.add(current_node.state)

            valid_moves, i = self.possibleMoves(current_node.state)

            for move in valid_moves:
                child_state = self.swapTiles(current_node.state, i, move)
                if child_state not in closed_nodes:
                    child_node = Node(
                        state=child_state,
                        parent=current_node,
                        g=current_node.g + 1,
                        h=self.calculateHeuristic(child_state)
                    )

                    open_nodes.put(child_node)
                    closed_nodes.add(child_state)

    def calculateHeuristic(self, state):
        # Implement your heuristic function here
        # Example: Manhattan distance
        goal_state = self.toString(range(1, self.grid * self.grid)) + str(self.grid * self.grid)
        distance = 0
        for digit in state:
            if digit != '0':
                goal_row, goal_col = self.get_indices(goal_state, digit)
                current_row, current_col = self.get_indices(state, digit)
                distance += abs(goal_row - current_row) + abs(goal_col - current_col)
        return distance

    def get_indices(self, state, digit):
        index = state.index(digit)
        row, col = index // self.grid, index % self.grid
        return row, col

    def swapTiles(self, state, i, j):
        state_list = list(state)
        state_list[i], state_list[j] = state_list[j], state_list[i]
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
            root.update()

class Main():
    def __init__(self,parent):
        self.parent = parent
        self.image = StringVar()
        self.winText = StringVar()
        self.createWidgets()

# Creates the widgets for the starting page, win page and board page
    def createWidgets(self):
        self.mainFrame = Frame(self.parent)
        Label(self.mainFrame, text = 'AI Puzzle Tile', font= ("Montserrat-Regular",40)).pack(padx = 10, pady = 10)
        frame = Frame(self.mainFrame)

        Label(frame, text = 'Image').grid(sticky = W)
        Entry(frame,textvariable = self.image).grid(row=0, column=1, padx = 30, pady = 30)
        Button(frame, text = "Browse", command = self.browse).grid(row=0, column=2, padx = 30, pady = 30)

        frame.pack(padx = 30, pady = 30)
        Button(self.mainFrame, text = "Start", command = self.start,font= ("Arial",15,"bold")).pack(padx = 30, pady = 30)
        self.mainFrame.pack()
        self.board = Frame(self.parent)
        self.winFrame = Frame(self.parent)
        Label(self.winFrame, textvariable = self.winText,font = ('',50)).pack(padx = 30, pady = 30)
        Button(self.winFrame, text = "Play again", command = self.playAgain).pack(padx = 30, pady = 30)

# Start button function, close main and open Board
    def start(self):
        image = self.image.get()
        if os.path.exists(image):
            self.board = Board(self.parent,image,4,self.win)
            self.mainFrame.pack_forget()
            self.board.pack()

# File dialog for image to use on puzzle
    def browse(self):
        self.image.set(filedialog.askopenfilename(title = "Select Image", filetype = (("JPG File","*.jpg"),("PNG File","*.png"))))

# Win state page
    def win(self,moves):
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