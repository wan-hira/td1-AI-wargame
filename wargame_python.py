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
    # Controle des limites de la grille (0 a 9)
    if (l1 < 0 or l1 >= NB_LIGNES or l2 < 0 or l2 >= NB_LIGNES or
            c1 < 0 or c1 >= NB_COLONNES or c2 < 0 or c2 >= NB_COLONNES):
        return 1

    # On verifie qu'il y a bien une piece sur la case de depart et qu'elle appartient au joueur
    if (plateau[l1 * NB_COLONNES + c1].valeur == 0 or
            plateau[l1 * NB_COLONNES + c1].couleur != couleur):
        return 1

    # Interdiction de capturer une piece de sa propre armee
    if plateau[l2 * NB_COLONNES + c2].couleur == plateau[l1 * NB_COLONNES + c1].couleur:
        return 1

    # Deplacement autorise uniquement vers les 8 cases adjacentes (distance max de 1 case)
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

# Resolution d'un combat sur la case (l, c)
# On passe le plateau local en argument pour ne pas impacter la grille globale
def f_bataille(plateau, l, c):
    mini = 0 if l - 1 < 0 else l - 1
    maxi = NB_LIGNES - 1 if l + 1 > NB_LIGNES - 1 else l + 1
    minj = 0 if c - 1 < 0 else c - 1
    maxj = NB_COLONNES - 1 if c + 1 > NB_COLONNES - 1 else c + 1

    somme = 0
    # Somme des forces presentes autour de la case
    for i in range(mini, maxi + 1):
        for j in range(minj, maxj + 1):
            somme += plateau[i * NB_COLONNES + j].couleur * plateau[i * NB_COLONNES + j].valeur

    # On soustrait la piece cible du defenseur
    somme -= plateau[l * NB_COLONNES + c].couleur * plateau[l * NB_COLONNES + c].valeur

    if somme < 0:
        return -1
    if somme > 0:
        return 1

    # En cas d'egalite, le defenseur conserve la case
    return plateau[l * NB_COLONNES + c].couleur

# Deplacement physique d'une piece et resolution si combat
def f_bouge_piece(plateau, l1, c1, l2, c2, couleur):
    if f_test_mouvement(plateau, l1, c1, l2, c2, couleur) != 0:
        return 1

    # Case vide a l'arrivee
    if plateau[l2 * NB_COLONNES + c2].valeur == 0:
        plateau[l2 * NB_COLONNES + c2].couleur = plateau[l1 * NB_COLONNES + c1].couleur
        plateau[l2 * NB_COLONNES + c2].valeur = plateau[l1 * NB_COLONNES + c1].valeur
        plateau[l1 * NB_COLONNES + c1].couleur = 0
        plateau[l1 * NB_COLONNES + c1].valeur = 0
    else:
        gagnant = f_bataille(plateau, l2, c2)
        # Victoire de l'attaquant : il prend la place
        if gagnant == couleur:
            plateau[l2 * NB_COLONNES + c2].couleur = plateau[l1 * NB_COLONNES + c1].couleur
            plateau[l2 * NB_COLONNES + c2].valeur = plateau[l1 * NB_COLONNES + c1].valeur
            plateau[l1 * NB_COLONNES + c1].couleur = 0
            plateau[l1 * NB_COLONNES + c1].valeur = 0
        # Defaite de l'attaquant : sa piece est eliminee
        elif gagnant != 0:
            plateau[l1 * NB_COLONNES + c1].couleur = 0
            plateau[l1 * NB_COLONNES + c1].valeur = 0

    return 0

# Test d'invasion de ligne de fond
def test_victoire(p):
    for i in range(NB_COLONNES):
        if p[0 * NB_COLONNES + i].couleur == 1:
            return 1
        if p[9 * NB_COLONNES + i].couleur == -1:
            return -1
    return 0

# Verification de l'etat final de la partie sur le plateau principal
def f_gagnant():
    global plateauDeJeu
    somme1 = 0
    somme2 = 0

    # Ligne adverse atteinte
    for i in range(NB_COLONNES):
        if plateauDeJeu[i].couleur == 1:
            return 1
        if plateauDeJeu[(NB_LIGNES - 1) * NB_COLONNES + i].couleur == -1:
            return -1

    # Comptage des pieces restantes
    for i in range(NB_LIGNES):
        for j in range(NB_COLONNES):
            if plateauDeJeu[i * NB_COLONNES + j].couleur == 1:
                somme1 += 1
            if plateauDeJeu[i * NB_COLONNES + j].couleur == -1:
                somme2 += 1

    if somme1 == 0:
        return -1
    if somme2 == 0:
        return 1

    return 0

# Comptage du nombre total de pieces d'un joueur
def f_nbPions(jeu, joueur):
    nb_pion = 0
    for i in range(NB_COLONNES):
        for j in range(NB_LIGNES):
            if jeu[i * NB_COLONNES + j].couleur == joueur:
                nb_pion += 1
    return nb_pion


# Somme des points de force de toutes les pieces d'un joueur
def f_valeur(jeu, joueur):
    valeur = 0
    for i in range(NB_COLONNES):
        for j in range(NB_LIGNES):
            if jeu[i * NB_COLONNES + j].couleur == joueur:
                valeur += jeu[i * NB_COLONNES + j].valeur
    return valeur

# Heuristique d'evaluation de position
def f_eval(jeu, joueur, profondeur):
    adversaire = -joueur
    score = 0

    # Victoire ou defaite par percee de la ligne adverse
    for i in range(NB_COLONNES):
        # Pour les Noirs (1), l'objectif est la ligne 0
        if jeu[0 * NB_COLONNES + i].couleur == 1:
            return (5000 + profondeur) if joueur == 1 else (-5000 - profondeur)
        # Pour les Blancs (-1), l'objectif est la ligne 9
        if jeu[(NB_LIGNES - 1) * NB_COLONNES + i].couleur == -1:
            return (5000 + profondeur) if joueur == -1 else (-5000 - profondeur)

    # Victoire ou defaite par extermination complete
    pions_joueur = f_nbPions(jeu, joueur)
    pions_adv = f_nbPions(jeu, adversaire)

    if pions_adv == 0:
        return 5000 + profondeur
    if pions_joueur == 0:
        return -5000 - profondeur

    # Equilibre
    val_joueur = f_valeur(jeu, joueur)
    val_adv = f_valeur(jeu, adversaire)
    score += (val_joueur - val_adv) * 20
    score += (pions_joueur - pions_adv) * 10

    # Avancement territorial et securite de la ligne arriere
    avancement = 0
    danger_fond = 0

    for i in range(NB_LIGNES):
        for j in range(NB_COLONNES):
            p = jeu[i * NB_COLONNES + j]
            if p.couleur == joueur:
                if joueur == 1:
                    avancement += (9 - i)  # Distance parcourue vers le bas
                else:
                    avancement += i        # Distance parcourue vers le haut
            elif p.couleur == adversaire:
                if adversaire == 1:
                    avancement -= (9 - i)
                    # Alerte si un pion adverse approche a 1 ou 2 cases de notre ligne 0
                    if i <= 2:
                        danger_fond += (3 - i) * 60
                else:
                    avancement -= i
                    # Alerte si un pion adverse approche a 1 ou 2 cases de notre ligne 9
                    if i >= 7:
                        danger_fond += (i - 6) * 60

    score += avancement * 2
    score -= danger_fond

    return score

#fonction min simule le tour de l'adversaire qui cherche a minimiser notre score
def f_min(plateau, profondeur, joueur_min, joueur_ia):
    global nb_noeuds_visites
    nb_noeuds_visites += 1

    # Condition d'arret : profondeur atteinte ou victoire immediate
    if profondeur <= 0 or test_victoire(plateau) != 0:
        return f_eval(plateau, joueur_ia, profondeur)

    meilleur_score = INFINI
    coups = generer_coups(plateau, joueur_min)
    courant = coups

    if coups is None:
        return f_eval(plateau, joueur_ia, profondeur)

    copie = [Pion(0, 0) for _ in range(NB_LIGNES * NB_COLONNES)]

    while courant is not None:
        # Simulation du coup sur une copie locale
        f_copie_plateau(plateau, copie)
        f_bouge_piece(copie, courant.coup.l1, courant.coup.c1, courant.coup.l2, courant.coup.c2, joueur_min)

        # Appel recursif vers max pour le tour suivant
        score = f_max(copie, profondeur - 1, -joueur_min, joueur_ia)

        if score < meilleur_score:
            meilleur_score = score

        courant = courant.suivant

    liberer_coups(coups)
    return meilleur_score

#fonction MAX qui simule notre tour ou l'on cherche a maximiser notre score
def f_max(plateau, profondeur, joueur_max, joueur_ia):
    global nb_noeuds_visites
    nb_noeuds_visites += 1

    # Condition d'arret : profondeur atteinte ou victoire immediate
    if profondeur <= 0 or test_victoire(plateau) != 0:
        return f_eval(plateau, joueur_ia, profondeur)

    valeur_max = -INFINI
    coups = generer_coups(plateau, joueur_max)
    courant = coups

    if coups is None:
        return f_eval(plateau, joueur_ia, profondeur)

    copie = [Pion(0, 0) for _ in range(NB_LIGNES * NB_COLONNES)]

    while courant is not None:
        # Simulation du coup sur une copie locale
        f_copie_plateau(plateau, copie)
        f_bouge_piece(copie, courant.coup.l1, courant.coup.c1, courant.coup.l2, courant.coup.c2, joueur_max)

        # Appel recursif vers MIN pour le contre de l'adversaire
        v = f_min(copie, profondeur - 1, -joueur_max, joueur_ia)
        if v > valeur_max:
            valeur_max = v

        courant = courant.suivant

    liberer_coups(coups)
    return valeur_max

# Test
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


    print(f"- Coups legaux generes pour les Noirs (x) au depart : {nb_noirs} coups")
    print(f"- Coups legaux generes pour les Blancs (o) au depart : {nb_blancs} coups")
    print(f"- Verification victoire initiale : {test_victoire(plateauDeJeu)}")
    print(f"- Verification f_gagnant initial : {f_gagnant()}")
    print(f"- Pions joueur 1 (x) : {f_nbPions(plateauDeJeu, 1)} (force totale : {f_valeur(plateauDeJeu, 1)})")
    print(f"- Pions joueur -1 (o) : {f_nbPions(plateauDeJeu, -1)} (force totale : {f_valeur(plateauDeJeu, -1)})")
    print(f"- Evaluation initiale pour joueur 1 (prof 3) : {f_eval(plateauDeJeu, 1, 3)}")
    nb_noeuds_visites = 0
    # Test d'une exploration Minimax a profondeur 1 pour verifier la recursion
    score_test = f_max(plateauDeJeu, 1, 1, 1)
    print(f"- Exploration Minimax (prof 1) score : {score_test}")
    print(f"- Noeuds visites : {nb_noeuds_visites}")