import pygame
import time

pygame.font.init()

# Screen dimensions
WIDTH, HEIGHT = 540, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")

# Fonts
FONT = pygame.font.SysFont('comicsans', 40)
FONT_SMALL = pygame.font.SysFont('comicsans', 2)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE  = (0, 0, 225)
RED = (255, 0, 0)

# Default grid
grid = [
    [7, 8, 0, 4, 0, 0, 1, 2, 0],
    [6, 0, 0, 0, 7, 5, 0, 0, 9],
    [0, 0, 0, 6, 0, 1, 0, 7, 8],
    [0, 0, 7, 0, 4, 0, 2, 6, 0],
    [0, 0, 1, 0, 5, 0, 9, 3, 0],
    [9, 0, 4, 0, 6, 0, 0, 0, 5],
    [0, 7, 0, 3, 0, 0, 0, 1, 2],
    [1, 2, 0, 0, 0, 7, 4, 0, 0],
    [0, 4, 9, 2, 0, 6, 0, 0, 7]
]

class Grid:
    def __init__(self, rows, cols, width, height):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.cells = [[Cell(grid[i][j], i, j, width, height)
                       for j in range(cols)] for i in range(rows)]
        self.model = None
        self.update_model()
        self.selected = None

    def update_model(self):
        self.model = [[self.cells[i][j].value for j in 
                       range(self.cols)] for i in range(self.rows)]

    def draw(self, win):
        gap = self.width / 9
        for i in range(self.rows + 1):
            thick = 4 if i % 3 == 0 else 1
            pygame.draw.line(win, BLACK, (0, i * gap), (self.width, i * gap), thick)
            pygame.draw.line(win, BLACK, (i * gap, 0), (i * gap, self.height), thick)

        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j].draw(win)

    def select(self, row, col):
        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j].selected = False
        self.cells[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        if self.selected:
            row, col = self.selected
            if self.cells[row][col].value == 0:
                self.cells[row][col].set_temp(0)

    def click(self, pos):
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        else:
            return None

    def place(self, val):
        if self.selected:
            row, col = self.selected
            if self.cells[row][col].value == 0:
                self.cells[row][col].set(val)
                self.update_model()

                if valid(self.model, val, (row, col)) and self.solve():
                    return True
                else:
                    self.cells[row][col].set(0)
                    self.cells[row][col].set_temp(0)
                    self.update_model()
                    return False
        return False

    def solve(self):
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i

                if self.solve():
                    return True

                self.model[row][col] = 0

        return False

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cells[i][j].value == 0:
                    return False
        return True

class Cell:
    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 45)
        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, BLUE)
            win.blit(text, (x + (gap / 2 - text.get_width() / 
                 2), y + (gap / 2 - text.get_height() / 2)))
        elif self.value != 0:
            text = fnt.render(str(self.value), 1, BLACK)
            win.blit(text, (x + (gap / 2 - text.get_width() / 
                                 2), y + (gap / 2 - text.get_height() / 2)))

        if self.selected:
            pygame.draw.rect(win, RED, (x, y, gap, gap), 3)

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val

def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)
    return None

def valid(bo, num, pos):
    for i in range(len(bo[0])):
        if bo[pos[1]][i] == num and pos[1] != i:
            return False

    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False

    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if bo[i][j] == num and (i, j) != pos:
                return False

    return True

def redraw_window(win, board, time, strikes):
    win.fill(WHITE)
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 0, BLACK)
    win.blit(text, (540 - 160, 560))
    text = fnt.render("X " * strikes, 1, RED)
    win.blit(text, (20, 560))
    board.draw(win)

def format_time(secs):
    sec = secs % 60
    minute = secs // 60
    hour = minute // 60
    return " {}:{}:{}".format(hour, minute, sec)

def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudoku")
    board = Grid(9, 9, WIDTH, HEIGHT - 60)
    key = None
    run = True
    start = time.time()
    strikes = 0

    while run:
        play_time = round(time.time() - start)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None
                if event.key == pygame.K_RETURN:
                    if board.selected:
                        i, j = board.selected
                        if board.cells[i][j].temp != 0:
                            if board.place(board.cells[i][j].temp):
                                print("Success")
                            else:
                                print("Wrong")
                                strikes += 1
                            key = None

                            if board.is_finished():
                                print("Game over")
                                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key is not None:
            board.cells[board.selected[0]][board.selected[1]].set_temp(key)

        redraw_window(win, board, play_time, strikes)
        pygame.display.update()

main()
pygame.quit()