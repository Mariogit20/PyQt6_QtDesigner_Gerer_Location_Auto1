from pack.database import bdd
db,cur = bdd("bdd.db")

import sqlite3

from pack.affichage import AffichageParDetail

def AffichageParDetail_PLUSIEURS_ENREGISTREMENTS(Table,colonne,valeur):
    query = f'SELECT* FROM {Table} WHERE  {colonne} = ?'
    result = cur.execute(query,(valeur,))
    data = result.fetchall()
    return data



def Fonction___Est_ce_que____EXISTE____True_False____NumeroForeignKey____TABLE_type_user____CHAMP_id_type_user____dans_le____CHAMPS_DE_RECHERCHE____QLineEdit____input_search(CHAMP_____id_type_user_____OU_____type_user_____TABLE_____type_user):
    #
    #### DEBUT ===> search_term :::
    """
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    Charge les types d'Utilisateurs de la base de données
    et les ajoute à la liste déroulante en associant chaque nom à son ID.
    """
    """
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    Charge les types d'Utilisateurs de la base de données
    et les ajoute à la liste déroulante en associant chaque nom à son ID.
    """
    connection = sqlite3.connect('bdd.db')
    cursor = connection.cursor()

    try:

        print(f"CHAMP_____id_type_user_____OU_____type_user_____TABLE_____type_user = {CHAMP_____id_type_user_____OU_____type_user_____TABLE_____type_user}")


        Table = "type_user"
        colonne = "id_type_user"
        valeur = CHAMP_____id_type_user_____OU_____type_user_____TABLE_____type_user

        data = AffichageParDetail(Table,colonne,valeur)
        # data = AffichageParDetail("type_user","type_user",CHAMP_____id_type_user_____OU_____type_user_____TABLE_____type_user)        

        if data:

            print(f"data AffichageParDetail NumeroForeignKey = {data}")
            print(f"data AffichageParDetail NumeroForeignKey CLEF id_type_user = {data[0]}")
            print(f"data AffichageParDetail NumeroForeignKey VALEUR type_user = {data[1]}")                

            print(f"valeur NumeroForeignKey = {valeur}")

            if str(data[0]) != str(valeur):
                return None
            else:
                return data[0]

    except sqlite3.Error as e:
        print(f"Erreur de base de données : {e}")
        # print(f"Erreur lors de la recherche: {e}")                        
    finally:
        connection.close()
    """
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    Charge les types d'Utilisateurs de la base de données
    et les ajoute à la liste déroulante en associant chaque nom à son ID.
    """
    """
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    Charge les types d'Utilisateurs de la base de données
    et les ajoute à la liste déroulante en associant chaque nom à son ID.
    """
    #### FIN   ===> search_term !!!
     




def Fonction_REMPLACER_LE____NumeroForeignKey____PAR_LA____ValeurForeignKey____QUI_est____Administrateur_OU_Moderateur_OU_Utilisateur(CHAMP_____id_type_user_____OU_____type_user_____TABLE_____type_user):
    # pass       # NE RIEN FAIRE DU TOUT

    #### DEBUT ===> search_term :::
    """
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    Charge les types d'Utilisateurs de la base de données
    et les ajoute à la liste déroulante en associant chaque nom à son ID.
    """
    """
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    DEBUT ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    Charge les types d'Utilisateurs de la base de données
    et les ajoute à la liste déroulante en associant chaque nom à son ID.
    """
    connection = sqlite3.connect('bdd.db')
    cursor = connection.cursor()

    try:

        print(f"CHAMP_____id_type_user_____OU_____type_user_____TABLE_____type_user = {CHAMP_____id_type_user_____OU_____type_user_____TABLE_____type_user}")


        Table = "type_user"
        colonne = "type_user"
        valeur = CHAMP_____id_type_user_____OU_____type_user_____TABLE_____type_user

        data = AffichageParDetail(Table,colonne,valeur)
        # data = AffichageParDetail("type_user","type_user",CHAMP_____id_type_user_____OU_____type_user_____TABLE_____type_user)        

        if data:

            print(f"data AffichageParDetail = {data}")
            print(f"data AffichageParDetail CLEF id_type_user = {data[0]}")
            print(f"data AffichageParDetail VALEUR type_user = {data[1]}")                

            print(f"valeur = {valeur}")

            if data[1] != valeur:
                return None
            else:
                return data[0]

    except sqlite3.Error as e:
        print(f"Erreur de base de données : {e}")
        # print(f"Erreur lors de la recherche: {e}")                        
    finally:
        connection.close()
    """
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    Charge les types d'Utilisateurs de la base de données
    et les ajoute à la liste déroulante en associant chaque nom à son ID.
    """
    """
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    FIN ========== QLineEdit ===========> input_search   ::::::::::   LISTE DEROULANTE ===========>   TYPE D'Utilisateur   ( 'Administrateur', 'Moderateur', 'Utilisateur' )
    Charge les types d'Utilisateurs de la base de données
    et les ajoute à la liste déroulante en associant chaque nom à son ID.
    """
    #### FIN   ===> search_term !!!
    
    