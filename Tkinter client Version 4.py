import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import socket
import threading

EMPTY = " "
HUMAN = "X"
BOT = "O"

SERVER_HOST = "127.0.0.1"  # à adapter avec l'IP publique de ton serveur
SERVER_PORT = 5000


class MorpionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Morpion - Version 4")
        self.board = [EMPTY] * 9
        self.buttons = []

        # Modes : "bot_random", "bot_level", "pvp", "online"
        self.mode = "bot_random"
        self.level = 1

        # PvP local
        self.player1_name = "Joueur 1"
        self.player2_name = "Joueur 2"
        self.current_symbol = "X"

        # Online
        self.online_socket = None
        self.online_is_my_turn = False
        self.online_symbol = "X"  # X ou O
        self.turn_label = None

        self.create_main_menu()

    # ---------- Menus ----------

    def create_main_menu(self):
        self.close_online_socket()
        for w in self.root.winfo_children():
            w.destroy()

        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        tk.Label(frame, text="Morpion - Menu principal (V4)", font=("Arial", 16)).pack(pady=10)

        tk.Button(frame, text="Joueur VS bot aléatoire",
                  font=("Arial", 12), width=25,
                  command=self.start_bot_random).pack(pady=5)

        tk.Button(frame, text="Choix difficulté du bot",
                  font=("Arial", 12), width=25,
                  command=self.open_bot_level_menu).pack(pady=5)

        tk.Button(frame, text="Joueur 1 VS Joueur 2",
                  font=("Arial", 12), width=25,
                  command=self.start_pvp).pack(pady=5)

        tk.Button(frame, text="Jouer en ligne (matchmaking)",
                  font=("Arial", 12), width=25,
                  command=self.start_online_matchmaking).pack(pady=5)

        tk.Button(frame, text="Quitter",
                  font=("Arial", 12), width=25,
                  command=self.root.quit).pack(pady=5)

    def open_bot_level_menu(self):
        for w in self.root.winfo_children():
            w.destroy()

        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        tk.Label(frame, text="Choix difficulté du bot", font=("Arial", 16)).pack(pady=10)

        self.level_var = tk.IntVar(value=self.level)

        tk.Radiobutton(frame, text="Facile", variable=self.level_var, value=1).pack(anchor="w")
        tk.Radiobutton(frame, text="Moyen", variable=self.level_var, value=2).pack(anchor="w")
        tk.Radiobutton(frame, text="Difficile", variable=self.level_var, value=3).pack(anchor="w")

        tk.Button(frame, text="Lancer la partie",
                  font=("Arial", 12),
                  command=self.start_bot_level).pack(pady=10)

        tk.Button(frame, text="Retour menu principal",
                  font=("Arial", 12),
                  command=self.create_main_menu).pack(pady=5)

    # ---------- Lancement modes locaux ----------

    def start_bot_random(self):
        self.mode = "bot_random"
        self.level = 1
        self.start_game_board_local()

    def start_bot_level(self):
        self.mode = "bot_level"
        self.level = self.level_var.get()
        self.start_game_board_local()

    def start_pvp(self):
        self.mode = "pvp"
        self.player1_name = simpledialog.askstring("Joueur 1", "Prénom du joueur 1 (X) :") or "Joueur 1"
        self.player2_name = simpledialog.askstring("Joueur 2", "Prénom du joueur 2 (O) :") or "Joueur 2"
        self.current_symbol = "X"
        self.start_game_board_local()

    # ---------- Plateau local ----------

    def start_game_board_local(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.board = [EMPTY] * 9
        self.buttons = []

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Button(top_frame, text="Retour menu principal",
                  command=self.create_main_menu).pack()

        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)

        if self.mode == "pvp":
            vs_text = f"{self.player1_name} (X) VS {self.player2_name} (O)"
        elif self.mode == "bot_random":
            vs_text = "Joueur (X) VS Bot aléatoire (O)"
        else:
            label_level = {1: "Facile", 2: "Moyen", 3: "Difficile"}[self.level]
            vs_text = f"Joueur (X) VS Bot ({label_level}) (O)"

        tk.Label(info_frame, text=vs_text, font=("Arial", 12)).pack()

        self.turn_label = tk.Label(self.root, font=("Arial", 11))
        self.turn_label.pack(pady=2)
        self.update_turn_label_local()

        grid_frame = tk.Frame(self.root)
        grid_frame.pack()

        for i in range(9):
            btn = tk.Button(
                grid_frame,
                text="",
                font=("Arial", 24),
                width=3,
                height=1,
                command=lambda idx=i: self.on_cell_clicked_local(idx)
            )
            btn.grid(row=i // 3, column=i % 3)
            self.buttons.append(btn)

    def update_turn_label_local(self):
        if self.mode == "pvp":
            if self.current_symbol == "X":
                self.turn_label.config(text=f"Au tour de \"{self.player1_name}\" (X)")
            else:
                self.turn_label.config(text=f"Au tour de \"{self.player2_name}\" (O)")
        else:
            self.turn_label.config(text="Clique sur une case pour jouer")

    def on_cell_clicked_local(self, index):
        if self.board[index] != EMPTY:
            return

        if self.mode in ("bot_random", "bot_level"):
            self.board[index] = HUMAN
            self.buttons[index]["text"] = HUMAN

            if self.check_end_of_game_local():
                return

            self.turn_label.config(text="Tour du bot...")
            self.root.after(300, self.bot_play)
        else:
            self.board[index] = self.current_symbol
            self.buttons[index]["text"] = self.current_symbol

            if self.check_end_of_game_pvp():
                return

            self.current_symbol = "O" if self.current_symbol == "X" else "X"
            self.update_turn_label_local()

    # ---------- IA locale ----------

    def available_moves(self):
        return [i for i, v in enumerate(self.board) if v == EMPTY]

    def bot_play(self):
        if self.mode == "bot_random":
            self.bot_easy()
        else:
            if self.level == 1:
                self.bot_easy()
            elif self.level == 2:
                self.bot_medium()
            else:
                self.bot_hard()

        self.check_end_of_game_local()
        if self.mode in ("bot_random", "bot_level"):
            self.turn_label.config(text="À ton tour de jouer")

    def bot_easy(self):
        moves = self.available_moves()
        if not moves:
            return
        choice = random.choice(moves)
        self.board[choice] = BOT
        self.buttons[choice]["text"] = BOT

    def bot_medium(self):
        moves = self.available_moves()
        if not moves:
            return
        for pos in moves:
            backup = self.board[pos]
            self.board[pos] = BOT
            if self.check_winner() == BOT:
                self.buttons[pos]["text"] = BOT
                return
            self.board[pos] = backup
        for pos in moves:
            backup = self.board[pos]
            self.board[pos] = HUMAN
            if self.check_winner() == HUMAN:
                self.board[pos] = BOT
                self.buttons[pos]["text"] = BOT
                return
            self.board[pos] = backup
        self.bot_easy()

    def minimax(self, is_maximizing):
        winner = self.check_winner()
        if winner == BOT:
            return 1
        elif winner == HUMAN:
            return -1
        elif EMPTY not in self.board:
            return 0
        if is_maximizing:
            best = -999
            for pos in self.available_moves():
                self.board[pos] = BOT
                score = self.minimax(False)
                self.board[pos] = EMPTY
                best = max(best, score)
            return best
        else:
            best = 999
            for pos in self.available_moves():
                self.board[pos] = HUMAN
                score = self.minimax(True)
                self.board[pos] = EMPTY
                best = min(best, score)
            return best

    def bot_hard(self):
        moves = self.available_moves()
        if not moves:
            return
        best_score = -999
        best_move = None
        for pos in moves:
            self.board[pos] = BOT
            score = self.minimax(False)
            self.board[pos] = EMPTY
            if score > best_score:
                best_score = score
                best_move = pos
        if best_move is not None:
            self.board[best_move] = BOT
            self.buttons[best_move]["text"] = BOT

    # ---------- Fin partie locale ----------

    def check_winner(self):
        wins = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for a, b, c in wins:
            if self.board[a] != EMPTY and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        if EMPTY not in self.board:
            return "draw"
        return None

    def end_game_dialog(self, message):
        if messagebox.askyesno("Fin de partie", message + "\n\nRejouer ?"):
            if self.mode == "online":
                self.start_game_board_online()
            else:
                self.start_game_board_local()
        else:
            self.create_main_menu()

    def check_end_of_game_local(self):
        result = self.check_winner()
        if result is None:
            return False
        if result == "draw":
            self.end_game_dialog("Match nul.")
        elif result == HUMAN:
            self.end_game_dialog("Tu as gagné !")
        else:
            if self.mode == "bot_random":
                self.end_game_dialog("Le bot aléatoire a gagné.")
            else:
                label_level = {1: "Facile", 2: "Moyen", 3: "Difficile"}[self.level]
                self.end_game_dialog(f"Le bot ({label_level}) a gagné.")
        return True

    def check_end_of_game_pvp(self):
        result = self.check_winner()
        if result is None:
            return False
        if result == "draw":
            self.end_game_dialog("Match nul.")
        else:
            winner_name = self.player1_name if result == "X" else self.player2_name
            self.end_game_dialog(f"{winner_name} ({result}) a gagné !")
        return True

    # ---------- Online : matchmaking ----------

    def start_online_matchmaking(self):
        self.mode = "online"
        for w in self.root.winfo_children():
            w.destroy()

        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        tk.Label(frame, text="Morpion - Matchmaking en ligne", font=("Arial", 16)).pack(pady=10)

        tk.Button(frame, text="Chercher un matchmaking",
                  font=("Arial", 12), width=25,
                  command=self.online_queue).pack(pady=5)

        tk.Button(frame, text="Retour menu principal",
                  font=("Arial", 12), width=25,
                  command=self.create_main_menu).pack(pady=5)

    def online_queue(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_HOST, SERVER_PORT))
            s.sendall(b"QUEUE\n")
            resp = s.recv(1024).decode().strip()
            if resp != "WAITING":
                messagebox.showerror("Erreur", "Réponse inattendue du serveur.")
                s.close()
                return
            self.online_socket = s
            # Afficher écran d'attente
            self.show_online_wait_screen()
            # Lancer un thread pour attendre MATCH_FOUND
            threading.Thread(target=self.online_wait_match_found, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Erreur", f"Connexion au serveur impossible : {e}")

    def show_online_wait_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        tk.Label(frame, text="En attente d'un autre joueur...", font=("Arial", 14)).pack(pady=10)

        tk.Button(frame, text="Annuler et retourner au menu",
                  font=("Arial", 12),
                  command=self.create_main_menu).pack(pady=5)

    def online_wait_match_found(self):
        try:
            msg = self.online_socket.recv(1024).decode().strip()
            if msg == "MATCH_FOUND":
                # Une fois le match trouvé, lancer la partie en ligne
                self.root.after(0, self.start_game_board_online)
        except Exception:
            self.close_online_socket()
            self.root.after(0, lambda: messagebox.showerror("Erreur", "Connexion perdue."))

    def close_online_socket(self):
        if self.online_socket:
            try:
                self.online_socket.close()
            except Exception:
                pass
        self.online_socket = None

    # ---------- Plateau en ligne ----------

    def start_game_board_online(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.board = [EMPTY] * 9
        self.buttons = []

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Button(top_frame, text="Retour menu principal",
                  command=self.create_main_menu).pack()

        info = "Jeu en ligne (symboles attribués par le serveur)"
        tk.Label(self.root, text=info, font=("Arial", 12)).pack(pady=5)

        self.turn_label = tk.Label(self.root, font=("Arial", 11))
        self.turn_label.pack(pady=2)

        grid_frame = tk.Frame(self.root)
        grid_frame.pack()

        for i in range(9):
            btn = tk.Button(
                grid_frame,
                text="",
                font=("Arial", 24),
                width=3,
                height=1,
                command=lambda idx=i: self.on_cell_clicked_online(idx)
            )
            btn.grid(row=i // 3, column=i % 3)
            self.buttons.append(btn)

        # Au début, on ne sait pas si c'est notre tour ; le serveur l'indiquera
        self.online_is_my_turn = False
        threading.Thread(target=self.online_receive_loop, daemon=True).start()

    def on_cell_clicked_online(self, index):
        if not self.online_is_my_turn:
            return
        if self.board[index] != EMPTY:
            return
        try:
            self.online_socket.sendall(f"MOVE {index}\n".encode())
        except Exception:
            self.close_online_socket()
            messagebox.showerror("Erreur", "Connexion perdue.")

    def online_receive_loop(self):
        try:
            while True:
                data = self.online_socket.recv(1024)
                if not data:
                    break
                msg = data.decode()
                if msg.startswith("BOARD"):
                    board_str = self.online_socket.recv(1024).decode()
                    self.root.after(0, self.update_board_from_string, board_str)
                elif msg.startswith("YOUR_TURN"):
                    _, sym = msg.strip().split()
                    self.online_is_my_turn = True
                    self.root.after(0, lambda: self.turn_label.config(text=f"À ton tour ({sym})"))
                elif msg.startswith("WAIT"):
                    _, sym = msg.strip().split()
                    self.online_is_my_turn = False
                    self.root.after(0, lambda: self.turn_label.config(text=f"En attente du joueur {sym}"))
                elif msg.startswith("INVALID"):
                    self.root.after(0, lambda: messagebox.showinfo("Info", "Coup invalide."))
                elif msg.startswith("RESULT"):
                    parts = msg.strip().split()
                    if parts[1] == "DRAW":
                        self.root.after(0, lambda: self.end_game_dialog("Match nul."))
                    elif parts[1] == "WIN":
                        self.root.after(0, lambda: self.end_game_dialog(f"Le joueur {parts[2]} a gagné !"))
                    break
        except Exception:
            pass
        finally:
            self.close_online_socket()

    def update_board_from_string(self, board_str):
        rows = board_str.strip().split("\n")
        flat = []
        for r in rows:
            cells = [c.strip() for c in r.split("|")]
            for c in cells:
                flat.append(" " if c == "." else c)
        if len(flat) == 9:
            self.board = flat
            for i, v in enumerate(flat):
                self.buttons[i]["text"] = "" if v == " " else v


if __name__ == "__main__":
    root = tk.Tk()
    app = MorpionApp(root)
    root.mainloop()
