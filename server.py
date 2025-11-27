import socket
import threading
import random

HOST = "0.0.0.0"
PORT = 5000

EMPTY = " "
SYMBOLS = ["X", "O"]

# Dictionnaire : code -> {"creator": conn, "joiner": conn}
games = {}
lock = threading.Lock()

def create_board():
    return [EMPTY] * 9

def check_winner(board):
    wins = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
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

def board_to_string(board):
    s = ""
    for i in range(3):
        row = board[3*i:3*i+3]
        s += " | ".join(c if c != EMPTY else "." for c in row) + "\n"
    return s

def handle_game(conn1, conn2):
    board = create_board()
    players = {conn1: SYMBOLS[0], conn2: SYMBOLS[1]}
    current_conn = conn1

    while True:
        # Envoi du plateau aux deux joueurs
        for c in (conn1, conn2):
            c.sendall(b"BOARD\n")
            c.sendall(board_to_string(board).encode())

        current_symbol = players[current_conn]
        other_conn = conn2 if current_conn is conn1 else conn1

        current_conn.sendall(f"YOUR_TURN {current_symbol}\n".encode())
        other_conn.sendall(f"WAIT {current_symbol}\n".encode())

        data = current_conn.recv(1024).decode().strip()
        if not data:
            break

        try:
            _, pos_str = data.split()
            pos = int(pos_str)
        except Exception:
            current_conn.sendall(b"INVALID\n")
            continue

        if pos < 0 or pos > 8 or board[pos] != EMPTY:
            current_conn.sendall(b"INVALID\n")
            continue

        board[pos] = current_symbol
        result = check_winner(board)
        if result:
            for c in (conn1, conn2):
                c.sendall(b"BOARD\n")
                c.sendall(board_to_string(board).encode())
            if result == "draw":
                msg = "RESULT DRAW\n"
            else:
                msg = f"RESULT WIN {result}\n"
            for c in (conn1, conn2):
                c.sendall(msg.encode())
            break

        current_conn = other_conn

    conn1.close()
    conn2.close()

def handle_client(conn, addr):
    """
    Protocole texte :
    - CREATE          -> le serveur génère un code et répond CODE <xxxx>
    - JOIN de>     -> le serveur associe ce client comme 2e joueur
    """
    try:
        line = conn.recv(1024).decode().strip()
        if not line:
            conn.close()
            return

        parts = line.split()
        cmd = parts[0].upper()

        if cmd == "CREATE":
            # Générer un code unique
            with lock:
                while True:
                    code = str(random.randint(1000, 9999))
                    if code not in games:
                        games[code] = {"creator": conn, "joiner": None}
                        break
            conn.sendall(f"CODE {code}\n".encode())
            conn.sendall(b"WAITING\n")

            # Attendre que le joiner arrive
            while True:
                with lock:
                    joiner = games[code]["joiner"]
                if joiner is not None:
                    break

            # Lancer la partie
            handle_game(conn, joiner)

            # Nettoyer
            with lock:
                del games[code]

        elif cmd == "JOIN" and len(parts) == 2:
            code = parts[1]
            with lock:
                if code not in games or games[code]["joiner"] is not None:
                    conn.sendall(b"INVALID_CODE\n")
                    conn.close()
                    return
                games[code]["joiner"] = conn
                creator = games[code]["creator"]

            conn.sendall(b"JOIN_OK\n")
            creator.sendall(b"OPPONENT_JOINED\n")
            # La partie est gérée par le thread CREATE (handle_game)
        else:
            conn.sendall(b"INVALID_COMMAND\n")
            conn.close()

    except Exception:
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Serveur en écoute sur {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        print("Nouveau client :", addr)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
