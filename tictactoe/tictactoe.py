"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None
N = 3
debugmode = False
minsteps = 0
maxsteps = 0


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
    Xs = sum([sum([1 if x=="X" else 0 for x in row]) for row in board])
    Os = sum([sum([1 if x=="O" else 0 for x in row]) for row in board])
    if Xs == Os:
        return X
    if Xs == Os+1:
        return O
    print(f'X={Xs}, O={Os}')
    raise Exception("Incorrect count of X's and O's")


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    acts = set()
    for i in range(N):
        for j in range(N):
            if board[i][j] == EMPTY:
                acts.add((i,j))
    return acts


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i,j = action
    if i<0 or j<0 or i>=N or j>=N:
        raise Exception("Out of boundary move")
    if board[i][j] != EMPTY:
        raise Exception("Cannot make move")
    # bcopy = copy.deepcopy(board)
    # bcopy[i][j] = player(board)
    # return bcopy
    board[i][j] = player(board)
    return board
    

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #transposeboard = list(zip(*board))
    for i in range(N):
        ##check by row
        if sum([1 if x=="X" else 0 for x in board[i]]) == N:
            return X 
        if sum([1 if x=="O" else 0 for x in board[i]]) == N:
            return O
        ##check by column
        if sum([1 if row[i]=="X" else 0 for row in board]) == N:
            return X
        if sum([1 if row[i]=="O" else 0 for row in board]) == N:
            return O
    ##check by diagonal
    if sum([1 if board[i][i]=="X" else 0 for i in range(N)]) == N:
        return X
    if sum([1 if board[i][i]=="O" else 0 for i in range(N)]) == N:
        return O
    if sum([1 if board[i][N-1-i]=="X" else 0 for i in range(N)]) == N:
        return X
    if sum([1 if board[i][N-1-i]=="O" else 0 for i in range(N)]) == N:
        return O
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    if sum([sum([1 if x == EMPTY else 0 for x in row]) for row in board]) == 0:
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


def minmaxvalue(board, alpha, beta, Xisplaying):
    """
    Returns the min/max value of the new states from all possible actions
    When using alpha beta pruning, alpha and beta are up to date the optimal value for the max and min player
    alpha is updated to the maximize, beta is updated to minimize
    alpha, beta are initially set to be -Inf, +Inf
    """
    global minsteps, maxsteps
    if terminal(board):
        if debugmode:
            print('current board is\n')
            for i in range(N):
                print('|'.join([x or '' for x in board[i]]))
                print('\n')
            print(f'terminal node, value={utility(board)}, alpha={alpha}, beta={beta}\n')
            print(f'maxsteps={maxsteps}, minsteps={minsteps}\n')
            input('press return to continue')
        return utility(board)
    if debugmode:
        print(f'alpha={alpha},beta={beta}, {X if Xisplaying else O} is playing\n')
        print('current board is\n')
        for i in range(N):
            print('|'.join([x or '' for x in board[i]]))
            print('\n')
        print(f'Possible actions for {X if Xisplaying else O} are {actions(board)}\n')
        print(f'maxsteps={maxsteps}, minsteps={minsteps}\n')
        input('press return to continue')
    bestmove = None
    if Xisplaying:
        maxsteps += 1
        v = float('-inf')
        for (i,j) in actions(board):
            board[i][j] = X
            vnew = minmaxvalue(board, alpha, beta, False)
            board[i][j] = EMPTY
            alpha = max(alpha, vnew)
            if debugmode:
                print(f'candidate position for X={(i,j)}, vnew={vnew}, v={v}, alpha={alpha}, beta={beta}\n')
                input('press return to continue')
            if vnew > v:
                v = vnew
                bestmove = (i,j)
            if beta <= alpha:
                break
            if v==1:
                break
    else:
        minsteps += 1
        v = float('inf')
        for (i,j) in actions(board):
            board[i][j] = O
            vnew = minmaxvalue(board, alpha, beta, True)
            board[i][j] = EMPTY
            beta = min(beta, vnew)
            if debugmode:
                print(f'candidate position for O={(i,j)}, vnew={vnew}, v={v}, alpha={alpha}, beta={beta}\n')
                input('press return to continue')
            if vnew < v:
                v = vnew
                bestmove = (i,j)
            if beta <= alpha:
                break
            if v==-1:
                break
    return v


def minimax_old(board):
    """
    Returns the optimal action for the current player on the board.
    """
    global minsteps, maxsteps
    minsteps, maxsteps = 0, 0 ## count how many times minmaxvalue function is called
    if terminal(board):
        return None
    p = player(board)
    bestmove = None
    if p == X: ## X wants to maximize
        maxsteps += 1
        v = float('-inf')
        for (i,j) in actions(board):
            board[i][j] = X
            vnew = minmaxvalue(board, float('-inf'), float('inf'), False)
            board[i][j] = EMPTY
            if vnew > v:
                v = vnew
                bestmove = (i,j)
    else: ## O wants to minimize
        minsteps += 1
        v = float('inf')
        for (i,j) in actions(board):
            board[i][j] = O
            vnew = minmaxvalue(board, float('-inf'), float('inf'), True)
            board[i][j] = EMPTY
            if vnew < v:
                v = vnew
                bestmove = (i,j)
    print(f'minmaxvalue is called {minsteps} and {maxsteps} times\n')
    return bestmove



def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    global minsteps,maxsteps
    minsteps, maxsteps = 0,0 ## count how many times minmaxvalue function is called
    if terminal(board):
        return None
    p = player(board)
    bestmove = None
    if p == X: ## X wants to maximize
        v, bestmove = max_value(board, float('-inf'), float('inf'))
    else:
        v, bestmove = min_value(board, float('-inf'), float('inf'))
    
    print(f'minmaxvalue is called {minsteps} and {maxsteps} times\n')
    return bestmove


def max_value(board, alpha, beta):
    """
    Returns the min/max value of the new states from all possible actions
    When using alpha beta pruning, alpha and beta are up to date the optimal value for the max and min player
    alpha is updated to the maximize, beta is updated to minimize
    alpha, beta are initially set to be -Inf, +Inf
    """
    global maxsteps
    if terminal(board):
        if debugmode:
            print('current board is\n')
            for i in range(N):
                print('|'.join([x or '' for x in board[i]]))
                print('\n')
            print(f'terminal node, value={utility(board)}, alpha={alpha}, beta={beta}\n')
            input('press return to continue')
        return utility(board), None
    maxsteps += 1
    if debugmode:
        print(f'alpha={alpha},beta={beta}, X is playing\n')
        print('current board is\n')
        for i in range(N):
            print('|'.join([x or '' for x in board[i]]))
            print('\n')
        print(f'Possible actions for X are {actions(board)}\n')
        input('press return to continue')
    bestmove = None
    v = float('-inf')
    for (i,j) in actions(board):
        board[i][j] = X
        vnew, move = min_value(board, alpha, beta)
        board[i][j] = EMPTY
        alpha = max(alpha, vnew)
        if debugmode:
            print(f'candidate position for X={(i,j)}, vnew={vnew}, v={v}, alpha={alpha}, beta={beta}\n')
            input('press return to continue')
        if vnew > v:
            v = vnew
            bestmove = (i,j)
        if beta <= alpha:
            break
        if v==1:
            break
    return v, bestmove


def min_value(board, alpha, beta):
    """
    Returns the min/max value of the new states from all possible actions
    When using alpha beta pruning, alpha and beta are up to date the optimal value for the max and min player
    alpha is updated to the maximize, beta is updated to minimize
    alpha, beta are initially set to be -Inf, +Inf
    """
    global minsteps
    if terminal(board):
        if debugmode:
            print('current board is\n')
            for i in range(N):
                print('|'.join([x or '' for x in board[i]]))
                print('\n')
            print(f'terminal node, value={utility(board)}, alpha={alpha}, beta={beta}\n')
            input('press return to continue')
        return utility(board), None
    minsteps += 1
    if debugmode:
        print(f'alpha={alpha},beta={beta}, O is playing\n')
        print('current board is\n')
        for i in range(N):
            print('|'.join([x or '' for x in board[i]]))
            print('\n')
        print(f'Possible actions for O are {actions(board)}\n')
        input('press return to continue')
    bestmove = None
    v = float('inf')
    for (i,j) in actions(board):
        board[i][j] = O
        vnew, move = max_value(board, alpha, beta)
        board[i][j] = EMPTY
        beta = min(beta, vnew)
        if debugmode:
            print(f'candidate position for O={(i,j)}, vnew={vnew}, v={v}, alpha={alpha}, beta={beta}\n')
            input('press return to continue')
        if vnew < v:
            v = vnew
            bestmove = (i,j)
        if v==-1:
            break
        if beta <= alpha:
            break
    return v, bestmove
