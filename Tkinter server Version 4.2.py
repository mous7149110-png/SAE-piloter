import socket
import threading
import sqlite3
import hashlib

HOST = "0.0.0.0"
PORT = 5000

EMPTY = " "

waiting_client = None
waiting_lock = threading.Lock()

DB_FILE = "users.db"


# ---------- Base de données utilisateurs ----------

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pseudo TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(pseudo: str, password: str) -> (bool, str):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE pseudo = ?", (pseudo,))
        if cur.fetchone():
            conn.close()
            return False, "Pseudo déjà utilisé."
        pwd_hash = hash_password(password)
        cur.execute("INSERT INTO users (pseudo, password_hash) VALUES (?, ?)", (pseudo, pwd_hash))
        conn.commit()
        conn.close()
        return True, "Inscription réussie."
    except Exception as e:
        return False, f"Erreur DB: {e}"


def check_login(pseudo: str, password: str) -> (bool, str):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE pseudo = ?", (pseudo,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return False, "Pseudo introuvable."
        stored_hash = row[0]
        if stored_hash == hash_password(password):
            return True, "Connexion réussie."
        else:
            return False, "Mot de passe incorrect."
    except Exception as e:
        return False, f"Erreur DB: {e}"


# ---------- Logique de jeu ----------

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
    """
    Protocole simplifié :

    - REGISTER <pseudo> <motdepasse>
        -> REGISTER_OK
        -> REGISTER_ERROR <message>

    - LOGIN <pseudo> <motdepasse>
        -> LOGIN_OK
        -> WAITING
        -> (plus tard) MATCH_FOUND
        -> BOARD / YOUR_TURN / WAIT / INVALID / RESULT ...
    """
    global waiting_client

    try:
        data = conn.recv(1024)
        if not data:
            conn.close()
            return
        line = data.decode().strip()
        parts = line.split()
        if not parts:
            conn.sendall(b"INVALID_COMMAND\n")
            conn.close()
            return

        cmd = parts[0].upper()

        if cmd == "REGISTER" and len(parts) >= 3:
            pseudo = parts[1]
            password = " ".join(parts[2:])
            ok, msg = register_user(pseudo, password)
            if ok:
                conn.sendall(b"REGISTER_OK\n")
            else:
                conn.sendall(f"REGISTER_ERROR {msg}\n".encode())
            conn.close()
            return

        elif cmd == "LOGIN" and len(parts) >= 3:
            pseudo = parts[1]
            password = " ".join(parts[2:])
            ok, msg = check_login(pseudo, password)
            if not ok:
                conn.sendall(f"LOGIN_ERROR {msg}\n".encode())
                conn.close()
                return
            else:
                conn.sendall(b"LOGIN_OK\n")
                conn.sendall(b"WAITING\n")

                with waiting_lock:
                    global waiting_client
                    if waiting_client is None:
                        waiting_client = conn
                        return  # ce thread se termine, connexion gardée pour futur adversaire
                    else:
                        opponent = waiting_client
                        waiting_client = None

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

                # Lancer la partie : opponent = X, conn = O
                handle_game(opponent, conn)
                return

        else:
            conn.sendall(b"INVALID_COMMAND\n")
            conn.close()
            return

    except Exception:
        try:
            conn.close()
        except Exception:
            pass


def main():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Serveur matchmaking + login en écoute sur {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        print("Nouveau client :", addr)
        threading.Thread(target=matchmaking, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
