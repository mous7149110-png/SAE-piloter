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

def bot_move_easy(board):
    available = [i for i, v in enumerate(board) if v == EMPTY]
    pos = random.choice(available)
    board[pos] = BOT

def play_game_v1():
    board = create_board()
    current = HUMAN
    while True:
        print_board(board)
        if current == HUMAN:
            human_move(board)
        else:
            bot_move_easy(board)
        result = check_winner(board)
        if result:
            print_board(board)
            if result == "draw":
                print("Match nul.")
            elif result == HUMAN:
                print("Tu as gagné !")
            else:
                print("Le bot a gagné.")
            break
        current = BOT if current == HUMAN else HUMAN

if __name__ == "__main__":
    play_game_v1()
