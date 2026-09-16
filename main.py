# import math
import time
# import pygame
from ui_elements import Text, Button
from classical_ai import ai
from ml_ai import evaluate_position as ml_evaluate_position, ai as learning_ai
from random_ai import ai as randomized_ai
from funcs import *
import numpy as np

pygame.init()


print("PROGRAM STARTED\n")
# WIDTH/HEIGHT = size of the window, BOARD_(WIDTH/HEIGHT) = size of the connect 4 board
WIDTH = 1400
HEIGHT = 600
BOARD_WIDTH = 700
BOARD_HEIGHT = 600

# Defines colours for the background, the chess squares, and the highlight colour for legal moves
bg_colour = (255, 255, 255)
board_colour = (40, 60, 240)
player_1_colour = (250, 10, 40)
player_2_colour = (240, 250, 80)
empty = (0, 0, 0, 0)

# 'win': Screen to which everything is drawn, 'surface': transparent layer for highlights
win = pygame.display.set_mode((WIDTH, HEIGHT))
surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
clock = pygame.time.Clock()
pygame.display.set_caption("Connect 4")

basic_font = pygame.font.SysFont('roboto', int((BOARD_WIDTH + BOARD_HEIGHT) / 50), True)

x_tiles = 7
y_tiles = 6
num_to_win = 4

is_left_clicking = False

is_in_game = False
is_in_menu = True
is_editing_weights = False
game_is_over = False
game_is_drawn = True
p1_won = False
p2_won = False
p1_to_move = True
p1_moves = 0
p2_moves = 0
opponent = ''

ml_pos_eval = 0

ai_depth = 5

streak_start_tile = [-1, -1]
streak_end_tile = [-1, -1]

moves_list = [p1_moves, p2_moves]

weights_matrix = []
for _ in range((x_tiles * y_tiles) - len(weights_matrix)):
    weights_matrix.append(0)

menu_buttons = [
    Button(WIDTH / 9 * 1.5, HEIGHT / 2 + HEIGHT / 10, WIDTH / 5, HEIGHT / 6, code='playhuman',
           text="PLAY AGAINST HUMAN", font_size=WIDTH / 60),
    Button(WIDTH / 9 * 3.5, HEIGHT / 2 + HEIGHT / 10, WIDTH / 5, HEIGHT / 6, code='playbot1',
           text="PLAY AGAINST BOT 1", font_size=WIDTH / 60),
    Button(WIDTH / 9 * 5.5, HEIGHT / 2 + HEIGHT / 10, WIDTH / 5, HEIGHT / 6, code='playbot2',
           text="PLAY AGAINST BOT 2", font_size=WIDTH / 60),
    Button(WIDTH / 9 * 7.5, HEIGHT / 2 + HEIGHT / 10, WIDTH / 5, HEIGHT / 6, code='playbot3',
           text="PLAY AGAINST BOT 3", font_size=WIDTH / 60),
    Button(WIDTH / 2, HEIGHT / 2 + HEIGHT / 3, WIDTH / 8, HEIGHT / 12, code='weights',
           text="WEIGHTS", font_size=WIDTH / 100)
]
menu_texts = [
    Text(WIDTH / 2, HEIGHT / 3.5, font_size=WIDTH / 8, text='Connect 4')
]

game_button_width = (WIDTH - BOARD_WIDTH) / 2.5
game_buttons = [
    Button(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 - game_button_width / 1.8, 5 + (HEIGHT / 8) / 2, game_button_width,
           HEIGHT / 8, code='reset', text="RESET GAME", font_size=WIDTH / 50),
    Button(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 - game_button_width / 1.8, 5 + (HEIGHT / 8) / 2 + HEIGHT / 8 + 10,
           game_button_width, HEIGHT / 8, code='quit', text="QUIT GAME", font_size=WIDTH / 50),
    Button(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 - game_button_width / 1.8, 5 + (HEIGHT / 8) / 2 + 2 *
           (HEIGHT / 8 + 10), game_button_width, HEIGHT / 8, code='menu', text="MAIN MENU", font_size=WIDTH / 50),
    Button(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 - game_button_width / 1.8, 5 + (HEIGHT / 8) / 2 + 3 *
           (HEIGHT / 8 + 10), game_button_width, HEIGHT / 8, code='undo1', text="UNDO MOVE", font_size=WIDTH / 50),
    Button(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 - game_button_width / 1.8, 5 +
           (HEIGHT / 8) / 2 + 4 * (HEIGHT / 8 + 10), game_button_width, HEIGHT / 8, code='undo2', text="UNDO 2 MOVES",
           font_size=WIDTH / 50),
    Button(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 - game_button_width / 1.8, 5 +
           (HEIGHT / 8) / 2 + 5 * (HEIGHT / 8 + 10), game_button_width, HEIGHT / 8, code='resetvars',
           text="RESET VARIABLES", font_size=WIDTH / 50),
    Button(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 - game_button_width / 1.8, 5 +
           (HEIGHT / 8) / 2 + 6 * (HEIGHT / 8 + 10), game_button_width, HEIGHT / 8, code='skip', text="SKIP TURN",
           font_size=WIDTH / 50),
    Button(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 + game_button_width / 1.8, 5 +
           (HEIGHT / 8) / 2, game_button_width, HEIGHT / 8, code='gameover', text="WIN GAME", font_size=WIDTH / 50),
    Button(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 + game_button_width / 1.8, 5 +
           (HEIGHT / 8) / 2 + HEIGHT / 8 + 10, game_button_width, HEIGHT / 8, code='printboard', text="PRINT BOARD",
           font_size=WIDTH / 50),
    Button(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 + game_button_width / 1.8, 5 +
           (HEIGHT / 8) / 2 + 2 * (HEIGHT / 8 + 10), game_button_width, HEIGHT / 8, code='printweights',
           text="PRINT WEIGHTS", font_size=WIDTH / 50),
    Button(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 + game_button_width / 1.8, 5 +
           (HEIGHT / 8) / 2 + 3 * (HEIGHT / 8 + 10), game_button_width, HEIGHT / 8, code='resetweights',
           text="RESET WEIGHTS", font_size=WIDTH / 50),
    Button(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 + game_button_width / 1.8, 5 +
           (HEIGHT / 8) / 2 + 4 * (HEIGHT / 8 + 10), game_button_width, HEIGHT / 8, code='bestmove',
           text="FIND BEST MOVE", font_size=WIDTH / 50)
]
game_texts = [
    Text(BOARD_WIDTH + (WIDTH - BOARD_WIDTH) / 2 + game_button_width / 1.8, 5 +
           (HEIGHT / 8) / 2 + 5 * (HEIGHT / 8 + 10), font_size=WIDTH / 32, text="", code='mleval')
]

game_over_buttons = [

]
game_over_texts = [
    Text(BOARD_WIDTH / 2, HEIGHT / 6, font_size=WIDTH / 16, text="", code='winner')
]


def check_for_win_v1(board_state, x, y, return_streak=False):
    tile_dist_from_end = x * y_tiles + y
    directions = [[0, 1], [1, 0], [1, 1], [1, -1], [0, -1], [-1, 0], [-1, -1], [-1, 1]]
    scores = [0, 0, 0, 0, 0, 0, 0, 0]
    tile_has_piece = False

    if bin(board_state >> tile_dist_from_end)[-1] == '1':
        tile_has_piece = True

    temp_board = []
    for i in range(y_tiles):
        temp_board.append([])
        for j in range(x_tiles):
            temp_board[i].append(0)

    for i, char in enumerate(bin(board_state)[2:][::-1]):
        temp_board[i % y_tiles][math.floor(i / y_tiles)] = int(char)

    for j, direction in enumerate(directions):
        for i in range(1, num_to_win+1):
            x_to_check = x + direction[0] * i
            y_to_check = (y + direction[1] * i)

            if 0 <= x_to_check < x_tiles and 0 <= y_to_check < y_tiles:
                if temp_board[y_to_check][x_to_check] == 0:
                    break

                scores[j] += temp_board[y_to_check][x_to_check]

                if tile_has_piece and scores[j] + scores[int((j + len(directions) / 2) % len(directions))] >=\
                        num_to_win - 1:
                    if return_streak:
                        streak_start = [x + direction[0] * scores[j], y + direction[1] * scores[j]]
                        streak_end = [streak_start[0] - direction[0] * (num_to_win - 1), streak_start[1] - direction[1]
                                      * (num_to_win - 1)]

                        return True, streak_start, streak_end

                    return True
                elif scores[j] >= num_to_win:
                    if return_streak:
                        streak_start = [x, y]
                        streak_end = [x + direction[0] * num_to_win, y + direction[1] * num_to_win]

                        return True, streak_start, streak_end

                    return True

    return False


def check_for_win(board_state, x, y, return_streak=False):
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

                if max(abs(x - x_to_check), abs(y - y_to_check)) == i and (x != x_to_check or y != y_to_check) and\
                        bin(board_state >> index_to_check)[-1] == '1' and (abs_x_dir == 1 or abs_x_dir == 0) and\
                        (abs_y_dir == 1 or abs_y_dir == 0):
                    scores[j] += 1

                    if tile_has_piece and scores[j] + scores[int((j + len(directions) / 2) % len(directions))] >=\
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


def print_board_state(p1_board=p1_moves, p2_board=p2_moves):
    print('Player 1 board position: ' + str(p1_board) + '   Player 2 board position: ' + str(p2_board))


def print_weights(weights=None):
    if weights is None:
        weights = weights_matrix

    print(weights)


running = True
while running:
    # print(evaluate_position(p1_moves, p2_moves)
    # evaluate_position(p1_moves, p2_moves)

    key = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    if not p1_to_move and opponent == 'bot1' and not game_is_over:
        old_p2 = p2_moves

        start_time = time.time()
        print("\nCalculating best move...")

        x_pos = ai(win, p2_moves, p1_moves, ai_depth, x_tiles=x_tiles, y_tiles=y_tiles, num_to_win=num_to_win)
        end_time = time.time()

        print("Time took AI to make move: " + str(round((end_time - start_time) * 1000) / 1000) + "s")

        board = int(bin(p1_moves | p2_moves), 2)
        column = board >> (x_pos * y_tiles)
        column -= (column >> y_tiles) << y_tiles
        column = bin(column)

        highest_val = highest_bit_flipped(column)

        y_pos = highest_val

        inserted_value = 1 << y_pos
        inserted_value <<= x_pos * y_tiles

        p2_moves |= inserted_value

        moves_list.append(p2_moves)

        p1_to_move = not p1_to_move

        if check_for_win(p2_moves, x_pos, y_pos):
            game_is_over = True
            p2_won = True
            print('Bot won!')

            _, streak_start_tile, streak_end_tile = check_for_win(p2_moves, x_pos, y_pos, return_streak=True)

        ml_pos_eval = np.clip(ml_evaluate_position(p1_moves, p2_moves), -100, 100)
    elif not p1_to_move and opponent == 'bot2' and not game_is_over:
        old_p2 = p2_moves

        start_time = time.time()
        print("\nCalculating best move...")

        x_pos = learning_ai(p2_moves, p1_moves, x_tiles=x_tiles, y_tiles=y_tiles)
        end_time = time.time()

        print("Time took AI to make move: " + str(round((end_time - start_time) * 1000) / 1000) + "s")

        board = int(bin(p1_moves | p2_moves), 2)
        column = board >> (x_pos * y_tiles)
        column -= (column >> y_tiles) << y_tiles
        column = bin(column)

        highest_val = highest_bit_flipped(column)

        y_pos = highest_val

        inserted_value = 1 << y_pos
        inserted_value <<= x_pos * y_tiles

        p2_moves |= inserted_value

        moves_list.append(p2_moves)

        p1_to_move = not p1_to_move

        if check_for_win(p2_moves, x_pos, y_pos):
            game_is_over = True
            p2_won = True
            print('Bot won!')

            _, streak_start_tile, streak_end_tile = check_for_win(p2_moves, x_pos, y_pos, return_streak=True)

        ml_pos_eval = np.clip(ml_evaluate_position(p1_moves, p2_moves), -100, 100)
    elif not p1_to_move and opponent == 'bot3' and not game_is_over:
        old_p2 = p2_moves

        start_time = time.time()
        print("\nCalculating best move...")

        x_pos = randomized_ai(p2_moves, p1_moves, x_tiles=x_tiles, y_tiles=y_tiles)
        end_time = time.time()

        print("Time took AI to make move: " + str(round((end_time - start_time) * 1000) / 1000) + "s")

        board = int(bin(p1_moves | p2_moves), 2)
        column = board >> (x_pos * y_tiles)
        column -= (column >> y_tiles) << y_tiles
        column = bin(column)

        highest_val = highest_bit_flipped(column)

        y_pos = highest_val

        inserted_value = 1 << y_pos
        inserted_value <<= x_pos * y_tiles

        p2_moves |= inserted_value

        moves_list.append(p2_moves)

        p1_to_move = not p1_to_move

        if check_for_win(p2_moves, x_pos, y_pos):
            game_is_over = True
            p2_won = True
            print('Bot won!')

            _, streak_start_tile, streak_end_tile = check_for_win(p2_moves, x_pos, y_pos, return_streak=True)

        ml_pos_eval = np.clip(ml_evaluate_position(p1_moves, p2_moves), -100, 100)

    visible_buttons = []
    visible_texts = []

    if is_in_game or is_editing_weights:
        visible_buttons += game_buttons
        visible_texts += game_texts
        if game_is_over:
            visible_buttons += game_over_buttons
            visible_texts += game_over_texts
    elif is_in_menu:
        visible_buttons += menu_buttons
        visible_texts += menu_texts

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_left_clicking = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                is_left_clicking = True

                if is_in_game and not game_is_over:
                    if 0 <= mouse_pos[0] <= BOARD_WIDTH and 0 <= mouse_pos[1] <= BOARD_HEIGHT:
                        if p1_to_move or opponent == 'human':
                            x_pos = math.floor(mouse_pos[0] / BOARD_WIDTH * x_tiles)

                            board = int(bin(p1_moves | p2_moves), 2)
                            column = board >> (x_pos * y_tiles)
                            column -= (column >> y_tiles) << y_tiles
                            column = bin(column)

                            highest_val = highest_bit_flipped(column)

                            if highest_val < y_tiles:
                                y_pos = highest_val

                                inserted_value = 1 << y_pos
                                inserted_value <<= x_pos * y_tiles

                                if p1_to_move:
                                    p1_moves |= inserted_value
                                    moves_list.append(p1_moves)
                                else:
                                    p2_moves |= inserted_value
                                    moves_list.append(p2_moves)

                                # print(find_end_positions(p2_moves, p1_moves, 2))

                                p1_to_move = not p1_to_move

                                p1_won = check_for_win(p1_moves, x_pos, y_pos)
                                p2_won = check_for_win(p2_moves, x_pos, y_pos)

                                if p1_won or p2_won:
                                    game_is_over = True

                                    winner = "Player 1" if p1_won else "Player 2"
                                    print(winner + ' won!')

                                    moves_to_check = p1_moves if p1_won else p2_moves

                                    _, streak_start_tile, streak_end_tile = check_for_win(moves_to_check, x_pos, y_pos,
                                                                                          return_streak=True)

                                ml_pos_eval = np.clip(ml_evaluate_position(p1_moves, p2_moves), -100, 100)

                elif is_editing_weights:
                    if 0 <= mouse_pos[0] <= BOARD_WIDTH and 0 <= mouse_pos[1] <= BOARD_HEIGHT:
                        x_pos = math.floor(mouse_pos[0] / BOARD_WIDTH * x_tiles)
                        y_pos = math.floor((BOARD_HEIGHT - mouse_pos[1]) / BOARD_HEIGHT * y_tiles)

                        weights_matrix[x_pos * y_tiles + y_pos] += 1

                for button in visible_buttons:
                    if button.x < mouse_pos[0] <= button.x + button.w:
                        if button.y < mouse_pos[1] <= button.y + button.h:
                            button_code = button.code

                            if 'play' in button_code:
                                print('Started game!')

                                is_in_game = True
                                is_in_menu = False

                                if button_code == 'playbot1':
                                    opponent = 'bot1'
                                elif button_code == 'playbot2':
                                    opponent = 'bot2'
                                elif button_code == 'playbot3':
                                    opponent = 'bot3'
                                elif button_code == 'playhuman':
                                    opponent = 'human'
                                else:
                                    print('ERROR: Button code is ' + button_code + ' which has the word play')
                            else:
                                if button_code == 'quit':
                                    running = False
                                elif button_code == 'reset':
                                    p1_moves = 0
                                    p2_moves = 0
                                    ml_pos_eval = 0
                                    p1_to_move = True
                                    game_is_over = False
                                    game_is_drawn = False
                                    p1_won = False
                                    p2_won = False
                                    streak_start_tile = [-1, -1]
                                    streak_end_tile = [-1, -1]
                                    moves_list = [p1_moves, p2_moves]
                                elif button_code == 'resetvars':
                                    game_is_over = False
                                    game_is_drawn = False
                                    p1_won = False
                                    p2_won = False
                                    streak_start_tile = [-1, -1]
                                    streak_end_tile = [-1, -1]
                                elif button_code == 'menu':
                                    p1_moves = 0
                                    p2_moves = 0
                                    ml_pos_eval = 0
                                    p1_to_move = True
                                    game_is_over = False
                                    game_is_drawn = False
                                    p1_won = False
                                    p2_won = False
                                    streak_start_tile = [-1, -1]
                                    streak_end_tile = [-1, -1]
                                    moves_list = [p1_moves, p2_moves]

                                    is_in_game = False
                                    is_in_menu = True
                                elif button_code == 'undo1':
                                    if len(moves_list) >= 3:
                                        if p1_to_move:
                                            p2_moves = moves_list[-3]
                                        else:
                                            p1_moves = moves_list[-3]

                                        p1_to_move = not p1_to_move
                                        del moves_list[-1]

                                        ml_pos_eval = np.clip(ml_evaluate_position(p1_moves, p2_moves), -100, 100)
                                elif button_code == 'undo2':
                                    if len(moves_list) >= 4:
                                        if p1_to_move:
                                            p2_moves = moves_list[-3]
                                            p1_moves = moves_list[-4]
                                        else:
                                            p1_moves = moves_list[-3]
                                            p2_moves = moves_list[-4]

                                        moves_list = moves_list[:-2]

                                        ml_pos_eval = np.clip(ml_evaluate_position(p1_moves, p2_moves), -100, 100)
                                elif button_code == 'skip':
                                    p1_to_move = not p1_to_move
                                elif button_code == 'gameover':
                                    game_is_over = True
                                elif button_code == 'printboard':
                                    print_board_state(p1_moves, p2_moves)
                                elif button_code == 'weights':
                                    is_in_menu = False
                                    is_editing_weights = True
                                elif button_code == 'printweights':
                                    print_weights(weights_matrix)
                                elif button_code == 'resetweights':
                                    weights_matrix = []

                                    for _ in range(x_tiles * y_tiles):
                                        weights_matrix.append(0)
                                elif button_code == 'bestmove':
                                    best_move = ai(win, p2_moves, p1_moves, ai_depth, x_tiles=x_tiles, y_tiles=y_tiles,
                                                   num_to_win=num_to_win, return_all_moves=True)

                                    print(f'Best move(s): {best_move}')

            elif event.button == 3:
                if is_editing_weights:
                    if 0 <= mouse_pos[0] <= BOARD_WIDTH and 0 <= mouse_pos[1] <= BOARD_HEIGHT:
                        x_pos = math.floor(mouse_pos[0] / BOARD_WIDTH * x_tiles)
                        y_pos = math.floor((BOARD_HEIGHT - mouse_pos[1]) / BOARD_HEIGHT * y_tiles)

                        weights_matrix[x_pos * y_tiles + y_pos] -= 1

    if not game_is_over:
        full_board = p1_moves | p2_moves
        board_full = False

        if full_board == 2 ** (x_tiles * y_tiles) - 1:
            board_full = True

        if board_full:
            game_is_over = True
            game_is_drawn = True

            print("It's a draw!")

    win.fill(bg_colour)

    if is_left_clicking:
        pass

    if is_in_game or is_editing_weights:
        draw_board(win, p1_moves, p2_moves, BOARD_WIDTH, BOARD_HEIGHT, x_tiles, y_tiles, board_colour, bg_colour,
                   player_1_colour, player_2_colour, start_streak=streak_start_tile, end_streak=streak_end_tile,
                   draw_pieces=is_in_game)

    for button in visible_buttons:
        button.draw(win, mouse_pos, is_left_clicking)

    for text in visible_texts:
        text_code = text.code
        if text_code == 'winner':
            text.text = 'Player 1 won!' if p1_won else ('Player 2 won!' if p2_won else "It's a draw!")
        elif text_code == 'mleval':
            text.text = str(f"ML Eval: {round(ml_pos_eval * 100) / 100}")

        text.draw(win)

    if is_editing_weights:
        for i, num in enumerate(weights_matrix):
            x_pos = (math.floor(i / y_tiles)) * (BOARD_WIDTH / x_tiles) + (BOARD_WIDTH / x_tiles) / 2
            y_pos = (y_tiles - (i % y_tiles) - 1) * (BOARD_HEIGHT / y_tiles) + (BOARD_HEIGHT / y_tiles) / 2

            text = basic_font.render(str(num), True, (0, 0, 0))
            win.blit(text, (x_pos - text.get_width() / 2, y_pos - text.get_height() / 2))

    win.blit(surface, (0, 0))
    pygame.display.update()

print("\nPROGRAM ENDED")
