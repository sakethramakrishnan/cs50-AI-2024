"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def count_in_list_of_lists(list_of_lists, obj):
    counter = 0
    for list_0 in list_of_lists:
        for item in list_0:
            if item == obj:
                counter += 1

    return counter


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    num_x = count_in_list_of_lists(board, X)

    num_o = count_in_list_of_lists(board, O)

    if num_x == num_o:
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_moves = set()

    for i, list_0 in enumerate(board):
        for j, item in enumerate(list_0):
            if item == EMPTY:
                possible_moves.add((i, j))

    return possible_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    current_player = player(board)
    i, j = action

    if i < 0 or i > 2 or j < 0 or j > 2:
        raise ValueError(f"({i}, {j}) is not a valid move")

    place = board[i][j]

    if place != EMPTY:
        raise ValueError(f"({i}, {j}) is not a valid move")

    board_copy = copy.deepcopy(board)
    board_copy[i][j] = current_player

    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    # """
    for player in (X, O):
        # column:
        for row in board:
            if row == [player] * 3:
                return player
        # row:
        for i in range(3):
            column = [board[x][i] for x in range(3)]
            if column == [player] * 3:
                return player

        # diagonal:
        if [board[i][i] for i in range(0, 3)] == [player] * 3:
            return player

        elif [board[i][~i] for i in range(0, 3)] == [player] * 3:
            return player

    return None


def is_tie(board):
    count_empty = 9
    for i in board:
        for j in i:
            if j != EMPTY:
                count_empty -= 1
    return count_empty == 0


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) or is_tie(board):
        return True

    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board) == True:
        return None

    else:
        if player(board) == X:

            value, move = get_min_board_state(board)
            return move
        else:
            value, move = get_max_board_state(board)
            return move


def get_max_board_state(board):
    """
    Returns the maximum value of a board and the best associated move
    """
    if terminal(board) == True:
        return utility(board), 'returned Max'

    v = -10000000000000000000000000000000000
    move = None
    for action in actions(board):
        # remember, we are trying to see what the other player would do
        # it's greedy
        # and play to that response

        min_val, min_action = get_min_board_state(result(board, action))

        if min_val > v:
            v = min_val
            move = min_action

            return v, move


def get_min_board_state(board):
    """
    Returns the minimum value of a board and the best associated move
    """
    if terminal(board) == True:
        return utility(board), 'returned min'

    v = 1000000000000000000000000000
    move = None
    for action in actions(board):
        # remember, we are trying to see what the other player would do
        # it's greedy
        # and play to that response

        min_val, min_action = get_max_board_state(result(board, action))

        if min_val < v:
            v = min_val
            move = min_action

            # if v == -1:
            return v, move

    # return v, move
