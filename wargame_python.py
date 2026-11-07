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


# Verification de la validite physique d'un mouvement
# Renvoie 0 si le coup est valide, 1 sinon
def f_test_mouvement(plateau, l1, c1, l2, c2, couleur):
    # 1. Controle des limites de la grille (0 a 9)
    if (l1 < 0 or l1 >= NB_LIGNES or l2 < 0 or l2 >= NB_LIGNES or
            c1 < 0 or c1 >= NB_COLONNES or c2 < 0 or c2 >= NB_COLONNES):
        return 1

    # 2. On verifie qu'il y a bien une piece sur la case de depart et qu'elle appartient au joueur
    if (plateau[l1 * NB_COLONNES + c1].valeur == 0 or
            plateau[l1 * NB_COLONNES + c1].couleur != couleur):
        return 1

    # 3. Interdiction de capturer une piece de sa propre armee
    if plateau[l2 * NB_COLONNES + c2].couleur == plateau[l1 * NB_COLONNES + c1].couleur:
        return 1

    # 4. Deplacement autorise uniquement vers les 8 cases adjacentes (distance max de 1 case)
    # et interdiction de rester immobile sur place (l1 == l2 and c1 == c2)
    if (l1 - l2 > 1 or l2 - l1 > 1 or c1 - c2 > 1 or c2 - c1 > 1 or
            (l1 == l2 and c1 == c2)):
        return 1

    return 0

# Parcours du plateau pour lister tous les coups legaux possibles du joueur
def generer_coups(plateau, joueur):
    liste = None
    # On scanne chaque case du plateau
    for l1 in range(NB_LIGNES):
        for c1 in range(NB_COLONNES):
            # Si la case contient un pion du joueur actif
            if plateau[l1 * NB_COLONNES + c1].couleur == joueur:
                # On teste les 8 directions relatives autour de la piece
                for dl in range(-1, 2):
                    for dc in range(-1, 2):
                        if dl == 0 and dc == 0:
                            continue  # Rester sur place n'est pas un deplacement
                        l2 = l1 + dl
                        c2 = c1 + dc
                        # Si le mouvement respecte les regles, on l'ajoute en tete de liste
                        if f_test_mouvement(plateau, l1, c1, l2, c2, joueur) == 0:
                            liste = ajouter_coup(liste, l1, c1, l2, c2)
    return liste

# Test rapide d'affichage
if __name__ == "__main__":
    plateauDeJeu = f_init_plateau()
    f_affiche_plateau(plateauDeJeu)

    # Test de generation pour les Noirs (1) et les Blancs (-1)
    coups_noirs = generer_coups(plateauDeJeu, 1)
    nb_noirs = 0
    cur = coups_noirs
    while cur:
        nb_noirs += 1
        cur = cur.suivant

    coups_blancs = generer_coups(plateauDeJeu, -1)
    nb_blancs = 0
    cur = coups_blancs
    while cur:
        nb_blancs += 1
        cur = cur.suivant


    print(f"- Coups legaux generes pour les Noirs (x) au depart : {nb_noirs} coup")
    print(f"- Coups legaux generes pour les Blancs (o) au depart : {nb_blancs} coup")