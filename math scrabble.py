import pygame
from pygame import display, Rect, draw, event, quit, mouse, QUIT, MOUSEBUTTONDOWN, get_init
from pygame.mixer import Sound 
from pygame.font import Font
from random import choice, shuffle

# Initialize Pygame
pygame.init()

# Define the dimensions of the grid and individual cells
grid_size = 9
cell_size = 50
grid_width = grid_size * cell_size + 150
grid_height = grid_size * cell_size 

selected_col = 12
selected_row = None

# sound for player change
# masti_sound = Sound('discord-sounds.mp3')

# Define colors for different cells
LIGHT_BLUE = (173, 216, 230)
PINK = (255, 192, 203)
LIGHT_GREEN = (144, 238, 144)
YELLOW = (255, 255, 153)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
HIGHLIGHT = (255, 0, 0)

# Create a font object
font = pygame.font.Font(None, 36)

# Create the Pygame display
window_width = grid_width + 20  # Add 20 pixels for padding
window_height = grid_height + 20
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Scrabble Board")

NUMBERS = [1,2,3,4,5,6,7,8,9]
OPERATORS = ['-', '+', 'x', '/']

PLAYERNUMS = 3
PLAYEROPS = 3

#penalties
# P0 = 'A'            # start penalty, -1
# P1 = 'B'            # -2 penalty
# P2 = 'C'            # -3 penalty
# P3 = 'D'            # /2 penalty
# P4 = 'E'            # /3 penalty

DIVPEN = 0
MULTPEN = 0
SUBPEN = 0
ADDPEN = 0

POSPEN =[['/3', 0, '-1', 0, '/3', 0, '-1', 0, '/3'], 
         [0, '/2', 0, '-1', 0, '-1', 0, '/2', 0], 
         ['-1', 0, '-3', 0, '-1', 0, '-3', 0, '-1'], 
         [0, '-1', 0, '-2', 0, '-2', 0, '-1', 0],
         ['/3', 0, '-1', 0, 0, 0, '-1', 0, '/3'],
         [0, '-1', 0, '-2', 0, '-2', 0, '-1', 0],
         ['-1', 0, '-3', 0, '-1', 0, '-3', 0, '-1'], 
         [0, '/2', 0, '-1', 0, '-1', 0, '/2', 0],
         ['/3', 0, '-1', 0, '/3', 0, '-1', 0, '/3']]

board_grid = [[' '] * 9 for _ in range(9)]
board_grid[4][4] = choice(NUMBERS)

num_block = [' ', ' ', ' ']
op_block = [' ', ' ', ' ']

# color setting grid
color_grid = [[None]*10 for _ in range(10)]

# Define the special cells
special_cells = [
    (0, 0), (0, 4), (0, 8),
    (4, 0), (4, 8),
    (8, 0), (8, 4), (8, 8)
]

#pouches
numspouch = [1,2,3]*6 + [4,5]*4 + [6,7]*3 + [8,9]*2
shuffle(numspouch)
opspouch  = ['+', '-']*9 + ['x', '/']*6
shuffle(opspouch)

#if vertical or horizontal var
h_or_v = None  

num_loc = []
op_loc = []

# selected blocks from mouseclick
row_selected = None
col_selected = None
selected_num = None
selected_num_bool = False
selected_op = None
selected_op_bool = False

def calculate_total(exp):
    expnums = []
    expops = []

    for i in exp:
        expnums.append(i) if i in NUMBERS else expops.append(i)
        
    for x, y in enumerate(expops):
        if y == '/':
            expnums[x] = (expnums[x]/expnums[x+1]) 
            expnums.pop(x+1)
            expops.pop(x)
    for x, y in enumerate(expops):
        if y == 'x':
            expnums[x] = (expnums[x]*expnums[x+1]) 
            expnums.pop(x+1)
            expops.pop(x)
    for x, y in enumerate(expops):
        if y == '-':
            expnums[x] = (expnums[x]-expnums[x+1]) 
            expnums.pop(x+1)
            expops.pop(x)
    for x, y in enumerate(expops):
        if y == '+':
            expnums[x] = (expnums[x]+expnums[x+1]) 
            expnums.pop(x+1)
            expops.pop(x)

    return (expnums[0])

def write_num_grid(grid, cell_rect, i , j):
    font = pygame.font.Font(None, 24)
    number_text = font.render(str(grid[i][j]), True, (0, 0, 0))
    text_rect = number_text.get_rect(center=cell_rect.center)
    screen.blit(number_text, text_rect)

def write_block(block, cell_rect, i):
    font = pygame.font.Font(None, 24)
    number_text = font.render(str(block[i]), True, (0, 0, 0))
    text_rect = number_text.get_rect(center=cell_rect.center)
    screen.blit(number_text, text_rect)        

def draw_grid():
    for i in range(grid_size):
        for j in range(grid_size):
            cell_rect = pygame.Rect(j * cell_size + 4, i * cell_size + 4, cell_size, cell_size)
            pygame.draw.rect(screen, color_grid[i][j], cell_rect)
            pygame.draw.rect(screen, BLACK, cell_rect, width = 1)
            
            write_num_grid(board_grid, cell_rect, i, j)

def draw_num_block(num_block):
    for i in range(PLAYERNUMS):
        cell_rect = pygame.Rect(500, i * cell_size + 4, cell_size, cell_size)
        pygame.draw.rect(screen, YELLOW, cell_rect)
        pygame.draw.rect(screen, BLACK, cell_rect, width = 1)

        write_block(num_block, cell_rect, i)

def draw_op_block(op_block):
    for i in range(PLAYERNUMS):
        cell_rect = pygame.Rect(500, i * cell_size + 204, cell_size, cell_size)
        pygame.draw.rect(screen, YELLOW, cell_rect)
        pygame.draw.rect(screen, BLACK, cell_rect, width = 1)

        write_block(op_block, cell_rect, i)

# Assign colors to the cells
for i in range(grid_size):
    for j in range(grid_size):
        if (i, j) in special_cells:
            color_grid[i][j] = YELLOW
        elif i % 4 == j % 4 == 0:
            color_grid[i][j] = LIGHT_GREEN
        elif (i % 4 == 0 and j % 4 == 2) or (i % 4 == 2 and j % 4 == 0):
            color_grid[i][j] = PINK
        else:
            color_grid[i][j] = LIGHT_BLUE

class Player:
    def __init__(self) -> None:
        self.nums = []
        self.ops = []
        self.score = 0

        for _ in range(PLAYERNUMS):
            self.nums.append(choice(numspouch))
        for _ in range(PLAYEROPS):
            self.ops.append(choice(opspouch))

    def updateNumber(self, numspouch, selected_num_index):
        self.nums[selected_num_index] = choice(numspouch)
        
    def updateOps(self, opspouch, selected_op_index):
        self.ops[selected_op_index] = choice(opspouch)

    def calcScore(self, num_loc, op_loc, board_grid):
        h_or_v = None

        if num_loc[0] == op_loc[0]:         #rows
            h_or_v = 'horizontal'
        elif num_loc[1] == op_loc[1]:       #columns
            h_or_v = 'vertical'
        
        if h_or_v == 'vertical':
            titty = [col[num_loc[1]] for col in board_grid if col[num_loc[1]] != " "]
            if num_loc[1] % 2 != 0:
                titty = titty[1:-1]
            self.score += calculate_total(titty)
        elif h_or_v == 'horizontal':
            titty = board_grid[num_loc[0]]
            titty = [tt for tt in titty if tt != " "]
            if num_loc[0] % 2 != 0:
                titty = titty[1:-1]
            self.score += calculate_total(titty)
        else:
            pass
            

player1 = Player()
player2 = Player()

p1_num_block = player1.nums
p1_op_block = player1.ops
p2_num_block = player2.nums
p2_op_block = player2.ops

num_block = p1_num_block
op_block = p1_op_block

selected_num_index = 1
selected_op_index = 1

def print_text_in_block(player1_score, i, j):     # for p1: 470, 370; for p2: 470, 420
    rectang = pygame.Rect(i, j, cell_size + 80, cell_size)
    pygame.draw.rect(screen, YELLOW, rectang)
    pygame.draw.rect(screen, BLACK, rectang, width = 1)        
    font = pygame.font.Font(None, 24)
    number_text = font.render(player1_score, True, BLACK)
    text_rect = number_text.get_rect(center=rectang.center)
    screen.blit(number_text, text_rect)   

def calculate_board(board_grid):
    calculation_board = [[' '] * 9 for _ in range(9)]
    for i in range(grid_size):
        for j in range(grid_size):
            if board_grid[i][j] != ' ':
                if POSPEN[i][j] == '-1':
                    calculation_board[i][j] = board_grid[i][j] - 1
                elif POSPEN[i][j] == '-2':
                    calculation_board[i][j] = board_grid[i][j] - 2
                elif POSPEN[i][j] == '3':
                    calculation_board[i][j] = board_grid[i][j] - 3
                elif POSPEN[i][j] == '/2':
                    calculation_board[i][j] = int(board_grid[i][j] / 2)
                elif POSPEN[i][j] == '/3':
                    calculation_board[i][j] = int(board_grid[i][j] / 3)
                else:
                    calculation_board[i][j] = board_grid[i][j]

    return calculation_board

p1_chance = True
count = 0

num_loc = [0,0]
op_loc = [0,0]

running = True
screen.fill((255, 255, 255))  # Fill window with white color

while running:
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            selected_row = mouse_pos[1] // cell_size 
            selected_col = mouse_pos[0] // cell_size 
            # print(mouse_pos[0], mouse_pos[1])


    if p1_chance:
        num_block = player1.nums
        op_block = player1.ops
        print_text_in_block("p1 score: " + str(player1.score), 470, 370)
        print_text_in_block("p2 score: " + str(player2.score), 470, 420)  
    else: 
        num_block = player2.nums
        op_block = player2.ops
        print_text_in_block("p1 score: " + str(player1.score), 470, 370)
        print_text_in_block("p2 score: " + str(player2.score), 470, 420)  
        

    # Draw the grid
    draw_grid()  

    draw_op_block(op_block)

    draw_num_block(num_block)

    # number selecting
    if selected_col == 10 and selected_row in [0,1,2]:
        cell_rect_1 = pygame.Rect(500, cell_size * selected_row + 4, cell_size, cell_size)
        pygame.draw.rect(screen, RED, cell_rect_1, width = 4)
        # if not selected_num_bool:
        selected_num = num_block[selected_row]
        selected_num_index = selected_row
        selected_num_bool = True

    # operator selecting
    if selected_col == 10 and selected_row in [4, 5, 6]:
        cell_rect_2 = pygame.Rect(500, cell_size * selected_row + 4, cell_size, cell_size)
        pygame.draw.rect(screen, RED, cell_rect_2, width = 4)
        selected_op = op_block[selected_row - 4]
        selected_op_index = selected_row - 4 
        selected_op_bool = True

    # updating contents in board grid
    if selected_col < 9:
        cell_rect_0 = pygame.Rect(cell_size * selected_col + 4, cell_size * selected_row + 4, cell_size, cell_size)
        pygame.draw.rect(screen, RED, cell_rect_0, width = 4)    
        if (selected_row + selected_col) % 2 == 0  and (selected_num_bool):
            board_grid[selected_row][selected_col] = selected_num
            selected_num_bool = False
            num_loc = [selected_row, selected_col]
            count += 1
            if p1_chance:
                player1.updateNumber(numspouch, selected_num_index)
            else:
                player2.updateNumber(numspouch, selected_num_index)

        elif (selected_row + selected_col) % 2 != 0  and (selected_op_bool):
            board_grid[selected_row][selected_col] = selected_op
            selected_op_bool = False
            op_loc = [selected_row, selected_col]
            count += 1
            if p1_chance:
                player1.updateOps(opspouch, selected_op_index)
            else:
                player2.updateOps(opspouch, selected_op_index)

    if count == 2:
        if p1_chance:
            pp = calculate_board(board_grid)
            player1.calcScore(num_loc, op_loc, pp)
        else:
            pp = calculate_board(board_grid)
            player2.calcScore(num_loc, op_loc, pp)
        p1_chance = not p1_chance
        # masti_sound.play()
        count = 0

    pygame.display.update()

# Quit Pygame
pygame.quit()