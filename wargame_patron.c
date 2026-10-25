

#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#define NB_LIGNES 10
#define NB_COLONNES 10
#define INFINI 10000


/*#define DEBUG*/

int algo_ia = 1; // 1 = Minimax classique, 2 = Alpha-Beta
long nb_noeuds_visites = 0; // Compteur de nœuds explorés

typedef struct pion_s
{
	int couleur;
	int valeur;
}Pion;

Pion *plateauDeJeu;

/** Structure coup **/
typedef struct coup_s {
	int l1, c1; //départ
	int l2, c2; //destination
} Coup;

/**
 *Structure Liste chaïnée des coups
 *
 **/
typedef struct liste_coups_s {
	Coup coup;
	struct liste_coups_s *suivant;
} ElementCoup, *ListeCoups;

//les prototypes des fonctions
void f_affiche_plateau(Pion *plateau);
int f_convert_char2int(char c);
char f_convert_int2char(int i);
ListeCoups ajouter_coup(ListeCoups tete, int l1, int c1, int l2, int c2);
void liberer_coups(ListeCoups tete);
ListeCoups generer_coups(Pion *plateau, int joueur);
int f_max(Pion *plateau, int profondeur, int joueur_max, int joueur_ia);
int f_min(Pion *plateau, int profondeur, int joueur_min, int joueur_ia);
int f_max_ab(Pion *plateau, int profondeur, int joueur_max, int joueur_ia, int alpha, int beta);
int f_min_ab(Pion *plateau, int profondeur, int joueur_min, int joueur_ia, int alpha, int beta);
int f_eval(Pion *jeu, int joueur, int profondeur);
int test_victoire(Pion *p);
int f_bataille(Pion *plateau, int l, int c);

/**
 * Fonction qui insère nouveau coup en tete
 ***/
ListeCoups ajouter_coup(ListeCoups tete, int l1, int c1, int l2, int c2) {
	ElementCoup *nouveau = (ElementCoup *)malloc(sizeof(ElementCoup));
	if (nouveau == NULL) {
		printf("Erreur allocation mémoire\n");
		exit(EXIT_FAILURE);
	}
	nouveau->coup.l1 = l1;
	nouveau->coup.c1 = c1;
	nouveau->coup.l2 = l2;
	nouveau->coup.c2 = c2;
	nouveau->suivant = tete;
	return nouveau;
}

/**
 *
 * fonction qui libère proprement la mémoire allouée
 *
 */
void liberer_coups(ListeCoups tete) {
	ElementCoup *courant = tete;
	while (courant != NULL) {
		ElementCoup *temp = courant->suivant;
		free(courant);
		courant = temp;
	}
}

int f_convert_char2int(char c)
{
#ifdef DEBUG
	printf("dbg: entering %s %d\n", __FUNCTION__, __LINE__);
#endif
	if(c>='A' && c<='Z')
		return (int)(c-'A');
	if(c>='a' && c<='z')
		return (int)(c-'a');
	return -1;
}

char f_convert_int2char(int i)
{
#ifdef DEBUG
	printf("dbg: entering %s %d\n", __FUNCTION__, __LINE__);
#endif

	return (char)i+'A';
}

Pion *f_init_plateau()
{
	int i, j;
	Pion *plateau=NULL;


#ifdef DEBUG
	printf("dbg: entering %s %d\n", __FUNCTION__, __LINE__);
#endif

	plateau = (Pion *)malloc(NB_LIGNES*NB_COLONNES*sizeof(Pion));
	if(plateau == NULL)
	{
		printf("error: unable to allocate memory\n");
		exit(EXIT_FAILURE);
	}

	for(i=0; i<NB_LIGNES; i++)
	{
		for(j=0; j<NB_COLONNES; j++)
		{
			plateau[i*NB_COLONNES+j].couleur = 0;
			plateau[i*NB_COLONNES+j].valeur = 0;
		}
	}

	plateau[9*NB_COLONNES+5].couleur = 1;
	plateau[9*NB_COLONNES+5].valeur = 1;

	plateau[9*NB_COLONNES+6].couleur = 1;
	plateau[9*NB_COLONNES+6].valeur = 2;

	plateau[9*NB_COLONNES+7].couleur = 1;
	plateau[9*NB_COLONNES+7].valeur = 3;

	plateau[9*NB_COLONNES+8].couleur = 1;
	plateau[9*NB_COLONNES+8].valeur = 2;

	plateau[9*NB_COLONNES+9].couleur = 1;
	plateau[9*NB_COLONNES+9].valeur = 1;

	plateau[8*NB_COLONNES+0].couleur = 1;
	plateau[8*NB_COLONNES+0].valeur = 1;

	plateau[8*NB_COLONNES+1].couleur = 1;
	plateau[8*NB_COLONNES+1].valeur = 3;

	plateau[8*NB_COLONNES+2].couleur = 1;
	plateau[8*NB_COLONNES+2].valeur = 3;

	plateau[8*NB_COLONNES+3].couleur = 1;
	plateau[8*NB_COLONNES+3].valeur = 1;

	plateau[8*NB_COLONNES+6].couleur = 1;
	plateau[8*NB_COLONNES+6].valeur = 1;

	plateau[8*NB_COLONNES+7].couleur = 1;
	plateau[8*NB_COLONNES+7].valeur = 1;

	plateau[8*NB_COLONNES+8].couleur = 1;
	plateau[8*NB_COLONNES+8].valeur = 1;

	plateau[7*NB_COLONNES+1].couleur = 1;
	plateau[7*NB_COLONNES+1].valeur = 1;

	plateau[7*NB_COLONNES+2].couleur = 1;
	plateau[7*NB_COLONNES+2].valeur = 1;

	plateau[2*NB_COLONNES+7].couleur = -1;
	plateau[2*NB_COLONNES+7].valeur = 1;

	plateau[2*NB_COLONNES+8].couleur = -1;
	plateau[2*NB_COLONNES+8].valeur = 1;

	plateau[1*NB_COLONNES+1].couleur = -1;
	plateau[1*NB_COLONNES+1].valeur = 1;

	plateau[1*NB_COLONNES+2].couleur = -1;
	plateau[1*NB_COLONNES+2].valeur = 1;

	plateau[1*NB_COLONNES+3].couleur = -1;
	plateau[1*NB_COLONNES+3].valeur = 1;

	plateau[1*NB_COLONNES+6].couleur = -1;
	plateau[1*NB_COLONNES+6].valeur = 1;

	plateau[1*NB_COLONNES+7].couleur = -1;
	plateau[1*NB_COLONNES+7].valeur = 3;

	plateau[1*NB_COLONNES+8].couleur = -1;
	plateau[1*NB_COLONNES+8].valeur = 3;

	plateau[1*NB_COLONNES+9].couleur = -1;
	plateau[1*NB_COLONNES+9].valeur = 1;

	plateau[0*NB_COLONNES+0].couleur = -1;
	plateau[0*NB_COLONNES+0].valeur = 1;

	plateau[0*NB_COLONNES+1].couleur = -1;
	plateau[0*NB_COLONNES+1].valeur = 2;

	plateau[0*NB_COLONNES+2].couleur = -1;
	plateau[0*NB_COLONNES+2].valeur = 3;

	plateau[0*NB_COLONNES+3].couleur = -1;
	plateau[0*NB_COLONNES+3].valeur = 2;

	plateau[0*NB_COLONNES+4].couleur = -1;
	plateau[0*NB_COLONNES+4].valeur = 1;

#ifdef DEBUG
printf("dbg: exiting %s %d\n", __FUNCTION__, __LINE__);
#endif

return plateau;
}

void f_affiche_plateau(Pion *plateau)
{
	int i,j,k;


#ifdef DEBUG
	printf("dbg: entering %s %d\n", __FUNCTION__, __LINE__);
#endif

	printf("\n    ");
	for(k=0; k<NB_COLONNES; k++)
		printf("%2c ",f_convert_int2char(k));
	printf("\n    ");
	for(k=0; k<NB_COLONNES; k++)
		printf("-- ");
	printf("\n");
	for(i=NB_LIGNES-1; i>=0; i--)
	{
		printf("%2d ", i);
		for(j=0; j<NB_COLONNES; j++)
		{
			printf("|");
			switch(plateau[i*NB_COLONNES+j].couleur)
			{
			case -1:
				printf("%do",plateau[i*NB_COLONNES+j].valeur);
				break;
			case 1:
				printf("%dx",plateau[i*NB_COLONNES+j].valeur);
				break;
			default:
				printf("  ");
			}
		}
		printf("|\n    ");
		for(k=0; k<NB_COLONNES; k++)
			printf("-- ");
		printf("\n");
	}
	printf("    ");

#ifdef DEBUG
	printf("dbg: exiting %s %d\n", __FUNCTION__, __LINE__);
#endif
}


int f_gagnant()
{
	int i, j, somme1=0, somme2=0;


#ifdef DEBUG
	printf("dbg: entering %s %d\n", __FUNCTION__, __LINE__);
#endif

	//Quelqu'un est-il arrive sur la ligne de l'autre
	for(i=0; i<NB_COLONNES; i++)
	{
		if(plateauDeJeu[i].couleur == 1)
			return 1;
		if(plateauDeJeu[(NB_LIGNES-1)*NB_COLONNES+i].couleur == -1)
			return -1;
	}

	//taille des armees
	for(i=0; i<NB_LIGNES; i++)
	{
		for(j=0; j<NB_COLONNES; j++)
		{
			if(plateauDeJeu[i*NB_COLONNES+j].couleur == 1)
				somme1++;
			if(plateauDeJeu[i*NB_COLONNES+j].couleur == -1)
				somme2++;
		}
	}
	if(somme1==0)
		return -1;
	if(somme2==0)
		return 1;

#ifdef DEBUG
	printf("dbg: exiting %s %d\n", __FUNCTION__, __LINE__);
#endif
	return 0;
}


/**
 * Prend comme argument la ligne et la colonne de la case
 * 	pour laquelle la bataille a lieu
 * Renvoie le couleur du gagnant
 * */
int f_bataille(Pion *plateau, int l, int c)
{
	int i, j, mini, maxi, minj, maxj;
	int somme=0;

#ifdef DEBUG
	printf("dbg: entering %s %d\n", __FUNCTION__, __LINE__);
#endif
	mini = l-1<0?0:l-1;
	maxi = l+1>NB_LIGNES-1?NB_LIGNES-1:l+1;
	minj = c-1<0?0:c-1;
	maxj = c+1>NB_COLONNES-1?NB_COLONNES-1:c+1;

	for(i=mini; i<=maxi; i++)
	{
		for(j=minj; j<=maxj; j++)
		{
			somme += plateau[i*NB_COLONNES+j].couleur*plateau[i*NB_COLONNES+j].valeur;
		}
	}
	somme -= plateau[l*NB_COLONNES+c].couleur*plateau[l*NB_COLONNES+c].valeur;

#ifdef DEBUG
	printf("dbg: exiting %s %d\n", __FUNCTION__, __LINE__);
#endif
	if(somme < 0)
		return -1;
	if(somme > 0)
		return 1;

	return plateau[l*NB_COLONNES+c].couleur;
}


/**
 * Prend la ligne et colonne de la case d'origine
 * 	et la ligne et colonne de la case de destination
 * Renvoie 1 en cas d'erreur
 * Renvoie 0 sinon
 * */
int f_test_mouvement(Pion *plateau, int l1, int c1, int l2, int c2, int couleur)
{
#ifdef DEBUG
	printf("dbg: entering %s %d\n", __FUNCTION__, __LINE__);
	printf("de (%d,%d) vers (%d,%d)\n", l1, c1, l2, c2);
#endif
	/* Erreur, hors du plateau */
	if(l1 < 0 || l1 >= NB_LIGNES || l2 < 0 || l2 >= NB_LIGNES ||
			c1 < 0 || c1 >= NB_COLONNES || c2 < 0 || c2 >= NB_COLONNES)
		return 1;
	/* Erreur, il n'y a pas de pion a deplacer ou le pion n'appartient pas au joueur*/
	if(plateau[l1*NB_COLONNES+c1].valeur == 0 || plateau[l1*NB_COLONNES+c1].couleur != couleur)
		return 1;
	/* Erreur, tentative de tir fratricide */
	if(plateau[l2*NB_COLONNES+c2].couleur == plateau[l1*NB_COLONNES+c1].couleur)
		return 1;

	if(l1-l2 >1 || l2-l1 >1 || c1-c2 >1 || c2-c1 >1 || (l1==l2 && c1==c2))
		return 1;
#ifdef DEBUG
	printf("dbg: exiting %s %d\n", __FUNCTION__, __LINE__);
#endif
	return 0;
}

/**
 * fonction qui génère les coups
 * **/
ListeCoups generer_coups(Pion *plateau, int joueur)
{
	ListeCoups liste = NULL;
	int l1, c1, dl, dc, l2, c2;

	for (l1 = 0; l1 < NB_LIGNES; l1++)
	{
		for (c1 = 0; c1 < NB_COLONNES; c1++)
		{
			// On cherche une pièce appartenant au joueur
			if (plateau[l1 * NB_COLONNES + c1].couleur == joueur)
			{
				// On explore les 8 directions autour d'elle
				for (dl = -1; dl <= 1; dl++)
				{
					for (dc = -1; dc <= 1; dc++)
					{
						if (dl == 0 && dc == 0)
							continue; // Rester sur place n'est pas un mouvement

						l2 = l1 + dl;
						c2 = c1 + dc;

						// f_test_mouvement renvoie 0 si le mouvement est légal
						if (f_test_mouvement(plateau, l1, c1, l2, c2, joueur) == 0)
						{
							liste = ajouter_coup(liste, l1, c1, l2, c2);
						}
					}
				}
			}
		}
	}

	return liste;
}

/**
 * Prend la ligne et colonne de la case d'origine
 * 	et la ligne et colonne de la case de destination
 *  et effectue le trantement de l'operation demandée
 * Renvoie 1 en cas d'erreur
 * Renvoie 0 sinon
 * */
int f_bouge_piece(Pion *plateau, int l1, int c1, int l2, int c2, int couleur)
{
	int gagnant=0;


#ifdef DEBUG
	printf("dbg: entering %s %d\n", __FUNCTION__, __LINE__);
#endif

	if(f_test_mouvement(plateau, l1, c1, l2, c2, couleur) != 0)
		return 1;


	/* Cas ou il n'y a personne a l'arrivee */
	if(plateau[l2*NB_COLONNES+c2].valeur == 0)
	{
		plateau[l2*NB_COLONNES+c2].couleur = plateau[l1*NB_COLONNES+c1].couleur;
		plateau[l2*NB_COLONNES+c2].valeur = plateau[l1*NB_COLONNES+c1].valeur;
		plateau[l1*NB_COLONNES+c1].couleur = 0;
		plateau[l1*NB_COLONNES+c1].valeur = 0;
	}
	else
	{
		gagnant=f_bataille(plateau, l2, c2);
		/* victoire */
		if(gagnant == couleur)
		{
			plateau[l2*NB_COLONNES+c2].couleur = plateau[l1*NB_COLONNES+c1].couleur;
			plateau[l2*NB_COLONNES+c2].valeur = plateau[l1*NB_COLONNES+c1].valeur;
			plateau[l1*NB_COLONNES+c1].couleur = 0;
			plateau[l1*NB_COLONNES+c1].valeur = 0;
		}
		/* defaite */
		else if(gagnant != 0)
		{
			plateau[l1*NB_COLONNES+c1].couleur = 0;
			plateau[l1*NB_COLONNES+c1].valeur = 0;
		}
	}

#ifdef DEBUG
	printf("dbg: exiting %s %d\n", __FUNCTION__, __LINE__);
#endif
	return 0;
}

//Calcul du nombre de pions sur le plateau du joueur
int f_nbPions(Pion* jeu, int joueur)
{
	int nbPion=0;
	int i, j;
	for (i = 0; i < NB_COLONNES; ++i)
	{
		for (j = 0; j < NB_LIGNES; ++j)
		{
			if (jeu[i * NB_COLONNES + j].couleur == joueur)
			{
				++nbPion;
			}
		}
	}
	return nbPion;
}

//Calcul de la valeur de tous les pions du joueur
int f_valeur(Pion* jeu, int joueur)
{
	int i, j;
	int valeur=0;
	for (i = 0; i < NB_COLONNES; ++i)
	{
		for (j = 0; j < NB_LIGNES; ++j)
		{
			if (jeu[i * NB_COLONNES + j].couleur == joueur)
			{
				valeur += jeu[i * NB_COLONNES + j].valeur;
			}
		}
	}
	return valeur;
}

//fonction d'évaluation
int f_eval(Pion *jeu, int joueur, int profondeur)
{
    int i, j;
    int adversaire = -joueur;
    int score = 0;

    // Détection de victoire ou défaite par percée de la ligne adverse
    for (i = 0; i < NB_COLONNES; i++)
    {
        // Pour les Noirs (1), la ligne de fond adverse est la ligne 0
        if (jeu[0 * NB_COLONNES + i].couleur == 1)
        {
            return (joueur == 1) ? (5000 + profondeur) : (-5000 - profondeur);
        }
        // Pour les Blancs (-1), la ligne de fond adverse est la ligne 9
        if (jeu[(NB_LIGNES - 1) * NB_COLONNES + i].couleur == -1)
        {
            return (joueur == -1) ? (5000 + profondeur) : (-5000 - profondeur);
        }
    }

    // Détection par extermination d'armée
    int pions_joueur = f_nbPions(jeu, joueur);
    int pions_adv = f_nbPions(jeu, adversaire);

    if (pions_adv == 0) return 5000 + profondeur;
    if (pions_joueur == 0) return -5000 - profondeur;

    // Différence matérielle (force et effectif)
    int val_joueur = f_valeur(jeu, joueur);
    int val_adv = f_valeur(jeu, adversaire);
    score += (val_joueur - val_adv) * 20; // Poids fort pour inciter aux batailles favorables
    score += (pions_joueur - pions_adv) * 10;

    // Avancement et sécurité de la ligne de fond
    int avancement = 0;
    int danger_fond = 0;

    for (i = 0; i < NB_LIGNES; i++)
    {
        for (j = 0; j < NB_COLONNES; j++)
        {
            Pion p = jeu[i * NB_COLONNES + j];
            if (p.couleur == joueur)
            {
                if (joueur == 1)
                    avancement += (9 - i); // Distance parcourue vers le bas
                else
                    avancement += i;       // Distance parcourue vers le haut
            }
            else if (p.couleur == adversaire)
            {
                if (adversaire == 1)
                {
                    avancement -= (9 - i);
                    // Alerte : un Noir approche de la ligne 0 des Blancs
                    if (i <= 2)
                        danger_fond += (3 - i) * 60;
                }
                else
                {
                    avancement -= i;
                    // Alerte : un Blanc approche de la ligne 9 des Noirs
                    if (i >= 7)
                        danger_fond += (i - 6) * 60;
                }
            }
        }
    }

    score += avancement * 2;
    score -= danger_fond; // Malus de sécurité

    return score;
}

//copie du plateau
void f_copie_plateau(Pion* source, Pion* destination)
{
	int i, j;
	for (i = 0; i < NB_LIGNES; i++)
	{
		for (j = 0; j < NB_COLONNES; j++)
		{
			destination[i * NB_COLONNES + j].couleur = source[i * NB_COLONNES + j].couleur;
			destination[i * NB_COLONNES + j].valeur = source[i * NB_COLONNES + j].valeur;
		}
	}
}

//mise a zero du plateau
Pion* f_raz_plateau()
{
	Pion* jeu = NULL;
	int i, j;
	jeu = (Pion *) malloc(NB_LIGNES * NB_COLONNES * sizeof (Pion));
	for (i = 0; i < NB_LIGNES; i++)
	{
		for (j = 0; j < NB_COLONNES; j++)
		{
			jeu[i * NB_COLONNES + j].couleur = 0;
			jeu[i * NB_COLONNES + j].valeur = 0;
		}
	}
	return jeu;
}

//Fonction min trouve le minimum des noeuds fils
int f_min(Pion *plateau, int profondeur, int joueur_min, int joueur_ia)
{
	nb_noeuds_visites++;

	if (profondeur <= 0 || test_victoire(plateau) != 0)
		return f_eval(plateau, joueur_ia, profondeur);

	// Condition d'arrêt
	if (profondeur == 0)
	{
		return f_eval(plateau, joueur_ia, profondeur);
	}

	int meilleur_score = INFINI;
	ListeCoups coups = generer_coups(plateau, joueur_min);
	ElementCoup *courant = coups;

	// Si aucun coup possible, on évalue la position
	if (coups == NULL)
		return f_eval(plateau, joueur_ia, profondeur);

	Pion copie[NB_LIGNES * NB_COLONNES];

	while (courant != NULL)
	{
		// Copier le plateau
		f_copie_plateau(plateau, copie);

		// Jouer le coup sur la copie
		f_bouge_piece(copie, courant->coup.l1, courant->coup.c1, courant->coup.l2, courant->coup.c2, joueur_min);

		// Appel récursif vers f_max
		int score = f_max(copie, profondeur - 1, -joueur_min, joueur_ia);

		// Garder le minimum
		if (score < meilleur_score)
			meilleur_score = score;

		courant = courant->suivant;
	}

	// Libérer la mémoire des coups
	liberer_coups(coups);

	return meilleur_score;
}

//Fonction max trouve le maximum des noeuds fils
int f_max(Pion *plateau, int profondeur, int joueur_max, int joueur_ia)
{
	nb_noeuds_visites++;

	if (profondeur <= 0 || test_victoire(plateau) != 0)
		return f_eval(plateau, joueur_ia, profondeur);

	// Condition d'arrêt
	if (profondeur <= 0) {
		return f_eval(plateau, joueur_ia, profondeur);
	}

	int valeur_max = -INFINI;
	ListeCoups coups = generer_coups(plateau, joueur_max);
	ElementCoup *courant = coups;

	if (coups == NULL)
		return f_eval(plateau, joueur_ia, profondeur);

	Pion copie[NB_LIGNES * NB_COLONNES];

	// Parcourir chaque coup possible
	while (courant != NULL)
	{
		f_copie_plateau(plateau, copie);
		f_bouge_piece(copie, courant->coup.l1, courant->coup.c1, courant->coup.l2, courant->coup.c2, joueur_max);

		// Appel recursif vers f_min pour le joueur adverse
		int v = f_min(copie, profondeur - 1, -joueur_max, joueur_ia);
		if (v > valeur_max) {
			valeur_max = v;
		}

		courant = courant->suivant;
	}

	liberer_coups(coups);
	return valeur_max;
}

// Version avec coupures Alpha/Beta de f_min
int f_min_ab(Pion *plateau, int profondeur, int joueur_min, int joueur_ia, int alpha, int beta)
{
    nb_noeuds_visites++; // On compte chaque nœud exploré

	if (profondeur <= 0 || test_victoire(plateau) != 0)
		return f_eval(plateau, joueur_ia, profondeur);

    if (profondeur <= 0)
    {
        return f_eval(plateau, joueur_ia, profondeur);
    }

    int meilleur_score = INFINI;
    ListeCoups coups = generer_coups(plateau, joueur_min);
    ElementCoup *courant = coups;

    if (coups == NULL)
        return f_eval(plateau, joueur_ia, profondeur);

    Pion copie[NB_LIGNES * NB_COLONNES];

    while (courant != NULL)
    {
        f_copie_plateau(plateau, copie);
        f_bouge_piece(copie, courant->coup.l1, courant->coup.c1, courant->coup.l2, courant->coup.c2, joueur_min);

        // Appel recursif croise vers f_max_ab avec alpha et beta
        int score = f_max_ab(copie, profondeur - 1, -joueur_min, joueur_ia, alpha, beta);

        if (score < meilleur_score)
            meilleur_score = score;

        // Mise a jour de la borne beta
        if (meilleur_score < beta)
            beta = meilleur_score;

        // Coupure Beta : le joueur MAX au-dessus ne choisira jamais cette branche
        if (beta <= alpha)
            break;

        courant = courant->suivant;
    }

    liberer_coups(coups);
    return meilleur_score;
}

// Version avec coupures Alpha/Beta de f_max
int f_max_ab(Pion *plateau, int profondeur, int joueur_max, int joueur_ia, int alpha, int beta)
{
    nb_noeuds_visites++; // On compte chaque nœud exploré

	if (profondeur <= 0 || test_victoire(plateau) != 0)
		return f_eval(plateau, joueur_ia, profondeur);

    if (profondeur <= 0)
    {
        return f_eval(plateau, joueur_ia, profondeur);
    }

    int valeur_max = -INFINI;
    ListeCoups coups = generer_coups(plateau, joueur_max);
    ElementCoup *courant = coups;

    if (coups == NULL)
        return f_eval(plateau, joueur_ia, profondeur);

    Pion copie[NB_LIGNES * NB_COLONNES];

    while (courant != NULL)
    {
        f_copie_plateau(plateau, copie);
        f_bouge_piece(copie, courant->coup.l1, courant->coup.c1, courant->coup.l2, courant->coup.c2, joueur_max);

        // Appel recursif croise vers f_min_ab avec alpha et beta
        int v = f_min_ab(copie, profondeur - 1, -joueur_max, joueur_ia, alpha, beta);

        if (v > valeur_max)
            valeur_max = v;

        // Mise a jour de la borne alpha
        if (valeur_max > alpha)
            alpha = valeur_max;

        // Coupure Alpha : le joueur MIN au-dessus ne permettra jamais d'atteindre ce score
        if (alpha >= beta)
            break;

        courant = courant->suivant;
    }

    liberer_coups(coups);
    return valeur_max;
}

/**
 *fonction qui test la victoire
 ***/
int test_victoire(Pion *p)
{
	int i;
	for (i = 0; i < NB_COLONNES; i++)
	{
		if (p[0 * NB_COLONNES + i].couleur == 1) return 1;       // Victoire Noirs (x)
		if (p[9 * NB_COLONNES + i].couleur == -1) return -1;     // Victoire Blancs (o)
	}
	return 0;
}

/**
 * Calcule et joue le meilleur cout
 * */
void f_IA(int joueur)
{
#ifdef DEBUG
	printf("dbg: entering %s %d\n", __FUNCTION__, __LINE__);
#endif

	int profondeur = 3;
	int meilleur_score = -INFINI;
	int meilleur_l1 = -1, meilleur_c1 = -1;
	int meilleur_l2 = -1, meilleur_c2 = -1;

	// Fenêtre initiale pour Alpha/Beta
	int alpha = -INFINI;
	int beta = +INFINI;

	nb_noeuds_visites = 0; // Remise à zéro pour ce coup précis

	ListeCoups coups = generer_coups(plateauDeJeu, joueur);
	ElementCoup *courant = coups;

	if (coups == NULL)
	{
		printf("Aucun coup possible pour le joueur %d\n", joueur);
		return;
	}

	Pion copie[NB_LIGNES * NB_COLONNES];

	while (courant != NULL) {
		// Simuler le coup sur une copie
		f_copie_plateau(plateauDeJeu, copie);
		f_bouge_piece(copie, courant->coup.l1, courant->coup.c1, courant->coup.l2, courant->coup.c2, joueur);

		// Evaluer la suite avec le tour de l'adversaire (-joueur)
		//int score = f_min(copie, profondeur - 1, -joueur, joueur); Pour version sans alpha/beta

		// Appel à la version Alpha/Beta
		//int score = f_min_ab(copie, profondeur - 1, -joueur, joueur, alpha, beta);

		int score;

		if (test_victoire(copie) == joueur) {
			score = 10000;
		}
		else{
			// Choix de l'algorithme sélectionné dans le menu
			if (algo_ia == 1)
			{
				// 1. Minimax classique
				score = f_min(copie, profondeur - 1, -joueur, joueur);
			}
			else
			{
				// 2. Alpha-Beta
				score = f_min_ab(copie, profondeur - 1, -joueur, joueur, alpha, beta);
			}
		}

		// Memoriser le meilleur coup
		if (score > meilleur_score)
		{
			meilleur_score = score;
			meilleur_l1 = courant->coup.l1;
			meilleur_c1 = courant->coup.c1;
			meilleur_l2 = courant->coup.l2;
			meilleur_c2 = courant->coup.c2;
		}

		// Mise à jour de la borne alpha pour le mode Alpha-Beta
		if (algo_ia == 2 && meilleur_score > alpha)
			alpha = meilleur_score;

		courant = courant->suivant;
	}

	// Libération
	liberer_coups(coups);

	// Appliquer le coup choisi sur le vrai plateau
	if (meilleur_l1 != -1)
	{
		printf("IA (%s | %s) joue : %c%d -> %c%d (score estimé : %d | noeuds : %ld)\n",
			   (joueur == 1 ? "x" : "o"),
			   (algo_ia == 1 ? "Minimax" : "Alpha-Beta"),
			   f_convert_int2char(meilleur_c1), meilleur_l1,
			   f_convert_int2char(meilleur_c2), meilleur_l2, meilleur_score, nb_noeuds_visites);
		f_bouge_piece(plateauDeJeu, meilleur_l1, meilleur_c1, meilleur_l2, meilleur_c2, joueur);
	}

#ifdef DEBUG
	printf("dbg: exiting %s %d\n", __FUNCTION__, __LINE__);
#endif
}

/**
 * Demande le choix du joueur humain et calcule le coup demande
 * */
void f_humain(int joueur)
{
	char c1, c2;
	char buffer[32];
	int l1, l2;


#ifdef DEBUG
	printf("dbg: entering %s %d\n", __FUNCTION__, __LINE__);
#endif

	printf("joueur ");
	switch(joueur)
	{
	case -1:
		printf("o ");
		break;
	case 1:
		printf("x ");
		break;
	default:
		printf("inconnu ");
	}
	printf("joue:\n");
	while(1)
	{
		fgets(buffer, 32, stdin);
		if(sscanf(buffer, "%c%i%c%i\n", &c1, &l1, &c2, &l2) == 4)
		{
			if(f_bouge_piece(plateauDeJeu, l1, f_convert_char2int(c1), l2, f_convert_char2int(c2), joueur) == 0)
				break;
		}
		fflush(stdin);
		printf("mauvais choix\n");
	}

#ifdef DEBUG
	printf("dbg: exiting %s %d\n", __FUNCTION__, __LINE__);
#endif
}

int main(int argv, char *argc[])
{
	int fin = 0,mode=0 , ret, joueur = 1;
	printf("1 humain vs IA\n2 humain vs humain\n3 IA vs IA\n");
	scanf("%d",&mode);

	if (mode == 1 || mode == 3)
	{
		printf("\n--- Choix de l'algorithme IA ---\n");
		printf("1. Minimax classique\n2. Minimax avec coupures Alpha-Beta\n");
		scanf("%d", &algo_ia);
	}

	plateauDeJeu = f_init_plateau();
	while (!fin)
	{
		f_affiche_plateau(plateauDeJeu);
		if(mode==1)
		{
			if(joueur>0)
				f_humain(joueur);
			else
				f_IA(joueur);
		}
		else if(mode==2)
		{
			f_humain(joueur);
		}
		else
		{
			f_IA(joueur);
		}

		if ((ret = f_gagnant()) != 0)
		{
			switch (ret)
			{
			case 1:
				f_affiche_plateau(plateauDeJeu);
				printf("joueur x gagne!\n");
				fin = 1;
				break;
			case -1:
				f_affiche_plateau(plateauDeJeu);
				printf("joueur o gagne!\n");
				fin = 1;
				break;
			}
		}
		joueur = -joueur;
	}

#ifdef DEBUG
	printf("dbg: exiting %s %d\n", __FUNCTION__, __LINE__);
#endif

	return 0;
}


