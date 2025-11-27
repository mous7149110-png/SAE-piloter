import random

EMPTY = " "
HUMAN = "X"
BOT = "O"

def create_board():
    return [EMPTY] * 9

def print_board(board):
    print("\n")
    for i in range(3):
        row = board[3*i:3*i+3]
        print(" | ".join(cell if cell != EMPTY else str(3*i + j + 1) for j, cell in enumerate(row)))
        if i < 2:
            print("--+---+--")
    print("\n")

def check_winner(board):
    wins = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in wins:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    if EMPTY not in board:
        return "draw"
    return None

def human_move(board):
    while True:
        try:
            choice = int(input("Choisis une case (1-9) : ")) - 1
            if choice < 0 or choice > 8:
                print("Choix invalide.")
            elif board[choice] != EMPTY:
                print("Case déjà prise.")
            else:
                board[choice] = HUMAN
                break
        except ValueError:
            print("Entre un nombre entre 1 et 9.")

def available_moves(board):
    return [i for i, v in enumerate(board) if v == EMPTY]

# Niveau facile : totalement aléatoire
def bot_move_easy(board):
    pos = random.choice(available_moves(board))
    board[pos] = BOT

# Niveau moyen : tente de gagner ou bloquer, sinon aléatoire
def bot_move_medium(board):
    # 1) Gagner si possible
    for pos in available_moves(board):
        copy = board[:]
        copy[pos] = BOT
        if check_winner(copy) == BOT:
            board[pos] = BOT
            return
    # 2) Bloquer humain
    for pos in available_moves(board):
        copy = board[:]
        copy[pos] = HUMAN
        if check_winner(copy) == HUMAN:
            board[pos] = BOT
            return
    # 3) Sinon aléatoire
    bot_move_easy(board)

# Niveau difficile : Minimax
def minimax(board, is_maximizing):
    result = check_winner(board)
    if result == BOT:
        return 1
    elif result == HUMAN:
        return -1
    elif result == "draw":
        return 0

    if is_maximizing:
        best_score = -999
        for pos in available_moves(board):
            board[pos] = BOT
            score = minimax(board, False)
            board[pos] = EMPTY
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = 999
        for pos in available_moves(board):
            board[pos] = HUMAN
            score = minimax(board, True)
            board[pos] = EMPTY
            best_score = min(best_score, score)
        return best_score

def bot_move_hard(board):
    best_score = -999
    best_move = None
    for pos in available_moves(board):
        board[pos] = BOT
        score = minimax(board, False)
        board[pos] = EMPTY
        if score > best_score:
            best_score = score
            best_move = pos
    board[best_move] = BOT

def choose_level():
    while True:
        print("Choisis le niveau du bot :")
        print("1 - Facile")
        print("2 - Moyen")
        print("3 - Difficile")
        choice = input("Niveau : ")
        if choice in ("1", "2", "3"):
            return int(choice)
        print("Choix invalide.")

def play_game_v2():
    level = choose_level()
    board = create_board()
    current = HUMAN
    while True:
        print_board(board)
        if current == HUMAN:
            human_move(board)
        else:
            if level == 1:
                bot_move_easy(board)
            elif level == 2:
                bot_move_medium(board)
            else:
                bot_move_hard(board)
        result = check_winner(board)
        if result:
            print_board(board)
            if result == "draw":
                print("Match nul.")
            elif result == HUMAN:
                print("Tu as gagné !")
            else:
                print("Le bot (niveau", level, ") a gagné.")
            break
        current = BOT if current == HUMAN else HUMAN

if __name__ == "__main__":
    play_game_v2()