import tkinter as tk
from tkinter import messagebox
import random

EMPTY = " "
HUMAN = "X"
BOT = "O"

class TicTacToeV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Morpion - Version 2 (Niveaux Bot)")
        self.current_player = HUMAN
        self.board = [EMPTY] * 9
        self.buttons = []
        self.level = 1  # 1 = facile, 2 = moyen, 3 = difficile

        self.create_menu()

    # --------- Écrans / menu ---------

    def create_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        tk.Label(frame, text="Morpion - Version 2", font=("Arial", 16)).pack(pady=10)

        # Choix du niveau
        level_frame = tk.LabelFrame(frame, text="Niveau du bot", padx=10, pady=10)
        level_frame.pack(pady=5)

        self.level_var = tk.IntVar(value=1)
        tk.Radiobutton(level_frame, text="Facile",   variable=self.level_var, value=1).pack(anchor="w")
        tk.Radiobutton(level_frame, text="Moyen",    variable=self.level_var, value=2).pack(anchor="w")
        tk.Radiobutton(level_frame, text="Difficile", variable=self.level_var, value=3).pack(anchor="w")

        tk.Button(frame, text="Jouer (Joueur vs Bot)",
                  font=("Arial", 12),
                  command=self.start_game).pack(pady=5)

        tk.Button(frame, text="Quitter",
                  font=("Arial", 12),
                  command=self.root.quit).pack(pady=5)

    def start_game(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.board = [EMPTY] * 9
        self.current_player = HUMAN
        self.buttons = []
        self.level = self.level_var.get()

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Button(top_frame, text="Retour menu",
                  command=self.create_menu).pack()

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

    # --------- Logique de jeu ---------

    def on_cell_clicked(self, index):
        if self.board[index] != EMPTY:
            return
        if self.current_player != HUMAN:
            return

        self.board[index] = HUMAN
        self.buttons[index]["text"] = HUMAN

        if self.check_end_of_game():
            return

        self.current_player = BOT
        self.root.after(300, self.bot_move)  # petit délai

    def available_moves(self):
        return [i for i, v in enumerate(self.board) if v == EMPTY]

    def bot_move(self):
        if self.level == 1:
            self.bot_easy()
        elif self.level == 2:
            self.bot_medium()
        else:
            self.bot_hard()

        if self.check_end_of_game():
            return

        self.current_player = HUMAN

    # --------- IA Niveaux ---------

    # Facile: totalement aléatoire
    def bot_easy(self):
        moves = self.available_moves()
        if not moves:
            return
        choice = random.choice(moves)
        self.board[choice] = BOT
        self.buttons[choice]["text"] = BOT

    # Moyen: gagne si possible, sinon bloque, sinon aléatoire
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

    # Difficile: Minimax (IA optimale)
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

    # --------- Fin de partie ---------

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

    def check_end_of_game(self):
        result = self.check_winner()
        if result is None:
            return False

        if result == "draw":
            messagebox.showinfo("Fin de partie", "Match nul.")
        elif result == HUMAN:
            messagebox.showinfo("Fin de partie", "Tu as gagné !")
        else:
            msg_level = {1: "Facile", 2: "Moyen", 3: "Difficile"}[self.level]
            messagebox.showinfo("Fin de partie", f"Le bot ({msg_level}) a gagné.")

        if messagebox.askyesno("Rejouer", "Voulez-vous rejouer ?"):
            self.start_game()
        else:
            self.create_menu()
        return True


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeV2(root)
    root.mainloop()
