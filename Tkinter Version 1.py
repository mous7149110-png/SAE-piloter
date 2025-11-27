import tkinter as tk
from tkinter import messagebox
import random

# Constantes
EMPTY = " "
HUMAN = "X"
BOT = "O"

class TicTacToeV1:
    def __init__(self, root):
        self.root = root
        self.root.title("Morpion - Version 1 (Joueur vs Bot)")
        self.current_player = HUMAN
        self.board = [EMPTY] * 9
        self.buttons = []

        self.create_menu()

    def create_menu(self):
        # Effacer le contenu
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        tk.Label(frame, text="Morpion - Version 1", font=("Arial", 16)).pack(pady=10)

        tk.Button(frame, text="Jouer (Joueur vs Bot)",
                  font=("Arial", 12),
                  command=self.start_game).pack(pady=5)

        tk.Button(frame, text="Quitter",
                  font=("Arial", 12),
                  command=self.root.quit).pack(pady=5)

    def start_game(self):
        # Effacer l'écran et créer la grille
        for widget in self.root.winfo_children():
            widget.destroy()

        self.board = [EMPTY] * 9
        self.current_player = HUMAN
        self.buttons = []

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

    def on_cell_clicked(self, index):
        # Clic humain
        if self.board[index] != EMPTY:
            return

        if self.current_player != HUMAN:
            return

        self.board[index] = HUMAN
        self.buttons[index]["text"] = HUMAN

        if self.check_end_of_game():
            return

        self.current_player = BOT
        self.root.after(300, self.bot_move)  # petit délai pour l'effet

    def bot_move(self):
        # Bot très simple : coup aléatoire sur case vide
        available = [i for i, v in enumerate(self.board) if v == EMPTY]
        if not available:
            return

        choice = random.choice(available)
        self.board[choice] = BOT
        self.buttons[choice]["text"] = BOT

        if self.check_end_of_game():
            return

        self.current_player = HUMAN

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
            messagebox.showinfo("Fin de partie", "Le bot a gagné.")

        # Rejouer ?
        if messagebox.askyesno("Rejouer", "Voulez-vous rejouer ?"):
            self.start_game()
        else:
            self.create_menu()
        return True


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeV1(root)
    root.mainloop()
