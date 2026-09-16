# import math
import random
import numpy as np
import tensorflow
import time
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras import layers
from sklearn.metrics import r2_score
from classical_ai import deep_eval as classical_deep_eval
from keras import backend as K
from keras.layers import Activation
from keras.utils import get_custom_objects
import pickle
from funcs import *
from random_ai import play_random_moves

start_time = time.time()

if __name__ == '__main__':
    print(f'\nPROGRAM STARTED\nTime:{start_time}')

# Creates variables for the paths of different files
MODEL_PATH = "ml_model/models/cnn4"
TRAINING_DATA_PATH = "ml_model/data/training_data.pickle"
RAW_DATA_PATH = "ml_model/data/ml_ai_raw_data.txt"
SAVEPOINT_PATH = 'ml_model/checkpoints/cnn_checkpoint1/checkpoint.ckpt'

# Creates a variable to check if the program is being run or imported
IN_MAIN = __name__ == '__main__'

new_data_to_generate = 20000

# Sets the learning rate (lr) to an adjustable variable
learning_rate = tensorflow.Variable(0.001, trainable=False)


def generate_new_boards(p1_board, p2_board, num_of_boards, min_moves=2, max_moves=20, x_tiles=7, y_tiles=6):
    boards = []

    for i in range(num_of_boards):
        moves_in_future = random.randint(min_moves, max_moves)

        new_board = play_random_moves(p1_board, p2_board, moves_in_future, x_tiles=x_tiles, y_tiles=y_tiles)
        boards.append(new_board)

    return boards


def create_new_model(verbose=1):
    # Creates the model architecture
    temp_model = Sequential()

    # temp_model.add(layers.ZeroPadding2D(padding=(1, 1)))
    temp_model.add(layers.Conv2D(8, (3, 3), activation='tanh', input_shape=(6, 7, 1)))
    temp_model.add(layers.MaxPooling2D((2, 2)))
    temp_model.add(layers.Conv2D(4, (2, 2), activation='tanh'))

    if verbose > 1:
        print("Convolutional model summery (half complete):", temp_model.summary())

    temp_model.add(layers.Flatten())
    temp_model.add(layers.Dense(4, activation='tanh'))
    temp_model.add(layers.Dense(2))

    if verbose > 0:
        print("Full model summary:\n", temp_model.summary())

    return temp_model


def train_model(model_instance, epochs, batch_size, lr, checkpoint_load_path=None, checkpoint_save_path=None,
                shuffle=True):
    tensorflow.keras.backend.set_value(learning_rate, lr)

    if checkpoint_load_path is not None:
        model_instance.load_weights(checkpoint_load_path)

    if checkpoint_save_path is not None:
        checkpoint = tensorflow.keras.callbacks.ModelCheckpoint(filepath=checkpoint_save_path, save_weights_only=True,
                                                                verbose=1)
        model_instance.fit(training_input, training_output, epochs=epochs, batch_size=batch_size,
                           callbacks=[checkpoint], shuffle=shuffle)
    else:
        model_instance.fit(training_input, training_output, epochs=epochs, batch_size=batch_size, shuffle=shuffle)


# Custom activation function for the model (similar to tanh but for higher values, and increases values slightly)
def extended_weighted_tanh(x):
    return K.tanh(x / 10) * 10


get_custom_objects().update({'extended_weighted_tanh': Activation(extended_weighted_tanh)})

# Attempts to load the training data
try:
    print('Attempting to load training data...')
    with open(TRAINING_DATA_PATH, "rb") as f:
        training_input, training_output = pickle.load(f)

    print('Training data loaded')
except FileNotFoundError:
    # If no training data exists, new data is created
    print('Training data not found\nCreating training data...')

    training_input = []
    training_output = []

    if new_data_to_generate > 0:
        print('Generating new data...')
        new_boards = generate_new_boards(0, 0, new_data_to_generate, min_moves=5, max_moves=42)

        with open(RAW_DATA_PATH, 'a') as f:
            for board in new_boards:
                f.write(f'\n{str(board[0])} {str(board[1])}')

        print('Data generated')

    empty_array = [0, 0]
    depth = 5

    eval_scalar = 0.01

    last_percent = -1

    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
        total_lines = len(f.readlines())

    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if round(i / total_lines * 1000) / 10 > last_percent:
                last_percent = round(i / total_lines * 1000) / 10
                print(f"Data created: {i} / {total_lines} ({last_percent}%)")

            parts = line.split(' ')
            p1_board = int(int(parts[0]))
            p2_board = int(parts[1])

            pos_eval = classical_deep_eval(None, p1_board, p2_board, depth)

            try:
                best_move = int(parts[2])
                pos_eval += 2
            except IndexError:
                pass

            pos_eval = np.clip(pos_eval, -100, 100)
            pos_eval *= eval_scalar
            output_data = empty_array.copy()
            output_data[0] = pos_eval

            reversed_pos_eval = classical_deep_eval(None, p2_board, p1_board, depth)

            try:
                best_move = int(parts[2])
                reversed_pos_eval += 2
            except IndexError:
                pass

            reversed_pos_eval = np.clip(reversed_pos_eval, -100, 100)
            reversed_pos_eval *= eval_scalar
            reversed_output_data = empty_array.copy()
            reversed_output_data[0] = reversed_pos_eval

            training_input.append(convert_board_to_input(p1_board, p2_board))
            training_input.append(convert_board_to_input(p2_board, p1_board))
            training_output.append(output_data)
            training_output.append(reversed_output_data)

    # Saves the new training data
    with open(TRAINING_DATA_PATH, "wb") as f:
        pickle.dump((training_input, training_output), f)

    print('Training data created')


# print(training_input[0])

# print(training_input, training_output)

# print('Training example 1: ' + str(training_input[1]))
# print('Training example 2: ' + str(training_input[2]))
# print('Training example 3: ' + str(training_input[5]))

print('Creating model...')

model = create_new_model()

model.compile(loss=tensorflow.keras.losses.MeanSquaredError(), optimizer='adam', metrics='accuracy')

print('Model created')

# Attempts to load a preexisting model
try:
    print('Attempting to load model...')
    model = load_model(MODEL_PATH)
    print('Model loaded')
except IOError:
    # If not such model exists, the model is trained
    print('Model save not found\nTraining model...')

    batch_size = 16

    """# First training: High lr, not many epochs; quickly gets the model to a rough but accurate state
    tensorflow.keras.backend.set_value(learning_rate, 1)
    model.fit(training_input, training_output, epochs=10, batch_size=32)

    # Lower lr: get a less rough state
    tensorflow.keras.backend.set_value(learning_rate, 0.1)
    model.fit(training_input, training_output, epochs=50, batch_size=batch_size)"""

    """# Even lower lr, start to increase the epochs
    train_model(model, 50, batch_size, 0.05, None, SAVEPOINT_PATH)

    # Lower lr, but more epochs: meant to get the model to its final stage
    train_model(model, 500, batch_size, 0.001, None, SAVEPOINT_PATH)

    # Lowest lr; used for very fine fine-tuning of the model
    train_model(model, 100, 4, 0.0001, None, SAVEPOINT_PATH)

    # LOWEST lr; used for very very very fine fine-tuning of the model
    train_model(model, 20, 4, 0.00001, None, SAVEPOINT_PATH)

    # LOWEST lr; used for very very very fine fine-tuning of the model
    train_model(model, 20, 2048, 0.00001, None, SAVEPOINT_PATH)"""

    # LOWEST lr; used for very very very fine fine-tuning of the model
    train_model(model, 10, 4, 0.00001, SAVEPOINT_PATH, SAVEPOINT_PATH)

    # Saves the model for future use
    model.save(MODEL_PATH)

    print('Model trained')


def extract_positions_from_arr(arr):
    extracted_arr = []

    if len(arr) > 0:
        for obj in arr:
            if type(obj) is list:
                new_arr = extract_positions_from_arr(obj)
                for new_obj in new_arr:
                    extracted_arr.append(new_obj)
            else:
                extracted_arr.append(obj)

    return extracted_arr


def evaluate_position(p1_board, p2_board, x_tiles=7, y_tiles=6, num_to_win=4, verbose=0):
    score_precision = 100

    p1_bin = bin(p1_board)[2:]
    p2_bin = bin(p2_board)[2:]

    if sum(list(map(int, p1_bin.strip()))) >= num_to_win and sum(list(map(int, p2_bin.strip()))) >= num_to_win:
        for i in range(x_tiles):
            for j in range(y_tiles):
                index = i * y_tiles + j

                if len(p1_bin) > index and p1_bin[::-1][index] == '1' and check_for_win(p1_board, i, j, x_tiles,
                                                                                        y_tiles, num_to_win):
                    return positive_infinity
                if len(p2_bin) > index and p2_bin[::-1][index] == '1' and check_for_win(p2_board, i, j, x_tiles,
                                                                                        y_tiles, num_to_win):
                    return negative_infinity

    if check_full_board(p1_board, p2_board, x_tiles=x_tiles, y_tiles=y_tiles):
        return 0

    board_arr = convert_board_to_input(p1_board, p2_board, x_tiles=x_tiles, y_tiles=y_tiles)

    prediction = model.predict([board_arr], verbose=verbose)[0][0]
    prediction = np.clip(prediction * 105, -100, 100)

    prediction = round(prediction * score_precision) / score_precision

    if prediction >= 100:
        prediction = positive_infinity
    elif prediction <= -100:
        prediction = negative_infinity

    return prediction


def find_best_move(p1_board, p2_board, x_tiles=7, y_tiles=6, verbose=0):
    all_moves = []

    for i in range(x_tiles):
        x_pos = i

        board = int(bin(p1_board | p2_board), 2)
        column = board >> (x_pos * y_tiles)
        column -= (column >> y_tiles) << y_tiles
        column = bin(column)

        highest_val = highest_bit_flipped(column)

        if highest_val < y_tiles:
            all_moves.append(i)

    board_arr = convert_board_to_input(p1_board, p2_board, x_tiles=x_tiles, y_tiles=y_tiles)

    move_evals = model.predict([board_arr], verbose=verbose)
    move_evals = move_evals[0][:-1]

    # print(move_evals)

    best_move = np.argmax(move_evals)

    while best_move not in all_moves:
        move_evals[best_move] = -math.inf
        best_move = np.argmax(move_evals)

    return best_move


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


def ai(p1_board, p2_board, x_tiles=7, y_tiles=6):
    positions = find_end_positions(p1_board, p2_board, 4, x_tiles=x_tiles, y_tiles=y_tiles)
    extracted_positions = extract_positions_from_arr(positions)
    print(extracted_positions)

    formatted_positions = []
    extra_positions = []
    indices = []

    for i, position in enumerate(extracted_positions):
        if type(position) is tuple:
            formatted_positions.append(convert_board_to_input(position[0], position[1], x_tiles=x_tiles, y_tiles=y_tiles))
        else:
            extra_positions.append(position)
            indices.append([i])

    print(formatted_positions)

    predictions = model.predict(formatted_positions)
    print(predictions)

    for i, pos in enumerate(extra_positions):
        np.insert(predictions, indices[i], pos)

    print(predictions)
    print(len(predictions))



    moves = find_all_moves(p1_board, p2_board, 1, x_tiles=x_tiles, y_tiles=y_tiles)

    move_scores = []
    highest_score = negative_infinity

    for move in moves:
        score = deep_eval(None, move[1], p2_board, 1, x_tiles=x_tiles, y_tiles=y_tiles)
        move_scores.append(score)

        if score > highest_score:
            highest_score = score

    best_moves = []
    for i in range(len(move_scores)):
        if move_scores[i] == highest_score:
            best_moves.append(moves[i][0][0])

    try:
        random_num = random.randint(0, len(best_moves)-1)
    except ValueError:
        print('ERROR: No good moves')
        return 0

    return best_moves[random_num]


if IN_MAIN:
    print('Testing model...')

    test_num = min(len(training_output) + 1, 100000000)

    # Creates a variable 'preds' for all the model predictions up to the variable 'test_num'
    preds = model.predict(training_input[:test_num])
    # print(preds)
    preds = [val for val in preds]

    # print(preds, training_output[:test_num])

    # Tests model on various training data, showing predicted and actual results
    print(f'Model prediction: {preds[0]}     True answer: {training_output[0]}')
    print(f'Model prediction: {model.predict([training_input[0]], verbose=0)}     True answer: {training_output[0]}')
    print(f'Model prediction: {preds[5]}     True answer: {training_output[5]}')
    print(f'Model prediction: {preds[23]}     True answer: {training_output[23]}')
    print(f'Model prediction: {preds[42]}     True answer: {training_output[42]}')
    print(f'Model prediction: {preds[1]}     True answer: {training_output[1]}')
    print(f'Model prediction: {preds[len(preds)-1]}     True answer: '
          f'{training_output[len(preds)-1]}')

    # Finds the model accuracy with sklearn.r2_score
    accuracy = r2_score(training_output[:test_num], preds)
    print(f'Model accuracy: {accuracy}')

    print('Testing finished')

    print(f'\nPROGRAM ENDED\nTime: {time.time()}\nDuration: {round((time.time() - start_time) * 1000) / 1000}s')
