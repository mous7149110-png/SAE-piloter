import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import json
import os

EMPTY = " "
HUMAN = "X"
BOT = "O"

POINTS_FILE = "points.json"


class MorpionV5App:
    def __init__(self, root):
        self.root = root
        self.root.title("Morpion - Version 5")
        self.board = [EMPTY] * 9
        self.buttons = []

        # Modes : "bot_random", "bot_level", "pvp"
        self.mode = "bot_random"
        self.level = 1

        # PvP local
        self.player1_name = "Joueur 1"
        self.player2_name = "Joueur 2"
        self.current_symbol = "X"

        # Points
        self.points = 0
        self.load_points()

        # 15 thèmes de plateau
        self.board_themes = {
            "Classique":      {"bg": "SystemButtonFace", "fg": "black",  "cost": 0},
            "Sombre":        {"bg": "#222222",          "fg": "white",  "cost": 20},
            "Océan":         {"bg": "#1B4965",          "fg": "white",  "cost": 20},
            "Forêt":         {"bg": "#2B9348",          "fg": "white",  "cost": 20},
            "Désert":        {"bg": "#F4A261",          "fg": "black",  "cost": 20},
            "Neige":         {"bg": "#E0FBFC",          "fg": "black",  "cost": 20},
            "Lave":          {"bg": "#9D0208",          "fg": "yellow", "cost": 25},
            "Violet néon":   {"bg": "#3A0CA3",          "fg": "#F72585","cost": 25},
            "Cyber":         {"bg": "#0B090A",          "fg": "#00FF9F","cost": 25},
            "Pastel":        {"bg": "#FFDDD2",          "fg": "#1D3557","cost": 20},
            "Noir & Or":     {"bg": "#000000",          "fg": "#FFD700","cost": 30},
            "Gris métal":    {"bg": "#6C757D",          "fg": "white",  "cost": 20},
            "Bleu nuit":     {"bg": "#03045E",          "fg": "#CAF0F8","cost": 20},
            "Vert pomme":    {"bg": "#80ED99",          "fg": "#22577A","cost": 20},
            "Retro Game":    {"bg": "#22223B",          "fg": "#F2E9E4","cost": 25},
        }
        self.board_theme = "Classique"

        # 15 couleurs Joueur/Bot
        self.symbol_colors_player = {
            "Noir":      ("black", 0),
            "Rouge":     ("red", 10),
            "Bleu":      ("blue", 10),
            "Vert":      ("green", 10),
            "Orange":    ("orange", 10),
            "Violet":    ("purple", 10),
            "Rose":      ("deeppink", 10),
            "Cyan":      ("cyan", 10),
            "Jaune":     ("yellow", 10),
            "Marron":    ("saddlebrown", 10),
            "Turquoise": ("turquoise", 10),
            "Gris":      ("gray", 10),
            "Blanc":     ("white", 10),
            "Or":        ("gold", 15),
            "Arc ciel":  ("magenta", 15),
        }
        self.symbol_colors_bot = dict(self.symbol_colors_player)

        self.symbol_color_X = "black"
        self.symbol_color_O = "black"

        # Items acquis
        self.owned_board_themes = set()
        self.owned_player_colors = set()
        self.owned_bot_colors = set()
        self.load_owned()

        self.turn_label = None

        self.create_menubar()
        self.create_main_menu()

    # ---------- Chargement / sauvegarde ----------

    def load_points(self):
        if os.path.exists(POINTS_FILE):
            try:
                with open(POINTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.points = int(data.get("points", 0))
            except Exception:
                self.points = 0
        else:
            self.points = 0

    def load_owned(self):
        if os.path.exists(POINTS_FILE):
            try:
                with open(POINTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.owned_board_themes = set(data.get("owned_boards", []))
                self.owned_player_colors = set(data.get("owned_player_colors", []))
                self.owned_bot_colors = set(data.get("owned_bot_colors", []))
            except Exception:
                self.owned_board_themes = set()
                self.owned_player_colors = set()
                self.owned_bot_colors = set()
        else:
            self.owned_board_themes = set()
            self.owned_player_colors = set()
            self.owned_bot_colors = set()

    def save_all(self):
        data = {
            "points": self.points,
            "owned_boards": list(self.owned_board_themes),
            "owned_player_colors": list(self.owned_player_colors),
            "owned_bot_colors": list(self.owned_bot_colors),
        }
        try:
            with open(POINTS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass

    # ---------- Barre de menus ----------

    def create_menubar(self):
        menubar = tk.Menu(self.root)

        info_menu = tk.Menu(menubar, tearoff=0)
        info_menu.add_command(label="Mes points", command=self.show_points)
        menubar.add_cascade(label="!", menu=info_menu)

        shop_menu = tk.Menu(menubar, tearoff=0)
        shop_menu.add_command(label="Plateau de jeu", command=self.open_shop_board)
        shop_menu.add_command(label="Couleur des symboles", command=self.open_shop_symbols)
        menubar.add_cascade(label="Boutique", menu=shop_menu)

        self.root.config(menu=menubar)

    def show_points(self):
        messagebox.showinfo("Mes points", f"Tu as actuellement {self.points} points.")

    # ---------- Boutique : Plateau ----------

    def open_shop_board(self):
        win = tk.Toplevel(self.root)
        win.title("Boutique - Plateau de jeu")

        tk.Label(win, text=f"Points disponibles : {self.points}", font=("Arial", 11)).pack(pady=5)

        frame = tk.Frame(win)
        frame.pack(padx=10, pady=5)

        row = 0
        col = 0

        def make_action(theme_name):
            def action():
                info = self.board_themes[theme_name]
                cost = info["cost"]

                if cost == 0 or theme_name in self.owned_board_themes:
                    self.board_theme = theme_name
                    messagebox.showinfo("Plateau", f"Plateau \"{theme_name}\" sélectionné.")
                    self.refresh_board_theme()
                else:
                    if self.points >= cost:
                        self.points -= cost
                        self.owned_board_themes.add(theme_name)
                        self.board_theme = theme_name
                        self.save_all()
                        messagebox.showinfo("Plateau", f"Plateau \"{theme_name}\" acheté et activé !")
                        self.refresh_board_theme()
                        win.destroy()
                    else:
                        messagebox.showwarning(
                            "Achat impossible",
                            f"Pas assez de points ({cost} requis) pour \"{theme_name}\"."
                        )
            return action

        for name, info in self.board_themes.items():
            if info["cost"] == 0 or name in self.owned_board_themes:
                text = f"{name} (Acquis)"
            else:
                text = f"{name} ({info['cost']} pts)"
            btn = tk.Button(frame, text=text, width=25, command=make_action(name))
            btn.grid(row=row, column=col, padx=5, pady=3)
            col += 1
            if col == 2:
                col = 0
                row += 1

    def refresh_board_theme(self):
        info = self.board_themes.get(self.board_theme, self.board_themes["Classique"])
        bg = info["bg"]
        fg = info["fg"]
        for btn in self.buttons:
            btn.configure(bg=bg, fg=fg)

    # ---------- Boutique : Couleurs ----------

    def open_shop_symbols(self):
        win = tk.Toplevel(self.root)
        win.title("Boutique - Couleurs des symboles")

        tk.Label(win, text=f"Points disponibles : {self.points}", font=("Arial", 11)).pack(pady=5)

        notebook = tk.Frame(win)
        notebook.pack(padx=10, pady=5)

        frame_player = tk.LabelFrame(notebook, text="Couleurs Joueur (X)")
        frame_player.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        frame_bot = tk.LabelFrame(notebook, text="Couleurs Bot (O)")
        frame_bot.grid(row=0, column=1, padx=5, pady=5, sticky="n")

        def make_player_action(name, color, cost):
            def action():
                if cost == 0 or name in self.owned_player_colors:
                    self.symbol_color_X = color
                    messagebox.showinfo("Couleur Joueur", f"Couleur X \"{name}\" sélectionnée.")
                else:
                    if self.points >= cost:
                        self.points -= cost
                        self.owned_player_colors.add(name)
                        self.symbol_color_X = color
                        self.save_all()
                        messagebox.showinfo("Couleur Joueur", f"Couleur X \"{name}\" achetée et activée.")
                        win.destroy()
                    else:
                        messagebox.showwarning(
                            "Achat impossible",
                            f"Pas assez de points ({cost} requis) pour \"{name}\"."
                        )
            return action

        def make_bot_action(name, color, cost):
            def action():
                if cost == 0 or name in self.owned_bot_colors:
                    self.symbol_color_O = color
                    messagebox.showinfo("Couleur Bot", f"Couleur O \"{name}\" sélectionnée.")
                else:
                    if self.points >= cost:
                        self.points -= cost
                        self.owned_bot_colors.add(name)
                        self.symbol_color_O = color
                        self.save_all()
                        messagebox.showinfo("Couleur Bot", f"Couleur O \"{name}\" achetée et activée.")
                        win.destroy()
                    else:
                        messagebox.showwarning(
                            "Achat impossible",
                            f"Pas assez de points ({cost} requis) pour \"{name}\"."
                        )
            return action

        row = 0
        for name, (color, cost) in self.symbol_colors_player.items():
            if cost == 0 or name in self.owned_player_colors:
                txt = f"{name} (Acquis)"
            else:
                txt = f"{name} ({cost} pts)"
            btn = tk.Button(frame_player, text=txt, fg=color, width=18,
                            command=make_player_action(name, color, cost))
            btn.grid(row=row, column=0, padx=3, pady=2, sticky="w")
            row += 1

        row = 0
        for name, (color, cost) in self.symbol_colors_bot.items():
            if cost == 0 or name in self.owned_bot_colors:
                txt = f"{name} (Acquis)"
            else:
                txt = f"{name} ({cost} pts)"
            btn = tk.Button(frame_bot, text=txt, fg=color, width=18,
                            command=make_bot_action(name, color, cost))
            btn.grid(row=row, column=0, padx=3, pady=2, sticky="w")
            row += 1

    # ---------- Menus principaux ----------

    def create_main_menu(self):
        for w in self.root.winfo_children():
            if not isinstance(w, tk.Menu):
                w.destroy()

        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        tk.Label(frame, text="Morpion - Version 5", font=("Arial", 16)).pack(pady=10)
        

        tk.Button(frame, text="Joueur VS bot aléatoire",
                  font=("Arial", 12), width=25,
                  command=self.start_bot_random).pack(pady=5)

        tk.Button(frame, text="Choix difficulté du bot",
                  font=("Arial", 12), width=25,
                  command=self.open_bot_level_menu).pack(pady=5)

        tk.Button(frame, text="Joueur 1 VS Joueur 2",
                  font=("Arial", 12), width=25,
                  command=self.start_pvp).pack(pady=5)

        tk.Button(frame, text="Quitter",
                  font=("Arial", 12), width=25,
                  command=self.root.quit).pack(pady=5)

    def open_bot_level_menu(self):
        for w in self.root.winfo_children():
            if not isinstance(w, tk.Menu):
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

    # ---------- Lancement modes ----------

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
        self.player1_name = simpledialog.askstring("Joueur 1", "Prénom du joueur 1 (X) :") or "Joueur 1"
        self.player2_name = simpledialog.askstring("Joueur 2", "Prénom du joueur 2 (O) :") or "Joueur 2"
        self.current_symbol = "X"
        self.start_game_board()

    # ---------- Plateau ----------

    def start_game_board(self):
        for w in self.root.winfo_children():
            if not isinstance(w, tk.Menu):
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
        tk.Label(info_frame, text=f"Points : {self.points}", font=("Arial", 10)).pack()

        self.turn_label = tk.Label(self.root, font=("Arial", 11))
        self.turn_label.pack(pady=2)
        self.update_turn_label()

        grid_frame = tk.Frame(self.root)
        grid_frame.pack()

        theme_info = self.board_themes.get(self.board_theme, self.board_themes["Classique"])
        bg_btn = theme_info["bg"]
        fg_btn = theme_info["fg"]

        for i in range(9):
            btn = tk.Button(
                grid_frame,
                text="",
                font=("Arial", 24),
                width=3,
                height=1,
                bg=bg_btn,
                fg=fg_btn,
                command=lambda idx=i: self.on_cell_clicked(idx)
            )
            btn.grid(row=i // 3, column=i % 3)
            self.buttons.append(btn)

    def update_turn_label(self):
        if self.mode == "pvp":
            if self.current_symbol == "X":
                self.turn_label.config(text=f"Au tour de \"{self.player1_name}\" (X)")
            else:
                self.turn_label.config(text=f"Au tour de \"{self.player2_name}\" (O)")
        else:
            self.turn_label.config(text="Clique sur une case pour jouer")

    # ---------- Clics ----------

    def on_cell_clicked(self, index):
        if self.board[index] != EMPTY:
            return

        if self.mode in ("bot_random", "bot_level"):
            self.board[index] = HUMAN
            self.buttons[index]["text"] = HUMAN
            self.buttons[index]["fg"] = self.symbol_color_X

            if self.check_end_of_game():
                return

            self.turn_label.config(text="Tour du bot...")
            self.root.after(300, self.bot_play)
        else:
            self.board[index] = self.current_symbol
            self.buttons[index]["text"] = self.current_symbol
            if self.current_symbol == "X":
                self.buttons[index]["fg"] = self.symbol_color_X
            else:
                self.buttons[index]["fg"] = self.symbol_color_O

            if self.check_end_of_game_pvp():
                return

            self.current_symbol = "O" if self.current_symbol == "X" else "X"
            self.update_turn_label()

    # ---------- IA ----------

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
        if self.mode in ("bot_random", "bot_level"):
            self.turn_label.config(text="À ton tour de jouer")

    def bot_easy(self):
        moves = self.available_moves()
        if not moves:
            return
        choice = random.choice(moves)
        self.board[choice] = BOT
        self.buttons[choice]["text"] = BOT
        self.buttons[choice]["fg"] = self.symbol_color_O

    def bot_medium(self):
        moves = self.available_moves()
        if not moves:
            return
        # gagner
        for pos in moves:
            backup = self.board[pos]
            self.board[pos] = BOT
            if self.check_winner() == BOT:
                self.buttons[pos]["text"] = BOT
                self.buttons[pos]["fg"] = self.symbol_color_O
                return
            self.board[pos] = backup
        # bloquer
        for pos in moves:
            backup = self.board[pos]
            self.board[pos] = HUMAN
            if self.check_winner() == HUMAN:
                self.board[pos] = BOT
                self.buttons[pos]["text"] = BOT
                self.buttons[pos]["fg"] = self.symbol_color_O
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
            self.buttons[best_move]["fg"] = self.symbol_color_O

    # ---------- Fin de partie ----------

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
            self.points += 5
            self.save_all()
            self.end_game_dialog("Match nul. +5 points")
        elif result == HUMAN:
            self.points += 10
            self.save_all()
            self.end_game_dialog("Tu as gagné ! +10 points")
        else:
            self.end_game_dialog("Le bot a gagné.")
        return True

    def check_end_of_game_pvp(self):
        result = self.check_winner()
        if result is None:
            return False

        if result == "draw":
            self.points += 5
            self.save_all()
            self.end_game_dialog("Match nul. +5 points")
        else:
            winner_name = self.player1_name if result == "X" else self.player2_name
            self.points += 10
            self.save_all()
            self.end_game_dialog(f"{winner_name} ({result}) a gagné ! +10 points")
        return True


if __name__ == "__main__":
    root = tk.Tk()
    app = MorpionV5App(root)
    root.mainloop()
