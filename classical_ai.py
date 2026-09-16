from funcs import *
import random
import math
import time
# import json

opening_tile_weights = [4, 6, 4, 2, 1, 0, 7, 8, 6, 3, 2, 1, 10, 11, 8, 6, 4, 3, 14, 15, 14, 11, 8, 6, 10, 11, 8, 6, 4,
                        3, 7, 8, 6, 3, 2, 1, 4, 6, 4, 2, 1, 0]
endgame_tile_weights = [5, 5, 3, 3, 3, 1, 7, 7, 5, 4, 3, 2, 10, 10, 7, 6, 5, 3, 13, 11, 8, 8, 7, 6, 10, 10, 7, 6, 5, 3,
                        7, 7, 5, 4, 3, 2, 5, 5, 3, 3, 3, 1]


def format_known_moves():
    p1_boards = []
    p2_boards = []
    best_moves = []

    with open('known_moves_database.txt') as f:
        for line in f:
            parts = line.split(' ')
            p1_boards.append(int(parts[0]))
            p2_boards.append(int(parts[1]))
            best_moves.append(int(parts[2]))

    return p1_boards, p2_boards, best_moves


known_p1_boards, known_p2_boards, known_best_moves = format_known_moves()


def evaluate_position(p1_board, p2_board, x_tiles=7, y_tiles=6, num_to_win=4):
    tile_weights_weight = 1

    score_precision = 100

    p1_bin = bin(p1_board)[2:]
    p2_bin = bin(p2_board)[2:]

    if sum(list(map(int, p1_bin.strip()))) >= num_to_win and sum(list(map(int, p2_bin.strip()))) >= num_to_win:
        for i in range(x_tiles):
            for j in range(y_tiles):
                if necessary_tiles[j][i]:
                    index = i * y_tiles + j

                    if len(p1_bin) > index and p1_bin[::-1][index] == '1' and check_for_win(p1_board, i, j, x_tiles,
                                                                                            y_tiles, num_to_win):
                        return positive_infinity
                    if len(p2_bin) > index and p2_bin[::-1][index] == '1' and check_for_win(p2_board, i, j, x_tiles,
                                                                                            y_tiles, num_to_win):
                        return negative_infinity

    if check_full_board(p1_board, p2_board, x_tiles=x_tiles, y_tiles=y_tiles):
        return 0

    score = 0

    endgame_score = 0
    full_board = p1_board | p2_board

    for char in bin(full_board)[2:]:
        endgame_score += int(char)

    endgame_score /= x_tiles * y_tiles

    for i, char in enumerate(bin(p1_board)[2:][::-1]):
        score += int(char) * opening_tile_weights[i] * (1 - endgame_score) * tile_weights_weight
        score += int(char) * endgame_tile_weights[i] * endgame_score * tile_weights_weight

    for i, char in enumerate(bin(p2_board)[2:][::-1]):
        score -= int(char) * opening_tile_weights[i] * (1 - endgame_score) * tile_weights_weight
        score -= int(char) * endgame_tile_weights[i] * endgame_score * tile_weights_weight

    score = round(score * score_precision) / score_precision

    return score


def deep_eval(win, p1_board, p2_board, search_depth, x_tiles=7, y_tiles=6, num_to_win=4, display_moves=False,
              current_best_score=positive_infinity):
    if search_depth <= 1:
        score = evaluate_position(p1_board, p2_board, x_tiles=x_tiles, y_tiles=y_tiles, num_to_win=num_to_win)

        if display_moves:
            draw_board(win, p2_board, p1_board)
            pygame.display.update()
            time.sleep(0.1)

        return score
    else:
        all_moves = find_all_moves(p2_board, p1_board, 1, x_tiles=x_tiles, y_tiles=y_tiles)
        high_score = negative_infinity

        sorted_moves = []
        while all_moves:
            sorted_moves.append(all_moves.pop(len(all_moves) // 2))

        for move in sorted_moves:
            score = evaluate_position(move[1], p1_board, x_tiles=x_tiles, y_tiles=y_tiles, num_to_win=num_to_win)

            if abs(score) >= positive_infinity:
                return -score

            score = deep_eval(win, move[1], p1_board, search_depth-1, x_tiles=x_tiles, y_tiles=y_tiles,
                              num_to_win=num_to_win, current_best_score=-high_score)

            if score > current_best_score:
                return -(score + 0.01)

            if score > high_score:
                high_score = score

        return -high_score


def ai(win, p1_board, p2_board, search_depth, x_tiles=7, y_tiles=6, num_to_win=4, return_all_moves=False,
       print_info=False, return_eval=False):
    for i in range(len(known_p1_boards)):
        if known_p1_boards[i] == p1_board and known_p2_boards[i] == p2_board:
            if print_info:
                print(p1_board, p2_board, i)

            return known_best_moves[i]

    moves = find_all_moves(p1_board, p2_board, 1, x_tiles=x_tiles, y_tiles=y_tiles)

    move_scores = []
    highest_score = negative_infinity

    for move in moves:
        score = deep_eval(win, move[1], p2_board, search_depth, x_tiles=x_tiles, y_tiles=y_tiles, num_to_win=num_to_win)
        move_scores.append(score)

        if score > highest_score:
            highest_score = score

    if print_info:
        print('Evaluation: ' + str(highest_score))

    best_moves = []
    for i in range(len(move_scores)):
        if move_scores[i] == highest_score:
            best_moves.append(moves[i][0][0])

    if print_info:
        print("Move scores: " + str(move_scores))
        print('Best moves: ' + str(best_moves))

    try:
        random_num = random.randint(0, len(best_moves)-1)
    except ValueError:
        print('ERROR: No good moves')
        return 0

    if return_all_moves:
        return best_moves

    if return_eval:
        return best_moves[random_num], highest_score
    else:
        return best_moves[random_num]
