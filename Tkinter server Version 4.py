import socket
import threading

HOST = "0.0.0.0"
PORT = 5000

EMPTY = " "

waiting_client = None
waiting_lock = threading.Lock()


def create_board():
    return [EMPTY] * 9


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


def board_to_string(board):
    s = ""
    for i in range(3):
        row = board[3 * i:3 * i + 3]
        s += " | ".join(c if c != EMPTY else "." for c in row) + "\n"
    return s


def handle_game(conn1, conn2):
    # conn1 = X, conn2 = O
    board = create_board()
    players = {conn1: "X", conn2: "O"}
    current_conn = conn1

    try:
        while True:
            # Envoi du plateau aux deux joueurs
            for c in (conn1, conn2):
                c.sendall(b"BOARD\n")
                c.sendall(board_to_string(board).encode())

            current_symbol = players[current_conn]
            other_conn = conn2 if current_conn is conn1 else conn1

            current_conn.sendall(f"YOUR_TURN {current_symbol}\n".encode())
            other_conn.sendall(f"WAIT {current_symbol}\n".encode())

            data = current_conn.recv(1024)
            if not data:
                break
            msg = data.decode().strip()

            # Attendu : MOVE <pos>
            try:
                cmd, pos_str = msg.split()
                if cmd != "MOVE":
                    current_conn.sendall(b"INVALID\n")
                    continue
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

    except Exception:
        pass
    finally:
        try:
            conn1.close()
        except Exception:
            pass
        try:
            conn2.close()
        except Exception:
            pass


def matchmaking(conn):
    global waiting_client
    try:
        # Le client envoie "QUEUE"
        data = conn.recv(1024)
        if not data:
            conn.close()
            return
        msg = data.decode().strip()
        if msg != "QUEUE":
            conn.sendall(b"INVALID_COMMAND\n")
            conn.close()
            return

        conn.sendall(b"WAITING\n")

        # Gestion de la file d'attente
        with waiting_lock:
            global waiting_client
            if waiting_client is None:
                # Personne n'attend, ce client sera le prochain
                waiting_client = conn
                return  # le thread se termine, mais la socket reste ouverte
            else:
                # Un client attend déjà, on le récupère et on lance une partie
                opponent = waiting_client
                waiting_client = None

        # Informer les deux qu'un joueur a été trouvé
        try:
            conn.sendall(b"MATCH_FOUND\n")
        except Exception:
            conn.close()
            return
        try:
            opponent.sendall(b"MATCH_FOUND\n")
        except Exception:
            opponent.close()
            conn.close()
            return

        # Lancer la partie : opponent = X, conn = O (par exemple)
        handle_game(opponent, conn)

    except Exception:
        try:
            conn.close()
        except Exception:
            pass


def cleanup_waiting_on_close():
    # Optionnel : pourrait surveiller waiting_client et vérifier si encore connecté
    pass


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Serveur matchmaking en écoute sur {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        print("Nouveau client :", addr)
        threading.Thread(target=matchmaking, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
