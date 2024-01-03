import time
import tkinter as tk
from queue import PriorityQueue
from math import inf
from tkinter import *
import random
from PIL import Image, ImageTk
import pygame

def isSolvable(seq):

        seq = list(seq) 
        N = int(len(seq) ** 0.5)
        def countInv(seq):
            numinv = 0
            for i in range(0,N**2,1):
                for j in range(i+1,N**2,1):
                    if seq[i] != N**2 and seq[j] != N**2 and seq[i] > seq[j]:
                        numinv += 1
            return numinv

        def blankRow(seq):
            return N - ((seq.index(N**2)) // N)

        numinv = countInv(seq)

        if N & 1:
            return bool(not numinv & 1)
        else:
            pos = blankRow(seq)
            if pos & 1:
                return bool(not numinv & 1)
            else:
                return bool(numinv & 1)

def manhattan(seq):
    result = 0
    dim = int(len(seq)**0.5)
    ref = [[x + i*dim for x in range(1,dim+1)] for i in range(dim)]
    seq2 = to2D(seq)
    for i in range(dim):
        for j in range (dim):
            if (ref[i][j] == dim**2):
                continue
            for l in range(dim):
                for m in range(dim):
                    if (ref[i][j] == seq2[l][m]):
                        result += (abs(m - j) + abs(l - i))
                        break
    return result

def encode_cfg(cfg, n):
    r = 0
    b = n.bit_length()
    for i in range(len(cfg)):
        r |= cfg[i] << (b*i)
    return r
 
def gen_wd_table(n):
    goal = [[0] * i + [n] + [0] * (n - 1 - i) for i in range(n)]
    goal[-1][-1] = n - 1
    goal = tuple(sum(goal, []))
 
    table = {}
    to_visit = [(goal, 0, n-1)]
    while to_visit:
        cfg, cost, e = to_visit.pop(0)
        enccfg = encode_cfg(cfg, n)
        if enccfg in table: continue
        table[enccfg] = cost
 
        for d in [-1, 1]:
            if 0 <= e + d < n:
                for c in range(n):
                    if cfg[n*(e+d) + c] > 0:
                        ncfg = list(cfg)
                        ncfg[n*(e+d) + c] -= 1
                        ncfg[n*e + c] += 1
                        to_visit.append((tuple(ncfg), cost + 1, e+d))
 
    return table
 
def slide_wd(n, goal):
    wd = gen_wd_table(n)
    goals = {i : goal.index(i) for i in goal}
    b = n.bit_length()
    def replace_with_0(p):
        tmp = list(p)
        idnsq = tmp.index(n*n)
        tmp[idnsq] = 0
        return tuple(tmp)
    def h(p):
        p = replace_with_0(p)
        ht = 0
        vt = 0
        d = 0
        for i, c in enumerate(p):
            if c == 0: continue
            g = goals[c]
            xi, yi = i % n, i // n
            xg, yg = g % n, g // n
            ht += 1 << (b*(n*yi+yg))
            vt += 1 << (b*(n*xi+xg))
 
            if yg == yi:
                for k in range(i + 1, i - i%n + n): # Until end of row.
                    if p[k] and goals[p[k]] // n == yi and goals[p[k]] < g:
                        d += 2
 
            if xg == xi:
                for k in range(i + n, n * n, n): # Until end of column.
                    if p[k] and goals[p[k]] % n == xi and goals[p[k]] < g:
                        d += 2
 
        d += wd[ht] + wd[vt]
 
        return d
    return h

def to2D(seq):
    N = int(len(seq)**0.5)
    tmp = []
    for i in range(N):
        tmp.append(seq[N*i:N*(i+1)])
    return tmp

def posibleMoves(seq):
    seq = list(seq)
    Nsq = len(seq)
    N = int(Nsq**0.5)
    empty_loc = seq.index(Nsq)
    row = empty_loc // N
    col = empty_loc % N
    
    def up():
        tmp = seq.copy()
        if row == 0:
            return tmp
        else:
            swap_pos = (row - 1) * N + col
            tmp[swap_pos], tmp[empty_loc] = tmp[empty_loc], tmp[swap_pos]
            return tmp

    def down():
        tmp = seq.copy()
        if row == (N - 1):
            return tmp
        else:
            swap_pos = (row + 1) * N + col
            tmp[swap_pos], tmp[empty_loc] = tmp[empty_loc], tmp[swap_pos]
            return tmp

    def left():
        tmp = seq.copy()
        if col == 0:
            return tmp
        else:
            swap_pos = (row * N) + (col - 1)
            tmp[swap_pos], tmp[empty_loc] = tmp[empty_loc], tmp[swap_pos]
            return tmp
    
    def right():
        tmp = seq.copy()
        if col == (N - 1):
            return tmp
        else:
            swap_pos = (row * N) + (col + 1)
            tmp[swap_pos], tmp[empty_loc] = tmp[empty_loc], tmp[swap_pos]
            return tmp

    moves = set()
    if up() != seq:
        moves.add(tuple(up()))
    if down() != seq:
        moves.add(tuple(down()))
    if left() != seq:
        moves.add(tuple(left()))
    if right() != seq:
        moves.add(tuple(right()))
    return list(moves)

def getPath(node):
    path = []
    path.append(node.board)
    while (node.parent is not None):
        node = node.parent
        path.append(node.board)
    return path[::-1]

def path_as_udlr(solution):
    Nsq = len(solution[0])
    n = int(Nsq ** 0.5)
    move_path = ""
    for i in range(len(solution)):
        if i == 0 : continue
        before = solution[i-1].index(Nsq)
        x = before // n
        y = before % n
        after = solution[i].index(Nsq)
        i = after // n
        j = after % n
        if x == i:
            pass
        elif x > i:
            move_path += "u"
            continue
        else:
            move_path += "d"
            continue
        if y == j:
            pass
        elif y > j:
            move_path += "l"
            continue
        else:
            move_path += "r"
            continue
    return move_path

def game_init(heuristic_name,stboard):
    n = int(len(stboard)**0.5)
    goal_board = tuple(i % (n*n) for i in range(1, n*n+1))
    end_board = tuple(x for x in range(1,n*n +1))
    if heuristic_name == "manhattan":
        heuristic = manhattan
    if heuristic_name == "walking_distance":
        heuristic = slide_wd(n,goal_board)   
    g = 0
    h = heuristic(stboard)
    f = g + h
    start = Node(stboard,None,g,h,f)
    goal = Node(end_board,None,0,0,0)
    return start,goal,heuristic

def AStarSearch(heuristic_name,board):
    start,goal,heuristic = game_init(heuristic_name,board)
    openset = PriorityQueue()
    closedset = {}
    openset.put(start)
    positions_seen = 0

    while not openset.empty():
        current = openset.get()
        closedset[current.board] = (current.g, current.h, current.f)
        positions_seen += 1
        if current == goal:
            return getPath(current),positions_seen
        for move in posibleMoves(current.board):
            newg = current.g + 1
            h = heuristic(move)
            f = newg + h
            if move in closedset:
                if newg < closedset[move][0]:
                    node = Node(move,current,newg,h,f)
                    openset.put(node)
                    del closedset[move]
                    continue
                else:
                    continue
            node = Node(move,current,newg,h,f)
            openset.put(node)
            
        if positions_seen % 100000 == 0:
            print("{} positions analyzed...".format(positions_seen))
        if positions_seen > 20000000:
            break
    return [],0

def AStarSearchWithGUI(board_size, solving_algorithm, heuristic_name, gui_board):
    start, goal, heuristic = game_init(heuristic_name, gui_board.board)
    openset = PriorityQueue()
    closedset = {}
    openset.put(start)
    positions_seen = 0

    while not openset.empty():
        current = openset.get()
        closedset[current.board] = (current.g, current.h, current.f)
        positions_seen += 1
        if current == goal:
            solution_path = getPath(current)
            gui_board.animate_solution(solution_path)
            return solution_path, positions_seen
        for move in posibleMoves(current.board):
            newg = current.g + 1
            h = heuristic(move)
            f = newg + h
            if move in closedset:
                if newg < closedset[move][0]:
                    node = Node(move, current, newg, h, f)
                    openset.put(node)
                    del closedset[move]
                    continue
                else:
                    continue
            node = Node(move, current, newg, h, f)
            openset.put(node)

        if positions_seen % 100000 == 0:
            print("{} positions analyzed...".format(positions_seen))
        if positions_seen > 20000000:
            break
    return [], 0

def IDAStar(heuristic_name,board):
    
    def search(path, is_in_path, g, threshold, num_positions_evaluated):
        num_positions_evaluated += 1
        current = path[-1]
        if num_positions_evaluated % 100000 == 0:
            print("{} positions analyzed...".format(num_positions_evaluated))
        newf = g + heuristic(current)
        if newf > threshold:
            return newf,num_positions_evaluated
        if current == goal:
            return FOUND,num_positions_evaluated
        minimum = inf
        for move in posibleMoves(current):
            if move in is_in_path:
                continue
            path.append(move)
            is_in_path.add(move)
            t,num_positions_evaluated = search(path, is_in_path, g+1, threshold, num_positions_evaluated)
            if t == FOUND:return FOUND,num_positions_evaluated
            if t < minimum:minimum = t
            path.pop()
            in_path.remove(move)
        return minimum,num_positions_evaluated

    start,goaln,heuristic = game_init(heuristic_name,board)
    goal = goaln.board
    num_positions_evaluated = 0
    threshold = heuristic(board)
    path = [board]
    in_path = set()
    FOUND = object()
    while True:
        t, num_positions_evaluated = search(path, in_path, 0, threshold, num_positions_evaluated)
        if t == FOUND:
            return path,num_positions_evaluated
        elif t is inf:
            return [], num_positions_evaluated
        else:
            threshold = t

def Solve(heuristic_name_short,algorithm_name, board):
    if not isSolvable(board):
        print("Bad board. not solvable")
        return -1
    if heuristic_name_short == "WD":
        heuristic_name = "walking_distance"
    else:
        heuristic_name = "manhattan"
    before = time.perf_counter()
    if algorithm_name == "A*":
        soln,numpos = AStarSearch(heuristic_name,board)
    elif algorithm_name == "IDA*":
        soln,numpos = IDAStar(heuristic_name,board)
    else:
        print("No valid solving algorithm")
        return -1
    after = time.perf_counter()
    moves_to_solve = list(path_as_udlr(soln))

    return (board,len(soln)-1,str(round(after - before,3)),numpos,heuristic_name,algorithm_name,moves_to_solve,soln)

class Node:
    def __init__(self,board,parent,g,h,f):
        self.board = tuple(board)
        self.parent = parent
        self.g = g
        self.h = h
        self.f = f

    def __lt__(self,other):
        return self.f < other.f

    def __eq__(self,other):
        return self.board == other.board

class Game(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.geometry("1366x766")
        self.resizable(0,0)
        self.title("Image Puzzle Game")
        self.var = IntVar()
        self.var.set(0)
        self.container = Frame(self)
        self.container.pack(side="top",fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        self.buttons = {}
        _s = Board(self.container,self)
        self.show_frame("Board")
        
    def setup_window(self):
        pygame.init()
        pygame.display.set_caption(self.caption)
        pygame_icon = pygame.image.load('icon.png')
        pygame.display.set_icon(pygame_icon)

    def show_frame(self,frame_name):
        if frame_name == "Board":
            self.frames["Board"].grid()
        elif frame_name == "StartPage":
            if "Board" in self.frames:
                self.frames["Board"].grid_forget()
            self.frames[frame_name].grid()
        else:
            pass

class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.parent_frame = parent
        self.controller = controller
        self.create_vars()
        self.create_layout()

    def create_vars(self):
        self.var1 = StringVar()
        self.var1.set("3x3")
        self.var2 = StringVar()
        self.var2.set("A*")
        self.var3 = StringVar()
        self.var3.set("WD")

    def create_layout(self):
        inner_frame = Frame(self.parent_frame)
        inner_frame.grid_columnconfigure(0,weight=1)
        inner_frame.grid_columnconfigure(1,weight=1)
        for row in range(9):
            inner_frame.grid_rowconfigure(row,weight=1)    
        lab4opt1 = Label(inner_frame,text="1. Pilih Layout Papan", font="Arial 16 bold")
        lab4opt1.grid(row=4,column=0,sticky=E)
        option1 = OptionMenu(inner_frame, self.var1, "3x3", "4x4")
        option1.grid(row=4,column=1,sticky=W)
        lab4opt2 = Label(inner_frame,text="2. Pilih Algoritma Penyelesaian", font="Arial 16 bold")
        lab4opt2.grid(row=5,column=0,sticky=E)
        option2 = OptionMenu(inner_frame, self.var2, "A*", "IDA*")
        option2.grid(row=5,column=1,sticky=W)
        lab4opt3 = Label(inner_frame,text="3. Pilih Jarak Heuristic Manhattan/WalkingDistance", font="Arial 16 bold")
        lab4opt3.grid(row=6,column=0,sticky=E)
        option3 = OptionMenu(inner_frame, self.var3, "WD", "MH")
        option3.grid(row=6,column=1,sticky=W)
        lab4opt3 = Label(inner_frame,text="4. Tekan tombol START untuk memulai Game", font="Arial 16 bold")
        lab4opt3.grid(row=7,column=0,sticky=E)
        start_button = Button(inner_frame,text="START",command=self.start, font="Arial 16 bold")
        start_button.grid(row=7,column=1,sticky=W)
        self.controller.frames["StartPage"] = inner_frame

    def start(self):
        board_size = self.var1.get()
        algo = self.var2.get()
        heuristic = self.var3.get()
        _b = Board(self.parent_frame,self.controller,board_size,algo,heuristic)
        self.controller.show_frame("Board")

class Board(Frame):
    # def __init__(self, parent, controller, board_size="4x4",solving_algorithm="A*",heuristic_name="WD"):
    def __init__(self, parent, controller, board_size="5x5",solving_algorithm="A*",heuristic_name="WD"):
        Frame.__init__(self,parent)
        self.parent_frame = parent
        self.N = int(board_size[0])
        print(self.N)
        self.Nsq = self.N ** 2
        self.board = [x for x in range(1,self.Nsq + 1)]
        self.goal = [x for x in range(1,self.Nsq + 1)]
        self.controller = controller
        self.game_solved = True
        self.solution = ""
        self.solving_algo = solving_algorithm
        self.heuristic_name = heuristic_name
        self.blank = self.find_blank()
        self.create_content()
        self.controller.bind("<Key>",self.move)

    def animate_solution(self, solution):
        def callback(index):
            if index < len(solution):
                move_direction = solution_as_udlr(solution[index - 1], solution[index])
                self.swap_with_animation(move_direction)
                self.frame1.after(500, callback, index + 1)
            else:
                self.controller.buttons["shuffle"].config(state=NORMAL, bg="red")

        callback(1)

    def swap_with_animation(self, move_direction):
        blank_row = self.blank[0]
        blank_col = self.blank[1]
        drow, dcol = 0, 0

        if move_direction == "u":
            drow = -1
        elif move_direction == "d":
            drow = 1
        elif move_direction == "l":
            dcol = -1
        elif move_direction == "r":
            dcol = 1

        new_blank_row = blank_row + drow
        new_blank_col = blank_col + dcol
        but_to_swap = self.frame1.grid_slaves(row=new_blank_row, column=new_blank_col)[0]
        but_blank = self.frame1.grid_slaves(row=blank_row, column=blank_col)[0]

        but_to_swap['text'], but_blank['text'] = but_blank['text'], but_to_swap['text']
        but_to_swap['image'], but_blank['image'] = but_blank['image'], but_to_swap['image']
        but_to_swap['bg'], but_blank['bg'] = "red", "grey"

        new_idx = new_blank_row * self.N + new_blank_col
        old_idx = blank_row * self.N + blank_col
        self.board[new_idx], self.board[old_idx] = self.board[old_idx], self.board[new_idx]
        self.blank = (new_blank_row, new_blank_col)

    def solution_as_udlr(prev_board, current_board):
        prev_blank_idx = prev_board.index(len(prev_board))
        current_blank_idx = current_board.index(len(current_board))

        prev_row, prev_col = divmod(prev_blank_idx, int(len(prev_board) ** 0.5))
        current_row, current_col = divmod(current_blank_idx, int(len(current_board) ** 0.5))

        if current_row < prev_row:
            return "u"
        elif current_row > prev_row:
            return "d"
        elif current_col < prev_col:
            return "l"
        elif current_col > prev_col:
            return "r"
        else:
            return ""
    
    def isSolvable(self,seq=None):
        if seq == None:
            seq = list(self.board)
        else:
            pass 
        N = int(len(seq) ** 0.5)
        
        def countInv(seq):
            numinv = 0
            for i in range(0,N**2,1):
                for j in range(i+1,N**2,1):
                    if seq[i] != N**2 and seq[j] != N**2 and seq[i] > seq[j]:
                        numinv += 1
            return numinv

        def blankRow(seq):
            return N - ((seq.index(N**2)) // N + 1)
        def isEven(num):
            return num % 2 == 0
        def isOdd(num):
            return num % 2 == 1

        numinv = countInv(seq)

        if isOdd(N):
            return isEven(numinv)
        else:
            pos = blankRow(seq)
            if isEven(pos):
                return isEven(numinv)
            else:
                return isOdd(numinv)

    def shuffle(self):
        tmp = self.board.copy()
        random.shuffle(tmp)
        while not self.isSolvable(tmp):
            random.shuffle(tmp)
        self.board = tmp.copy()
        self.blank = self.find_blank()
        self.create_tiles()
        self.controller.var.set(0)
        self.solution = ""
        self.game_solved = False

    def find_blank(self):
        idx = self.board.index(self.Nsq)
        return (idx // self.N, idx % self.N)

    def move(self,event):
        blank_row = self.blank[0]
        blank_col = self.blank[1]
        sym = event.keysym
        if sym not in ["Atas","Bawah","Kiri","Kanan"]:
            print("Please press one of the arrow Keys\n")
        else:
            if sym == "Atas" and blank_row > 0:
                self.swap("Atas",-1,0)
            if sym == "Bawah" and blank_row < (self.N - 1):
                self.swap("Bawah",1,0)
            if sym == "Kiri" and blank_col > 0:
                self.swap("Kiri",0,-1)
            if sym == "Kanan" and blank_col < (self.N - 1):
                self.swap("Kanan",0,1)

    def move_solution(self):
        self.controller.buttons["shuffle"].config(state=DISABLED,bg="Grey")
        stboard,num_moves,time4soln,positions_look,hname,algo,moves2solve,soln = Solve(self.heuristic_name,self.solving_algo,self.board)
        
        if len(soln) == 0:
            print("puzzle was not solved")
        else:
            self.solution = moves2solve

        def callback():
            if len(self.solution) == 0:
                # self.controller.buttons["Solve"].config(state=NORMAL,bg="yellow")
                self.controller.buttons["Solution"].config(state=DISABLED,bg="Grey")
                self.controller.buttons["shuffle"].config(state=NORMAL,bg="yellow")
                return
            uldr = self.solution.pop(0)
            if uldr == "u":
                self.swap("Atas",-1,0)
            if uldr == "d":
                self.swap("Bawah",1,0)
            if uldr == "l":
                self.swap("Kiri",0,-1)
            if uldr == "r":
                self.swap("Kanan",0,1)
            self.frame1.after(500,callback)
        self.frame1.after(500, callback)
        
    def swap(self,move_name,drow,dcol):
        blank_row = self.blank[0]
        blank_col = self.blank[1]
        new_blank_row = blank_row + drow
        new_blank_col = blank_col + dcol
        but_to_swap = self.frame1.grid_slaves(row=new_blank_row,column=new_blank_col)[0]
        but_blank = self.frame1.grid_slaves(row=blank_row,column=blank_col)[0]

        tmp_to_swap = but_to_swap.image
        tmp_blank = but_blank.image
        but_to_swap.image = tmp_blank
        but_blank.image = tmp_to_swap

        but_to_swap.grid(row=blank_row, column=blank_col)
        but_blank.grid(row=new_blank_row, column=new_blank_col)

        new_idx = new_blank_row * self.N + new_blank_col
        old_idx = blank_row * self.N + blank_col
        self.board[new_idx], self.board[old_idx] = self.board[old_idx], self.board[new_idx]
        self.blank = (new_blank_row, new_blank_col)

        intvartmp = self.controller.var.get() + 1
        self.controller.var.set(intvartmp)
        if self.game_solved == False and self.board == self.goal:
            self.popupResult()
        else:
            pass

    def click(self,event):
        txt = event.widget['text']
        row = event.widget.grid_info()['row']
        col = event.widget.grid_info()['column']
        if (abs(row-self.blank[0]) + abs(col - self.blank[1])) == 1:
            if row == self.blank[0]:
                if col > self.blank[1]:
                    self.swap("Kanan",0,1)
                else:
                    self.swap("Kiri",0,-1)
            elif col == self.blank[1]:
                if row > self.blank[0]:
                    self.swap("Bawah",1,0)
                else:
                    self.swap("Atas",-1,0)
        else:
            print("Click a neighbour\n")

    def create_tiles(self):
        for i in range(self.N):
            for j in range(self.N):
                idx = i * self.N + j
                tmp = self.board[idx]
                if tmp == self.Nsq:
                    tmp = "  "
                    tmp_image = Image.open("blank_tile.png")
                    tmp_image = tmp_image.resize((100, 100), Image.Resampling.LANCZOS)
                    tile_image = ImageTk.PhotoImage(tmp_image)
                    but = Button(self.frame1, image=tile_image, command=lambda idx=idx: self.click(idx))
                    but.image = tile_image
                else:
                    # tmp_image = Image.open(f"tile_{tmp}.png")
                    tmp_image = Image.open(f"5/{tmp}.png")
                    tmp_image = tmp_image.resize((100, 100), Image.Resampling.LANCZOS)
                    tile_image = ImageTk.PhotoImage(tmp_image)
                    but = Button(self.frame1, image=tile_image, command=lambda idx=idx: self.click(idx))
                    but.image = tile_image

                but.grid(row=i,column=j)
                but.bind('<Button-1>',self.click)
    
    def create_content(self):
        inner_frame = Frame(self.parent_frame)
        frame0 = Frame(inner_frame)
        self.frame1 = Frame(inner_frame)
        frame2 = Frame(inner_frame)

        self.create_tiles()

        but_shuf = Button(frame2, text="Acak", bg="yellow", justify="center", font=("Arial Bold", 10),command=self.shuffle)
        but_shuf.pack(padx=1,side=LEFT)
        self.controller.buttons["shuffle"] = but_shuf

        but_realimage = Button(frame2, text="Show", bg="yellow", justify="center", font=("Arial Bold", 10),command=self.realImage)
        but_realimage.pack(padx=1,side=LEFT)
        self.controller.buttons["Show"] = but_realimage

        but_play = Button(frame2, text="Solusi", bg="yellow", justify="center", font=("Arial Bold", 10),command=self.move_solution)
        but_play.pack(padx=1,side=LEFT)
        self.controller.buttons["Solution"] = but_play
        
        but_quit = Button(frame2, text="Keluar", bg="orange", justify="center", font=("Arial Bold", 10),command=self.controller.destroy)
        but_quit.pack(padx=1,side=LEFT)

        frame0.grid(row=0,column=0,pady=10)
        self.frame1.grid(row=1,column=0,pady=10)
        frame2.grid(row=2,column=0,pady=10)
        self.controller.frames["Board"] = inner_frame

    def goToStart(self):
        self.controller.show_frame("StartPage")

    def popupResult(self):
        top = Toplevel()
        top.title("Result")
        top.geometry("200x200")
        msg_text = "DONE!\nPuzzle bergeser sebanyak {} kali".format(self.controller.var.get())
        msg = Message(top, text=msg_text, font=("Arial Bold", 16))
        msg.pack()
        button = Button(top, text="Keluar", command=top.destroy)
        button.pack()

    def realImage(self):
        top = tk.Toplevel()
        top.title("Original Image")

        image_path = "ori.png"
        original_image = Image.open(image_path)
        original_image = original_image.resize((500, 500), Image.Resampling.LANCZOS)
        tk_image = ImageTk.PhotoImage(original_image)

        image_label = tk.Label(top, image=tk_image)
        image_label.image = tk_image
        image_label.pack()

        close_button = Button(top, text="Close", command=top.destroy)
        close_button.pack()

    def Solver(self):
        self.controller.buttons["shuffle"].config(state=DISABLED,bg="Grey")
        stboard,num_moves,time4soln,positions_look,hname,algo,moves2solve,soln = Solve(self.heuristic_name,self.solving_algo,self.board)
        if len(soln) == 0:
            print("puzzle was not solved")
        else:
            self.solution = moves2solve
            # self.controller.buttons["Solve"].config(state=DISABLED,bg="Grey")
            # self.controller.buttons["Solution"].config(state=NORMAL,bg="yellow")

if __name__ == "__main__":
    game = Game()
    game.mainloop()
