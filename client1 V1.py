import socket

SERVER_HOST = "127.0.0.1"   # à adapter avec l'IP du serveur
SERVER_PORT = 5000

def play_loop(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        msg = data.decode()

        if msg.startswith("BOARD"):
            board_str = sock.recv(1024).decode()
            print("\nPlateau :")
            print(board_str)
        elif msg.startswith("YOUR_TURN"):
            _, sym = msg.strip().split()
            print(f"C'est ton tour ({sym}).")
            while True:
                try:
                    case = int(input("Choisis une case (1-9) : ")) - 1
                    if case < 0 or case > 8:
                        print("Choix invalide.")
                        continue
                    sock.sendall(f"MOVE {case}\n".encode())
                    break
                except ValueError:
                    print("Entre un nombre entre 1 et 9.")
        elif msg.startswith("WAIT"):
            _, sym = msg.strip().split()
            print(f"Attends, c'est au joueur {sym}.")
        elif msg.startswith("INVALID"):
            print("Coup invalide, recommence.")
        elif msg.startswith("RESULT"):
            parts = msg.strip().split()
            if parts[1] == "DRAW":
                print("Match nul.")
            elif parts[1] == "WIN":
                print(f"Le joueur {parts[2]} a gagné.")
            break

def create_game():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))
    sock.sendall(b"CREATE\n")
    # Réception du code
    line = sock.recv(1024).decode().strip()
    if not line.startswith("CODE"):
        print("Erreur côté serveur (pas de code).")
        sock.close()
        return
    _, code = line.split()
    print(f"Partie créée. Code à communiquer au 2e joueur : {code}")

    # Attente de l'adversaire
    status = sock.recv(1024).decode().strip()
    if status == "WAITING":
        print("En attente d'un adversaire...")
        msg = sock.recv(1024).decode().strip()
        if msg == "OPPONENT_JOINED":
            print("Adversaire connecté, la partie commence.")
            play_loop(sock)

    sock.close()

def join_game():
    code = input("Entrez le code de la partie : ").strip()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))
    sock.sendall(f"JOIN {code}\n".encode())
    resp = sock.recv(1024).decode().strip()
    if resp == "INVALID_CODE":
        print("Code invalide ou partie déjà pleine.")
        sock.close()
        return
    elif resp == "JOIN_OK":
        print("Connexion à la partie réussie, la partie commence.")
        play_loop(sock)
    sock.close()

def main():
    print("1 - Jouer en ligne (créer une partie)")
    print("2 - Saisir un code (rejoindre une partie)")
    choice = input("Choix : ").strip()
    if choice == "1":
        create_game()
    elif choice == "2":
        join_game()
    else:
        print("Choix invalide.")

if __name__ == "__main__":
    main()
