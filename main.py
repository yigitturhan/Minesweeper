import tkinter as tk
import random as rd
from PIL import Image, ImageTk

game_over, win = False, False
matrix = []
count, remaining_mines = 0, 0
root, game_over_window, win_game_window = None, None, None
color_mapping = {
    1: 'blue',
    2: 'green',
    3: 'brown',
    4: 'purple',
    5: 'red',
    6: 'cyan',
    7: 'orange',
    8: 'black'
}
bg_color = 'grey81'


def neighbour_create(x, y):
    return [(x - 1, y), (x - 1, y + 1), (x, y - 1), (x + 1, y - 1), (x + 1, y), (x + 1, y + 1), (x, y + 1),
            (x - 1, y - 1)]


def reset_data():
    global game_over, win, matrix, count, game_over_window, remaining_mines, root
    game_over, win, matrix, count, root, game_over_window, remaining_mines = False, False, [], 0, None, None, 0


def start_page(game):
    global root
    if game:
        game.destroy()
    if root:
        root.destroy()
    reset_data()
    start_window = tk.Tk()
    start_window.title("Minesweeper")
    beginner_button = tk.Button(start_window, text="Beginner", command=lambda: button_click("beginner", start_window))
    intermediate_button = tk.Button(start_window, text="Intermediate",
                                    command=lambda: button_click("intermediate", start_window))
    expert_button = tk.Button(start_window, text="Expert", command=lambda: button_click("expert", start_window))
    result_label = tk.Label(start_window, text="")
    beginner_button.pack()
    intermediate_button.pack()
    expert_button.pack()
    result_label.pack()
    start_window.mainloop()


def game_over_message():
    global game_over_window
    if game_over_window:
        game_over_window.destroy()
    game_over_window = tk.Toplevel(root)
    game_over_window.title("Game Over")
    game_over_label = tk.Label(game_over_window, text="Game Over", font=("Helvetica", 24))
    game_over_label.pack(padx=20, pady=20)
    try_again_button = tk.Button(game_over_window, text="Try Again", command=lambda: start_page(game_over_window))
    try_again_button.pack(pady=10)
    game_over_window.mainloop()


def button_click(level, start_window):
    global root, matrix, remaining_mines
    start_window.destroy()
    if root:
        root.destroy()
    root = tk.Tk()
    if level == "beginner":
        rows, cols, mines = 9, 9, 10
        remaining_mines = 10
    elif level == "intermediate":
        rows, cols, mines = 16, 16, 40
        remaining_mines = 40
    else:
        rows, cols, mines = 30, 16, 99
        remaining_mines = 99
    matrix = create_board(rows, cols, mines)
    draw_board()


def win_game():
    global win_game_window, root
    if win_game_window:
        win_game_window.destroy()
    win_game_window = tk.Toplevel(root)
    win_game_window.title("You win!")
    win_game_label = tk.Label(win_game_window, text="Congratulations, you win!", font=("Helvetica", 24))
    win_game_label.pack(padx=20, pady=20)
    try_again_button = tk.Button(win_game_window, text="Try Again", command=lambda: start_page(win_game_window))
    try_again_button.pack(pady=10)
    win_game_window.mainloop()


def is_mine(i, j):
    if matrix[i][j][0] == 9:
        return True
    return False


def open_consecutive_zeros(lst, lst2):
    global matrix
    cols, rows = len(matrix[0]), len(matrix)
    if len(lst) == 0:
        return matrix
    for p in lst:
        lst.remove(p)
        matrix[p[0]][p[1]][1] = True
        x, y = p
        if p not in lst2:
            lst2.append(p)
        neighbors = neighbour_create(x, y)
        for i in neighbors:
            if i in lst2 or i in lst:
                neighbors.remove(i)
        for n in neighbors:
            if 0 <= n[0] <= cols - 1 and 0 <= n[1] <= rows - 1:
                if matrix[n[0]][n[1]][0] == 0:
                    if n not in lst2 and n not in lst:
                        lst.append(n)
                else:
                    matrix[n[0]][n[1]][1] = True
    return open_consecutive_zeros(lst, lst2)


def is_finished():
    global matrix
    for i in matrix:
        for j in i:
            if j[0] != 9 and (not j[1]):
                return False
    return True


def click_handler(event, i, j):
    global matrix, count, remaining_mines, game_over
    if matrix[i][j][2]:
        return
    print(matrix[i][j][1])
    if matrix[i][j][1]:
        open_surroundings(i, j)
    else:
        matrix[i][j][1] = True
        if is_mine(i, j):
            if count == 0:
                matrix[i][j][2] = not matrix[i][j][2]
                remaining_mines -= 1
            else:
                game_over = True
        count += 1
        if matrix[i][j][0] == 0:
            matrix = open_consecutive_zeros([(i, j)], [])
        if is_finished():
            matrix[i][j][1] = True
            win_game()
            return
    draw_board()


def open_surroundings(i, j):
    global matrix
    count = 0
    for x in range(i - 1, i + 2):
        for y in range(j - 1, j + 2):
            if x < 0 or x >= len(matrix) or y < 0 or y >= len(matrix[0]):
                continue
            if matrix[x][y][0] == 9 and matrix[x][y][2]:
                count += 1
    if count == matrix[i][j][0]:
        for x in range(i - 1, i + 2):
            for y in range(j - 1, j + 2):
                if x < 0 or x >= len(matrix) or y < 0 or y >= len(matrix[0]):
                    continue
                matrix[x][y][1] = True


def right_click_handler(event, i, j):
    global remaining_mines, matrix
    if matrix[i][j][1]:
        draw_board()
        return
    elif matrix[i][j][2]:
        remaining_mines += 1
    else:
        remaining_mines -= 1
    matrix[i][j][2] = not matrix[i][j][2]
    draw_board()


def draw_board():
    global game_over, win, matrix, remaining_mines, root
    if not root:
        root = tk.Tk()
    for widget in root.winfo_children():
        widget.destroy()
    rows, cols = len(matrix), len(matrix[0])
    remaining_mines_label = tk.Label(root, text=f"Remaining Mines: {remaining_mines}", bg='grey60')
    remaining_mines_label.grid(row=0, column=0, columnspan=cols)
    if game_over:
        open_board()
        for x in range(rows):
            for y in range(cols):
                value = matrix[x][y][0]
                if value == 0:
                    label = tk.Label(root, text='', width=4, height=2, relief=tk.RIDGE, fg='red', bg='grey60')
                elif value == 9:
                    img = (Image.open("bomb.png"))
                    resized_image = img.resize((35, 33))
                    new_image = ImageTk.PhotoImage(resized_image)
                    label = tk.Label(root, image=new_image, bg='grey60')
                    label.image = new_image
                else:
                    color = color_mapping.get(value, 'black')
                    label = tk.Label(root, text=str(value), width=4, height=2, relief=tk.RIDGE, fg=color, bg='grey60')
                label.grid(row=x + 1, column=y)
        root.update()
        game_over_message()
        return
    if win:
        root.destroy()
        win_game()
        return
    for x in range(rows):
        for y in range(cols):
            value = matrix[x][y][0]
            if matrix[x][y][2]:
                img = (Image.open("flag.png"))
                resized_image = img.resize((35, 33))
                new_image = ImageTk.PhotoImage(resized_image)
                label = tk.Label(root, image=new_image, bg='grey60')
                label.image = new_image
            elif not matrix[x][y][1]:
                label = tk.Label(root, text='', width=4, height=2, relief=tk.RIDGE, bg=bg_color)
            elif value == 0:
                label = tk.Label(root, text='', width=4, height=2, relief=tk.RIDGE, fg='red', bg='grey60')
            else:
                color = color_mapping.get(value, 'black')
                label = tk.Label(root, text=str(value), width=4, height=2, relief=tk.RIDGE, fg=color, bg='grey60')
            click_lambda = lambda event, i=x, j=y: click_handler(event, i, j)
            right_click_lambda = lambda event, i=x, j=y: right_click_handler(event, i, j)
            label.bind("<Button-1>", click_lambda)
            label.bind("<Button-2>", right_click_lambda)
            label.grid(row=x + 1, column=y)
    root.mainloop()


def create_board(rows, cols, num_mines):
    board = [[[0, False, False] for _ in range(0, rows)] for _ in range(0, cols)]
    board_coordinates = [(x, y) for x in range(0, cols) for y in range(0, rows)]
    mine_coordinates = rd.sample(board_coordinates, num_mines)
    for mine in mine_coordinates:
        x, y = mine
        board[x][y][0] = 9
        neighbors = neighbour_create(x, y)
        for n in neighbors:
            if 0 <= n[0] <= cols - 1 and 0 <= n[1] <= rows - 1 and n not in mine_coordinates:
                board[n[0]][n[1]][0] += 1
    return board


def open_board():
    for i in matrix:
        for j in i:
            j[2], j[1] = False, True


start_page(game_over_window)
