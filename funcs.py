import math
import pygame

pygame.init()

positive_infinity = math.inf
negative_infinity = -math.inf

necessary_tiles = [[False, False, False, True, False, False, False],
                   [False, False, False, True, False, False, False],
                   [True, True, True, True, True, True, True],
                   [False, False, False, True, False, False, False],
                   [False, False, False, True, False, False, False],
                   [False, False, False, True, False, False, False]]


def check_for_win(board_state, x, y, x_tiles=7, y_tiles=6, num_to_win=4, return_streak=False):
    tile_dist_from_end = x * y_tiles + y
    directions = [1, y_tiles, y_tiles + 1, y_tiles - 1, -1, -y_tiles, -(y_tiles + 1), -(y_tiles - 1)]
    scores = [0, 0, 0, 0, 0, 0, 0, 0]
    tile_has_piece = False

    if bin(board_state >> tile_dist_from_end)[-1] == '1':
        tile_has_piece = True

    for j, direction in enumerate(directions):
        for i in range(1, num_to_win + 1):
            index_to_check = tile_dist_from_end + (i * direction)

            if index_to_check >= 0:
                x_to_check = math.floor(index_to_check / y_tiles)
                y_to_check = index_to_check % y_tiles

                abs_x_dir = abs(x_to_check - x) / i
                abs_y_dir = abs(y_to_check - y) / i

                if max(abs(x - x_to_check), abs(y - y_to_check)) == i and (x != x_to_check or y != y_to_check) and \
                        bin(board_state >> index_to_check)[-1] == '1' and (abs_x_dir == 1 or abs_x_dir == 0) and \
                        (abs_y_dir == 1 or abs_y_dir == 0):
                    scores[j] += 1

                    if tile_has_piece and scores[j] + scores[int((j + len(directions) / 2) % len(directions))] >= \
                            num_to_win - 1:
                        if return_streak:
                            streak_start = [x_to_check, y_to_check]
                            try:
                                x_end = x_to_check + (x - x_to_check) / abs(x - x_to_check) * (num_to_win - 1)
                            except ZeroDivisionError:
                                x_end = x_to_check

                            try:
                                y_end = y_to_check + (y - y_to_check) / abs(y - y_to_check) * (num_to_win - 1)
                            except ZeroDivisionError:
                                y_end = y_to_check

                            streak_end = [x_end, y_end]

                            return True, streak_start, streak_end

                        return True
                    elif scores[j] >= num_to_win:
                        if return_streak:
                            streak_start = [x, y]
                            streak_end = [x_to_check + (x_to_check - x) / i * scores[j], y_to_check + (y_to_check - y)
                                          / i * scores[j]]

                            return True, streak_start, streak_end

                        return True
                else:
                    break
            else:
                break

    return False


def check_board_for_win(board_state, x_tiles=7, y_tiles=6, num_to_win=4):
    for i in range(x_tiles):
        for j in range(y_tiles):
            if necessary_tiles[j][i] and check_for_win(board_state, i, j, x_tiles=x_tiles, y_tiles=y_tiles,
                                                       num_to_win=num_to_win):
                return True

    return False


def check_full_board(p1_state, p2_state, x_tiles=7, y_tiles=6):
    full_board = p1_state | p2_state

    if full_board == 2 ** (x_tiles * y_tiles) - 1:
        return True

    return False


def highest_bit_flipped(binary_number):
    num = int(binary_number, 2)

    highest_bit_position = 0
    while num:
        num >>= 1
        highest_bit_position += 1

    return highest_bit_position


def return_move_pos(current_moves, prev_moves, y_tiles=6):
    move_made = current_moves ^ prev_moves
    index = int(math.log2(move_made))

    x = math.floor(index / y_tiles)
    y = index % y_tiles

    return x, y


def find_all_moves(p1_moves, p2_moves, search_depth=1, x_tiles=7, y_tiles=6, moves_thusfar=None):
    all_boards = []

    if moves_thusfar is None:
        moves_thusfar = []

    for i in range(x_tiles):
        x_pos = i

        board = int(bin(p1_moves | p2_moves), 2)
        column = board >> (x_pos * y_tiles)
        column -= (column >> y_tiles) << y_tiles
        column = bin(column)

        highest_val = highest_bit_flipped(column)

        if highest_val < y_tiles:
            y_pos = highest_val

            inserted_value = 1 << y_pos
            inserted_value <<= x_pos * y_tiles

            new_board = p1_moves | inserted_value

            if search_depth <= 1:
                all_boards.append([moves_thusfar + [i], new_board])
            else:

                moves = find_all_moves(p2_moves, p1_moves, search_depth-1, x_tiles=x_tiles, y_tiles=y_tiles,
                                       moves_thusfar=moves_thusfar+[i])
                all_boards.append(moves)

    return all_boards


def find_end_positions(p1_moves, p2_moves, depth, x_tiles=7, y_tiles=6):
    all_boards = []

    if depth <= 0:
        return [(p1_moves, p2_moves)]
    else:
        all_moves = find_all_moves(p1_moves, p2_moves, 1, x_tiles=x_tiles, y_tiles=y_tiles)

        for move in all_moves:
            if check_board_for_win(move[1], x_tiles=x_tiles, y_tiles=y_tiles):
                return [positive_infinity]

        if check_full_board(p2_moves, all_moves[0][1]):
            return [0]

        index = 0
        for move in all_moves:
            if index != move[0][0]:
                all_boards.append([])
                index += 1

            all_boards.append(find_end_positions(p2_moves, move[1], depth-1, x_tiles=x_tiles, y_tiles=y_tiles))

            index += 1

        return all_boards


def draw_board(win, p1_board, p2_board, width=700, height=600, x_tiles=7, y_tiles=6, board_colour=(40, 60, 240),
               bg_colour=(255, 255, 255), p1_colour=(240, 250, 80), p2_colour=(250, 10, 40), line_colour=(0, 0, 0),
               start_streak=None, end_streak=None, draw_pieces=True):
    pygame.draw.rect(win, board_colour, (0, 0, width, height))

    for i in range(x_tiles):
        for j in range(y_tiles):
            x_pos = i * (width / x_tiles) + (width / x_tiles) / 2
            y_pos = j * (height / y_tiles) + (height / y_tiles) / 2

            radius = ((width / x_tiles) + (height / y_tiles)) / 2 / 2.5

            colour = bg_colour
            offset = x_tiles - y_tiles + 1

            if draw_pieces:
                if len(bin(p1_board)) >= i * y_tiles + (x_tiles - offset - j) and bin(p1_board >> (i * y_tiles +
                                                                                                   (x_tiles -
                                                                                                    offset -
                                                                                                    j)))[-1] \
                        == '1':
                    colour = p1_colour
                elif len(bin(p2_board)) >= i * y_tiles + (x_tiles - offset - j) and bin(p2_board >> (i * y_tiles +
                                                                                                     (x_tiles
                                                                                                      - offset
                                                                                                      - j)))\
                        [-1] == '1':
                    colour = p2_colour

            pygame.draw.circle(win, colour, (x_pos, y_pos), radius)

    if start_streak is not None and end_streak is not None and start_streak[0] >= 0:

        x_start = start_streak[0] * (width / x_tiles) + (width / x_tiles) / 2
        x_end = end_streak[0] * (width / x_tiles) + (width / x_tiles) / 2
        y_start = (y_tiles - start_streak[1] - 1) * (height / y_tiles) + (height / y_tiles) / 2
        y_end = (y_tiles - end_streak[1] - 1) * (height / y_tiles) + (height / y_tiles) / 2

        pygame.draw.line(win, line_colour, (x_start, y_start), (x_end, y_end), round((width + height) /
                                                                                     250))


# A function that takes in two numbers (player 1 and 2's board positions) and outputs an array of the piece positions
def convert_board_to_input(p1_board, p2_board, x_tiles=7, y_tiles=6, group=True):
    p1_bin = bin(p1_board)[2:]
    p2_bin = bin(p2_board)[2:]

    board = []

    for i in range(x_tiles * y_tiles):
        if group and i % 6 == 0:
            board.append([])
        if len(p1_bin) > i and p1_bin[::-1][i] == '1':
            if group:
                board[-1].append(1)
            else:
                board.append(1)
        elif len(p2_bin) > i and p2_bin[::-1][i] == '1':
            if group:
                board[-1].append(-1)
            else:
                board.append(-1)
        else:
            if group:
                board[-1].append(0)
            else:
                board.append(0)

    if group:
        new_board = []
        for i in range(y_tiles):
            new_board.append([l[i] for l in board])

        board = new_board

    return board
