import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import json
import os

EMPTY = " "
HUMAN = "X"
BOT = "O"

POINTS_FILE = "points.json"


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None,
                 bg="#2b2d42", fg="#edf2f4",
                 hover_bg="#3b3f5c",
                 radius=12, padding_x=20, padding_y=8, font=("Segoe UI", 11, "bold"),
                 *args, **kwargs):
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.command = command
        self.radius = radius
        self.padding_x = padding_x
        self.padding_y = padding_y
        self.text = text
        self.font = font

        tk.Canvas.__init__(self, parent, highlightthickness=0, bg=parent["bg"], *args, **kwargs)

        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.draw_button(self.bg)

    def draw_button(self, color):
        self.delete("all")
        tmp = tk.Label(self, text=self.text, font=self.font)
        tmp.update_idletasks()
        w = tmp.winfo_reqwidth() + 2 * self.padding_x
        h = tmp.winfo_reqheight() + 2 * self.padding_y

        r = self.radius
        self.config(width=w, height=h)

        self.create_arc((0, 0, 2 * r, 2 * r), start=90, extent=90, fill=color, outline=color)
        self.create_arc((w - 2 * r, 0, w, 2 * r), start=0, extent=90, fill=color, outline=color)
        self.create_arc((0, h - 2 * r, 2 * r, h), start=180, extent=90, fill=color, outline=color)
        self.create_arc((w - 2 * r, h - 2 * r, w, h), start=270, extent=90, fill=color, outline=color)
        self.create_rectangle((r, 0, w - r, h), fill=color, outline=color)
        self.create_rectangle((0, r, w, h - r), fill=color, outline=color)

        self.create_text(w // 2, h // 2, text=self.text, fill=self.fg, font=self.font)

    def on_click(self, event):
        if self.command:
            self.command()

    def on_enter(self, event):
        self.draw_button(self.hover_bg)

    def on_leave(self, event):
        self.draw_button(self.bg)


class MorpionV5App:
    def __init__(self, root):
        self.root = root
        self.root.title("Master Morpion")
        self.root.configure(bg="#1b1d2b")
        self.board = [EMPTY] * 9
        self.buttons = []

        self.mode = "bot_random"
        self.level = 1

        self.player1_name = "Joueur 1"
        self.player2_name = "Joueur 2"
        self.current_symbol = "X"

        self.points = 0
        self.load_points()

        self.board_themes = {
            "Classique":      {"bg": "#2b2d42", "fg": "#edf2f4", "cost": 0},
            "Sombre":        {"bg": "#12131c", "fg": "#edf2f4", "cost": 20},
            "Océan":         {"bg": "#1b4965", "fg": "#edf2f4", "cost": 20},
            "Forêt":         {"bg": "#2b9348", "fg": "#f1faee", "cost": 20},
            "Désert":        {"bg": "#f4a261", "fg": "#1d3557", "cost": 20},
            "Neige":         {"bg": "#e0fbfc", "fg": "#1d3557", "cost": 20},
            "Lave":          {"bg": "#9d0208", "fg": "#ffdd57", "cost": 25},
            "Violet néon":   {"bg": "#3a0ca3", "fg": "#f72585", "cost": 25},
            "Cyber":         {"bg": "#0b090a", "fg": "#00ff9f", "cost": 25},
            "Pastel":        {"bg": "#ffddd2", "fg": "#264653", "cost": 20},
            "Noir & Or":     {"bg": "#000000", "fg": "#ffd700", "cost": 30},
            "Gris métal":    {"bg": "#6c757d", "fg": "#f8f9fa", "cost": 20},
            "Bleu nuit":     {"bg": "#03045e", "fg": "#caf0f8", "cost": 20},
            "Vert pomme":    {"bg": "#80ed99", "fg": "#22577a", "cost": 20},
            "Retro Game":    {"bg": "#22223b", "fg": "#f2e9e4", "cost": 25},
        }
        self.board_theme = "Classique"

        self.symbol_colors_player = {
            "Noir":      ("#edf2f4", 0),
            "Rouge":     ("#e63946", 10),
            "Bleu":      ("#1d3557", 10),
            "Vert":      ("#2a9d8f", 10),
            "Orange":    ("#f4a261", 10),
            "Violet":    ("#7209b7", 10),
            "Rose":      ("#ff006e", 10),
            "Cyan":      ("#00b4d8", 10),
            "Jaune":     ("#ffbe0b", 10),
            "Marron":    ("#6f4518", 10),
            "Turquoise": ("#06d6a0", 10),
            "Gris":      ("#adb5bd", 10),
            "Blanc":     ("#ffffff", 10),
            "Or":        ("#ffd700", 15),
            "Arc ciel":  ("#ff006e", 15),
        }
        self.symbol_colors_bot = dict(self.symbol_colors_player)

        self.symbol_color_X = "#edf2f4"
        self.symbol_color_O = "#edf2f4"

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
        menubar = tk.Menu(self.root, bg="#1b1d2b", fg="#edf2f4", tearoff=0)

        info_menu = tk.Menu(menubar, tearoff=0, bg="#2b2d42", fg="#edf2f4")
        info_menu.add_command(label="Mes points", command=self.show_points)
        info_menu.add_command(label="Règle du jeu", command=self.show_rules)
        info_menu.add_separator()
        info_menu.add_command(label="Réinitialiser le compte", command=self.reset_account)
        menubar.add_cascade(label="!", menu=info_menu)

        shop_menu = tk.Menu(menubar, tearoff=0, bg="#2b2d42", fg="#edf2f4")
        shop_menu.add_command(label="Plateau de jeu", command=self.open_shop_board)
        shop_menu.add_command(label="Couleur des symboles", command=self.open_shop_symbols)
        menubar.add_cascade(label="Boutique", menu=shop_menu)

        self.root.config(menu=menubar)

    def show_points(self):
        messagebox.showinfo("Mes points", f"Tu as actuellement {self.points} points.")

    def show_rules(self):
        rules = (
            "Règles simplifiées du morpion :\n\n"
            "- Le jeu se joue à 2 joueurs sur une grille de 3x3.\n"
            "- Un joueur joue les X, l’autre joue les O.\n"
            "- À tour de rôle, chaque joueur place son symbole dans une case vide.\n"
            "- Le premier joueur qui aligne 3 symboles identiques gagne :\n"
            "  • en ligne, en colonne ou en diagonale.\n"
            "- Si toutes les cases sont remplies sans alignement, la partie est nulle."
        )
        messagebox.showinfo("Règle du jeu", rules)

    def reset_account(self):
        rep = messagebox.askyesno(
            "Réinitialiser le compte",
            "Êtes-vous sûr de vouloir tout supprimer ?\n\n"
            "Tous vos points et tous vos achats de la boutique seront définitivement perdus."
        )
        if not rep:
            self.create_main_menu()
            return

        self.points = 0
        self.owned_board_themes = set()
        self.owned_player_colors = set()
        self.owned_bot_colors = set()
        self.board_theme = "Classique"
        self.symbol_color_X = "#edf2f4"
        self.symbol_color_O = "#edf2f4"

        try:
            if os.path.exists(POINTS_FILE):
                os.remove(POINTS_FILE)
        except Exception:
            pass

        self.save_all()
        messagebox.showinfo("Compte réinitialisé", "Votre compte a été entièrement réinitialisé.")
        self.create_main_menu()

    # ---------- Boutique : Plateau ----------

    def open_shop_board(self):
        win = tk.Toplevel(self.root)
        win.title("Boutique - Plateau de jeu")
        win.configure(bg="#1b1d2b")

        tk.Label(win, text=f"Points disponibles : {self.points}",
                 font=("Segoe UI", 11), bg="#1b1d2b", fg="#edf2f4").pack(pady=5)

        frame = tk.Frame(win, bg="#1b1d2b")
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
            btn = RoundedButton(frame, text=text, command=make_action(name),
                                bg="#2b2d42", hover_bg="#3b3f5c", fg="#edf2f4",
                                font=("Segoe UI", 10, "bold"))
            btn.grid(row=row, column=col, padx=5, pady=3, sticky="w")
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
        win.configure(bg="#1b1d2b")

        tk.Label(win, text=f"Points disponibles : {self.points}",
                 font=("Segoe UI", 11), bg="#1b1d2b", fg="#edf2f4").pack(pady=5)

        notebook = tk.Frame(win, bg="#1b1d2b")
        notebook.pack(padx=10, pady=5)

        frame_player = tk.LabelFrame(notebook, text="Couleurs Joueur (X)",
                                     bg="#1b1d2b", fg="#edf2f4")
        frame_player.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        frame_bot = tk.LabelFrame(notebook, text="Couleurs Bot (O)",
                                  bg="#1b1d2b", fg="#edf2f4")
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
            btn = RoundedButton(frame_player, text=txt,
                                command=make_player_action(name, color, cost),
                                bg="#2b2d42", hover_bg="#3b3f5c", fg=color,
                                font=("Segoe UI", 9, "bold"))
            btn.grid(row=row, column=0, padx=3, pady=2, sticky="w")
            row += 1

        row = 0
        for name, (color, cost) in self.symbol_colors_bot.items():
            if cost == 0 or name in self.owned_bot_colors:
                txt = f"{name} (Acquis)"
            else:
                txt = f"{name} ({cost} pts)"
            btn = RoundedButton(frame_bot, text=txt,
                                command=make_bot_action(name, color, cost),
                                bg="#2b2d42", hover_bg="#3b3f5c", fg=color,
                                font=("Segoe UI", 9, "bold"))
            btn.grid(row=row, column=0, padx=3, pady=2, sticky="w")
            row += 1

    # ---------- Menus principaux ----------

    def create_main_menu(self):
        for w in self.root.winfo_children():
            if not isinstance(w, tk.Menu):
                w.destroy()

        frame = tk.Frame(self.root, bg="#1b1d2b")
        frame.pack(pady=30)

        tk.Label(frame, text="Have a pion, Have a morpion !",
                 font=("Segoe UI", 20, "bold"),
                 bg="#1b1d2b", fg="#edf2f4").pack(pady=10)

        

        RoundedButton(frame, text="Joueur VS bot aléatoire",
                      command=self.start_bot_random).pack(pady=7)
        RoundedButton(frame, text="Choix difficulté du bot",
                      command=self.open_bot_level_menu).pack(pady=7)
        RoundedButton(frame, text="Joueur 1 VS Joueur 2",
                      command=self.start_pvp).pack(pady=7)
        RoundedButton(frame, text="Quitter",
                      command=self.root.quit,
                      bg="#780000", hover_bg="#9d0208").pack(pady=7)

    def open_bot_level_menu(self):
        for w in self.root.winfo_children():
            if not isinstance(w, tk.Menu):
                w.destroy()

        frame = tk.Frame(self.root, bg="#1b1d2b")
        frame.pack(pady=30)

        tk.Label(frame, text="Choix difficulté du bot",
                 font=("Segoe UI", 18, "bold"),
                 bg="#1b1d2b", fg="#edf2f4").pack(pady=10)

        self.level_var = tk.IntVar(value=self.level)

        for text, val in [("Facile", 1), ("Moyen", 2), ("Difficile", 3)]:
            tk.Radiobutton(frame, text=text, variable=self.level_var, value=val,
                           bg="#1b1d2b", fg="#edf2f4",
                           selectcolor="#2b2d42",
                           activebackground="#1b1d2b",
                           font=("Segoe UI", 11)).pack(anchor="w", padx=20)

        RoundedButton(frame, text="Lancer la partie",
                      command=self.start_bot_level).pack(pady=10)
        RoundedButton(frame, text="Retour menu principal",
                      command=self.create_main_menu,
                      bg="#343a40", hover_bg="#495057").pack(pady=5)

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

        top_frame = tk.Frame(self.root, bg="#1b1d2b")
        top_frame.pack(pady=10)

        RoundedButton(top_frame, text="Retour menu principal",
                      command=self.create_main_menu,
                      bg="#343a40", hover_bg="#495057",
                      font=("Segoe UI", 9, "bold"),
                      padding_x=12, padding_y=4).pack()

        info_frame = tk.Frame(self.root, bg="#1b1d2b")
        info_frame.pack(pady=5)

        if self.mode == "pvp":
            vs_text = f"{self.player1_name} (X) VS {self.player2_name} (O)"
        elif self.mode == "bot_random":
            vs_text = "Joueur (X) VS Bot aléatoire (O)"
        else:
            label_level = {1: "Facile", 2: "Moyen", 3: "Difficile"}[self.level]
            vs_text = f"Joueur (X) VS Bot ({label_level}) (O)"

        tk.Label(info_frame, text=vs_text,
                 font=("Segoe UI", 12),
                 bg="#1b1d2b", fg="#edf2f4").pack()
        tk.Label(info_frame, text=f"Points : {self.points}",
                 font=("Segoe UI", 10),
                 bg="#1b1d2b", fg="#8d99ae").pack()

        self.turn_label = tk.Label(self.root, font=("Segoe UI", 11),
                                   bg="#1b1d2b", fg="#edf2f4")
        self.turn_label.pack(pady=4)
        self.update_turn_label()

        grid_frame = tk.Frame(self.root, bg="#1b1d2b")
        grid_frame.pack(pady=10)

        theme_info = self.board_themes.get(self.board_theme, self.board_themes["Classique"])
        bg_btn = theme_info["bg"]
        fg_btn = theme_info["fg"]

        for i in range(9):
            btn = tk.Button(
                grid_frame,
                text="",
                font=("Segoe UI", 24, "bold"),
                width=3,
                height=1,
                bg=bg_btn,
                fg=fg_btn,
                activebackground=bg_btn,
                activeforeground=fg_btn,
                relief="flat",
                bd=0,
                command=lambda idx=i: self.on_cell_clicked(idx)
            )
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3)
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
        for pos in moves:
            backup = self.board[pos]
            self.board[pos] = BOT
            if self.check_winner() == BOT:
                self.buttons[pos]["text"] = BOT
                self.buttons[pos]["fg"] = self.symbol_color_O
                return
            self.board[pos] = backup
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
