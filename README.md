# Master Morpion – SAE Piloter un projet informatique

Master Morpion est un jeu de morpion stylisé développé en Python/Tkinter dans le cadre du TP R502 « Piloter un projet informatique ».  
Le jeu propose plusieurs modes locaux, une IA à trois niveaux de difficulté, un système de points persistants et une boutique de personnalisations (plateaux et couleurs).

Dépôt GitHub : https://github.com/mous7149110-png/SAE-piloter/

## Contexte du projet

Ce projet est réalisé dans le cadre de la SAE / TP R502 « Piloter un projet informatique ».

Objectifs pédagogiques :

- Mettre en pratique une démarche agile (Kanban, sprints courts).
- Utiliser un outil de gestion de projet type Trello.
- Versionner le code sur GitHub avec un historique lisible.
- Livrer une solution « as code » facilement exécutable (Python).

Contrainte initiale du sujet :

> Créer un morpion stylisé jouable à deux sur une même machine ou à distance (mode en ligne).

Pendant la conception, nous avons envisagé un mode en ligne client/serveur.  
Cependant, l’absence de VPS et de solution d’hébergement stable nous a amené à **abandonner la partie en ligne** pour cette version, afin de concentrer les efforts sur :

- La qualité des modes locaux.
- Une IA solide (jusqu’à minimax).
- Une expérience utilisateur travaillée (design + boutique).

## Fonctionnalités

### Modes de jeu

- Joueur vs Bot aléatoire.
- Joueur vs Bot avec choix de difficulté :
  - Facile : coups aléatoires.
  - Moyen : heuristique (tente de gagner ou bloque l’adversaire).
  - Difficile : algorithme minimax (IA quasi imbattable).
- Joueur 1 vs Joueur 2 sur la même machine (PvP local).

### Système de points

- +10 points par victoire.
- +5 points par match nul.
- Points sauvegardés localement dans `points.json`.
- Affichage des points :
  - Dans le menu principal.
  - Via l’onglet `!` → « Mes points ».

### Boutique

- **Plateau de jeu** :
  - 15 thèmes de plateau (Classique, Sombre, Océan, Forêt, Désert, Neige, Lave, Violet néon, Cyber, Pastel, Noir & Or, Gris métal, Bleu nuit, Vert pomme, Retro Game).
- **Couleur des symboles** :
  - 15 couleurs pour le Joueur (X).
  - 15 couleurs pour le Bot (O).

Principes :

- Chaque thème/couleur a un coût en points (ou est gratuit).
- Une fois acheté, un élément devient **« Acquis »** et peut être re-sélectionné à tout moment sans repayer.
- Les achats et l’état de possession sont sauvegardés dans `points.json`.

### Interface utilisateur

- Titre de la fenêtre : **Master Morpion**.
- Titre du menu principal : **Have fun, Have Morpion !**.
- Palette de couleurs sobre :
  - Fond sombre (`#1b1d2b`).
  - Texte clair (`#edf2f4`).
- Boutons arrondis personnalisés (classe `RoundedButton` basée sur `Canvas` Tkinter).
- Menus :

  - **Menu `!` :**
    - « Mes points » : affiche le total de points actuel.
    - « Règle du jeu » : rappel des règles simplifiées du morpion.
    - « Réinitialiser le compte » : remet à zéro les points, les achats et supprime `points.json` après confirmation.

  - **Menu `Boutique` :**
    - « Plateau de jeu » : choix/achat des thèmes.
    - « Couleur des symboles » : choix/achat des couleurs Joueur/Bot.

## Installation

### Prérequis

- Python 3.10 ou supérieur (testé avec Python 3.11).
- Tkinter (inclus par défaut avec la plupart des distributions Python).
- Aucun module externe supplémentaire n’est requis.

### Récupérer le projet

git clone https://github.com/mous7149110-png/SAE-piloter.git
cd SAE-piloter


### Lancer le jeu

python Master Morpion.py

- Au premier lancement, un fichier `points.json` est créé automatiquement pour stocker :
  - Le nombre de points.
  - Les thèmes et couleurs déjà achetés.

## Utilisation

### Menu principal

Une fois `Master Morpion.py` lancé, le menu principal s’affiche :

- **Joueur VS bot aléatoire**
- **Choix difficulté du bot**
- **Joueur 1 VS Joueur 2**
- **Quitter**

Le nombre de points actuels est visible sous le titre.

### Modes de jeu

1. **Joueur VS Bot aléatoire**  
   Le bot joue des coups entièrement aléatoires.

2. **Choix difficulté du bot**  
   Propose 3 niveaux :
   - Facile : coups aléatoires.
   - Moyen : essaie de gagner si possible, sinon bloque l’adversaire, sinon aléatoire.
   - Difficile : utilise l’algorithme minimax pour choisir le meilleur coup.

3. **Joueur 1 VS Joueur 2**  
   Deux joueurs humains jouent chacun leur tour sur le même clavier/souris.

### Points et récompenses

À la fin de chaque partie :

- Victoire → +10 points.
- Match nul → +5 points.
- Défaite → 0 point.

Les points sont automatiquement mis à jour et sauvegardés.

### Boutique

1. Ouvrir le menu **Boutique** → « Plateau de jeu » :
   - Liste des 15 thèmes avec soit le coût, soit « Acquis ».
   - Un clic :
     - Si gratuit ou déjà acquis → applique le thème.
     - Si coût > 0 et points suffisants → déduit les points, marque « Acquis », applique le thème.
     - Si points insuffisants → message d’erreur.

2. Ouvrir **Boutique** → « Couleur des symboles » :
   - Deux sections :
     - Joueur (X)
     - Bot (O)
   - Chaque couleur affiche son coût ou « Acquis ».
   - Même logique d’achat / sélection que pour les plateaux.

### Menu `!`

- **Mes points** :  
  Affiche une boîte de dialogue avec le total de points actuel.

- **Règle du jeu** :  
  Rappelle les règles simplifiées du morpion :
  - Grille 3x3.
  - Un joueur joue les X, l’autre les O.
  - Chaque joueur joue à tour de rôle dans une case vide.
  - Le premier qui aligne 3 symboles (ligne, colonne, diagonale) gagne.
  - Si la grille est pleine sans alignement, la partie est nulle.

- **Réinitialiser le compte** :  
  - Affiche une confirmation : « Êtes-vous sûr de vouloir tout supprimer ? ».
  - Si **Oui** :
    - Points remis à 0.
    - Thèmes et couleurs possédés effacés.
    - Fichier `points.json` supprimé puis recréé proprement.
  - Si **Non** :
    - Aucun changement, retour au menu principal.


## Architecture du code

### Fichiers principaux

- `Master Morpion.py`  
  - Interface graphique Tkinter.
  - Gestion du plateau et des modes de jeu.
  - IA (facile, moyen, difficile/minimax).
  - Gestion des points (victoire/nul).
  - Système de boutique (plateaux + couleurs).
  - Sauvegarde/chargement dans `points.json`.
  - Classe `RoundedButton` pour les boutons arrondis.

- `points.json` (généré automatiquement)  
  Exemple de structure simplifiée :

{
"points": 35,
"owned_boards": ["Classique", "Sombre"],
"owned_player_colors": ["Rouge", "Bleu"],
"owned_bot_colors": ["Vert"]
}

### IA

- **Facile** : `random.choice` sur la liste des coups possibles.
- **Moyen** :
1. Vérifie si le bot peut gagner en un coup.
2. Sinon, vérifie si le joueur peut gagner en un coup et bloque.
3. Sinon, joue un coup aléatoire.
- **Difficile** : Minimax complet sur la grille 3x3 :
- Explore récursivement toutes les possibilités.
- Retourne le score optimal pour l’IA.
- Rend le bot quasiment imbattable.
