import tkinter as tk
from tkinter import messagebox, simpledialog
import random

EMPTY = " "
HUMAN = "X"
BOT = "O"

class MorpionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Morpion - Menu principal")
        self.board = [EMPTY] * 9
        self.buttons = []

        # Mode de jeu
        self.mode = "bot_random"  # "bot_random", "bot_level", "pvp"
        self.level = 1  # pour mode "bot_level": 1=facile, 2=moyen, 3=difficile

        # Pour mode Joueur vs Joueur
        self.player1_name = "Joueur 1"
        self.player2_name = "Joueur 2"
        self.current_symbol = "X"

        self.create_main_menu()

    # ---------- Menus ----------

    def create_main_menu(self):
        for w in self.root.winfo_children():
            w.destroy()

        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        tk.Label(frame, text="Morpion - Menu principal", font=("Arial", 16)).pack(pady=10)

        tk.Button(frame, text="Joueur VS bot aléatoire",
                  font=("Arial", 12),
                  width=25,
                  command=self.start_bot_random).pack(pady=5)

        tk.Button(frame, text="Choix difficulté du bot",
                  font=("Arial", 12),
                  width=25,
                  command=self.open_bot_level_menu).pack(pady=5)

        tk.Button(frame, text="Joueur 1 VS Joueur 2",
                  font=("Arial", 12),
                  width=25,
                  command=self.start_pvp).pack(pady=5)

        tk.Button(frame, text="Quitter",
                  font=("Arial", 12),
                  width=25,
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

    # ---------- Lancement des modes ----------

    def start_bot_random(self):
        self.mode = "bot_random"
        self.level = 1
        self.start_game_board()

    def start_bot_level(self):
        self.mode = "bot_level"
        self.level = self.level_var.get()
        self.start_game_board()

    def start_pvp(self):
        self.mode = "pvp"
        # Demander les prénoms
        self.player1_name = simpledialog.askstring("Joueur 1", "Prénom du joueur 1 (X) :") or "Joueur 1"
        self.player2_name = simpledialog.askstring("Joueur 2", "Prénom du joueur 2 (O) :") or "Joueur 2"
        self.current_symbol = "X"
        self.start_game_board()

    # ---------- Plateau commun ----------

    def start_game_board(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.board = [EMPTY] * 9
        self.buttons = []

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Button(top_frame, text="Retour menu principal",
                  command=self.create_main_menu).pack()

        if self.mode == "pvp":
            info_text = f"{self.player1_name} (X) VS {self.player2_name} (O)"
        elif self.mode == "bot_random":
            info_text = "Joueur (X) VS Bot aléatoire (O)"
        else:
            label_level = {1: "Facile", 2: "Moyen", 3: "Difficile"}[self.level]
            info_text = f"Joueur (X) VS Bot ({label_level}) (O)"

        tk.Label(self.root, text=info_text, font=("Arial", 12)).pack(pady=5)

        grid_frame = tk.Frame(self.root)
        grid_frame.pack()

        for i in range(9):
            btn = tk.Button(
                grid_frame,
                text="",
                font=("Arial", 24),
                width=3,
                height=1,
                command=lambda idx=i: self.on_cell_clicked(idx)
            )
            btn.grid(row=i // 3, column=i % 3)
            self.buttons.append(btn)

    # ---------- Gestion des clics ----------

    def on_cell_clicked(self, index):
        if self.board[index] != EMPTY:
            return

        if self.mode in ("bot_random", "bot_level"):
            # Tour du joueur humain
            self.board[index] = HUMAN
            self.buttons[index]["text"] = HUMAN

            if self.check_end_of_game():
                return

            # Tour du bot
            self.root.after(300, self.bot_play)
        else:
            # Mode Joueur vs Joueur
            self.board[index] = self.current_symbol
            self.buttons[index]["text"] = self.current_symbol

            if self.check_end_of_game_pvp():
                return

            # Changer de joueur
            self.current_symbol = "O" if self.current_symbol == "X" else "X"

    # ---------- Logique IA ----------

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

        self.check_end_of_game()

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

        # 1) Essayer de gagner
        for pos in moves:
            backup = self.board[pos]
            self.board[pos] = BOT
            if self.check_winner() == BOT:
                self.buttons[pos]["text"] = BOT
                return
            self.board[pos] = backup

        # 2) Bloquer le joueur
        for pos in moves:
            backup = self.board[pos]
            self.board[pos] = HUMAN
            if self.check_winner() == HUMAN:
                self.board[pos] = BOT
                self.buttons[pos]["text"] = BOT
                return
            self.board[pos] = backup

        # 3) Sinon aléatoire
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
            best_score = -999
            for pos in self.available_moves():
                self.board[pos] = BOT
                score = self.minimax(False)
                self.board[pos] = EMPTY
                if score > best_score:
                    best_score = score
            return best_score
        else:
            best_score = 999
            for pos in self.available_moves():
                self.board[pos] = HUMAN
                score = self.minimax(True)
                self.board[pos] = EMPTY
                if score < best_score:
                    best_score = score
            return best_score

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

    # ---------- Fin de partie (commun IA) ----------

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
            self.start_game_board()
        else:
            self.create_main_menu()

    def check_end_of_game(self):
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

    # ---------- Fin de partie (PvP) ----------

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


if __name__ == "__main__":
    root = tk.Tk()
    app = MorpionApp(root)
    root.mainloop()
