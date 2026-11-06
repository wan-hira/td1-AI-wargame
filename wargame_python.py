#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Dimensions du plateau de wargame et constante d'infini
NB_LIGNES = 10
NB_COLONNES = 10
INFINI = 10000

# Variables globales du jeu 
algo_ia = 1  # 1 = Minimax simple, 2 = Minimax avec elagage Alpha-Beta
nb_noeuds_visites = 0  # Compteur pour mesurer l'efficacite de la recherche


# Representation d'une piece sur le plateau
# couleur : 1 pour les Noirs ('x'), -1 pour les Blancs ('o'), 0 si vide
# valeur : force de frappe du pion (de 1 a 3)
class Pion:
    def __init__(self, couleur=0, valeur=0):
        self.couleur = couleur
        self.valeur = valeur

    def copy(self):
        return Pion(self.couleur, self.valeur)


# Coordonnees d'un coup (case de depart -> case d'arrivee)
class Coup:
    def __init__(self, l1, c1, l2, c2):
        self.l1 = l1
        self.c1 = c1
        self.l2 = l2
        self.c2 = c2


# Element de liste chainee pour stocker les coups generes
# On garde le pointeur 'suivant' 
class ElementCoup:
    def __init__(self, coup, suivant=None):
        self.coup = coup
        self.suivant = suivant


# Insertion d'un nouveau coup en tete de liste
def ajouter_coup(tete, l1, c1, l2, c2):
    return ElementCoup(Coup(l1, c1, l2, c2), tete)


# Liberation de la memoire allouee pour la liste
def liberer_coups(tete):
    pass


# Conversion d'une lettre de colonne ('A'..'J') en indice (0..9)
def f_convert_char2int(c):
    if 'A' <= c <= 'Z':
        return ord(c) - ord('A')
    if 'a' <= c <= 'z':
        return ord(c) - ord('a')
    return -1


# Conversion d'un indice de colonne (0..9) en lettre ('A'..'J')
def f_convert_int2char(i):
    return chr(i + ord('A'))


# Initialisation du plateau avec la disposition officielle du sujet
def f_init_plateau():
    plateau = [Pion(0, 0) for _ in range(NB_LIGNES * NB_COLONNES)]

    # Armee des Noirs (joueur 1 / 'x') installee sur les lignes 9, 8 et 7
    plateau[9 * NB_COLONNES + 5] = Pion(1, 1)
    plateau[9 * NB_COLONNES + 6] = Pion(1, 2)
    plateau[9 * NB_COLONNES + 7] = Pion(1, 3)
    plateau[9 * NB_COLONNES + 8] = Pion(1, 2)
    plateau[9 * NB_COLONNES + 9] = Pion(1, 1)

    plateau[8 * NB_COLONNES + 0] = Pion(1, 1)
    plateau[8 * NB_COLONNES + 1] = Pion(1, 3)
    plateau[8 * NB_COLONNES + 2] = Pion(1, 3)
    plateau[8 * NB_COLONNES + 3] = Pion(1, 1)
    plateau[8 * NB_COLONNES + 6] = Pion(1, 1)
    plateau[8 * NB_COLONNES + 7] = Pion(1, 1)
    plateau[8 * NB_COLONNES + 8] = Pion(1, 1)

    plateau[7 * NB_COLONNES + 1] = Pion(1, 1)
    plateau[7 * NB_COLONNES + 2] = Pion(1, 1)

    # Armee des Blancs (joueur -1 / 'o') installee sur les lignes 0, 1 et 2
    plateau[2 * NB_COLONNES + 7] = Pion(-1, 1)
    plateau[2 * NB_COLONNES + 8] = Pion(-1, 1)

    plateau[1 * NB_COLONNES + 1] = Pion(-1, 1)
    plateau[1 * NB_COLONNES + 2] = Pion(-1, 1)
    plateau[1 * NB_COLONNES + 3] = Pion(-1, 1)
    plateau[1 * NB_COLONNES + 6] = Pion(-1, 1)
    plateau[1 * NB_COLONNES + 7] = Pion(-1, 3)
    plateau[1 * NB_COLONNES + 8] = Pion(-1, 3)
    plateau[1 * NB_COLONNES + 9] = Pion(-1, 1)

    plateau[0 * NB_COLONNES + 0] = Pion(-1, 1)
    plateau[0 * NB_COLONNES + 1] = Pion(-1, 2)
    plateau[0 * NB_COLONNES + 2] = Pion(-1, 3)
    plateau[0 * NB_COLONNES + 3] = Pion(-1, 2)
    plateau[0 * NB_COLONNES + 4] = Pion(-1, 1)

    return plateau


# Affichage textuel de la grille 10x10 avec reperes de lignes et colonnes
def f_affiche_plateau(plateau):
    print("\n    ", end="")
    for k in range(NB_COLONNES):
        print(f"{f_convert_int2char(k):>2} ", end="")
    print("\n    ", end="")
    for k in range(NB_COLONNES):
        print("-- ", end="")
    print()

    # On affiche de la ligne 9 (haut) vers la ligne 0 (bas)
    for i in range(NB_LIGNES - 1, -1, -1):
        print(f"{i:>2} ", end="")
        for j in range(NB_COLONNES):
            print("|", end="")
            p = plateau[i * NB_COLONNES + j]
            if p.couleur == -1:
                print(f"{p.valeur}o", end="")
            elif p.couleur == 1:
                print(f"{p.valeur}x", end="")
            else:
                print("  ", end="")
        print("|\n    ", end="")
        for k in range(NB_COLONNES):
            print("-- ", end="")
        print()
    print("    ", end="")


# Copie case par case d'un plateau vers un autre pour les simulations
def f_copie_plateau(source, destination):
    for i in range(NB_LIGNES):
        for j in range(NB_COLONNES):
            idx = i * NB_COLONNES + j
            destination[idx].couleur = source[idx].couleur
            destination[idx].valeur = source[idx].valeur


# Creation d'un plateau vierge
def f_raz_plateau():
    return [Pion(0, 0) for _ in range(NB_LIGNES * NB_COLONNES)]


# Test rapide d'affichage 
if __name__ == "__main__":
    plateauDeJeu = f_init_plateau()
    f_affiche_plateau(plateauDeJeu)
    print("\nInitialisation et affichage valides.")