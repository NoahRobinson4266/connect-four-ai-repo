import random
from funcs import *


def ai(p1_board, p2_board, x_tiles=7, y_tiles=6):
    moves = []

    columns = []

    combined_bin = bin(p1_board | p2_board)[2:]

    for i in range(x_tiles):
        columns.append([])

    for i, char in enumerate(combined_bin[::-1]):
        columns[math.floor(i / y_tiles)].append(int(char))

    for i in range(x_tiles):
        if sum(columns[i]) < y_tiles:
            moves.append(i)

    try:
        return random.choice(moves)
    except IndexError:
        return None


def play_random_moves(p1_board, p2_board, num_of_moves=1, x_tiles=7, y_tiles=6):
    if num_of_moves == 0:
        return p1_board, p2_board

    x_pos = ai(p1_board, p2_board, x_tiles=x_tiles, y_tiles=y_tiles)

    if x_pos is None:
        return p1_board, p2_board

    board = int(bin(p1_board | p2_board), 2)
    column = board >> (x_pos * y_tiles)
    column -= (column >> y_tiles) << y_tiles
    column = bin(column)

    highest_val = highest_bit_flipped(column)

    y_pos = highest_val

    inserted_value = 1 << y_pos
    inserted_value <<= x_pos * y_tiles

    p2_board |= inserted_value

    if check_for_win(p1_board, x_pos, y_pos, x_tiles=x_tiles, y_tiles=y_tiles):
        return p1_board, p2_board

    return play_random_moves(p2_board, p1_board, num_of_moves-1, x_tiles=x_tiles, y_tiles=y_tiles)
