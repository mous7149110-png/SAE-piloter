EMPTY = " "

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

def player_move(board, symbol, player_name):
    while True:
        try:
            choice = int(input(f"{player_name} ({symbol}), choisis une case (1-9) : ")) - 1
            if choice < 0 or choice > 8:
                print("Choix invalide.")
            elif board[choice] != EMPTY:
                print("Case déjà prise.")
            else:
                board[choice] = symbol
                break
        except ValueError:
            print("Entre un nombre entre 1 et 9.")

def play_game_v3():
    # Demander les prénoms
    player1_name = input("Prénom du joueur 1 (X) : ")
    player2_name = input("Prénom du joueur 2 (O) : ")

    board = create_board()
    player1_symbol = "X"
    player2_symbol = "O"
    current_symbol = player1_symbol
    current_name = player1_name

    while True:
        print_board(board)
        player_move(board, current_symbol, current_name)
        result = check_winner(board)
        if result:
            print_board(board)
            if result == "draw":
                print("Match nul.")
            else:
                winner_name = player1_name if result == player1_symbol else player2_name
                print(f"{winner_name} ({result}) a gagné !")
            break
        # Changer de joueur
        if current_symbol == player1_symbol:
            current_symbol = player2_symbol
            current_name = player2_name
        else:
            current_symbol = player1_symbol
            current_name = player1_name

if __name__ == "__main__":
    play_game_v3()