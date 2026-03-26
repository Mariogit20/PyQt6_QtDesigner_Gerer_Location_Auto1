import sqlite3

def create_table():
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\User_form.ui ::::::::::::::::::
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\User_form.ui ::::::::::::::::::
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\User_form.ui ::::::::::::::::::
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\User_form.ui ::::::::::::::::::
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\User_form.ui ::::::::::::::::::
    connection = sqlite3.connect('bdd.db')
    cursor = connection.cursor()

    # Activer la vérification des clés étrangères
    cursor.execute('PRAGMA foreign_keys = ON;')

    # Création de la table type_user (inchangée)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS type_user(
            id_type_user INTEGER PRIMARY KEY,
            type_user TEXT NOT NULL UNIQUE
        )
    ''')

    # Insertion des trois valeurs par défaut (inchangée)
    types_a_inserer = ['Administrateur', 'Moderateur', 'Utilisateur']
    for type_user_value in types_a_inserer:
        cursor.execute('''
            INSERT OR IGNORE INTO type_user(type_user) VALUES(?)
        ''', (type_user_value,))

    # Création de la table user avec la clé étrangère obligatoire et les cascades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            prenom TEXT,
            age INTEGER NOT NULL,
            sexe TEXT NOT NULL,
            email TEXT NOT NULL,
            telephone TEXT NOT NULL,
            id_type_user INTEGER NOT NULL,
            FOREIGN KEY(id_type_user) 
            REFERENCES type_user(id_type_user)
            ON UPDATE CASCADE
            ON DELETE CASCADE
        )
    ''')

    ## Suppression de la table admin (elle n'a pas été demandée dans la nouvelle structure relationnelle)
    #cursor.execute('''
    #    DROP TABLE IF EXISTS admin	
    #''')
	
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login Text,
            password Text
        )
    ''')	


    # Appel de la fonction pour mettre à jour la base de données
    create_agence_tables(connection, cursor)
    print("La base de données 'bdd.db' a été créée et mise à jour avec toutes les tables de l'agence (transport et maintenance).")    
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\User_form.ui !!!!!!!!!!!!!!!!!!
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\User_form.ui !!!!!!!!!!!!!!!!!!
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\User_form.ui !!!!!!!!!!!!!!!!!!
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\User_form.ui !!!!!!!!!!!!!!!!!!
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\User_form.ui !!!!!!!!!!!!!!!!!!










    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionVoyage.ui ::::::::::::::::::
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionVehicule.ui ::::::::::::::::::
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionReparation.ui ::::::::::::::::::
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionVoyage.ui ::::::::::::::::::
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionVehicule.ui ::::::::::::::::::
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionReparation.ui ::::::::::::::::::
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionVoyage.ui ::::::::::::::::::
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionVehicule.ui ::::::::::::::::::
    # DEBUT ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionReparation.ui ::::::::::::::::::    

def create_agence_tables(connection, cursor):
    """
    Crée toutes les tables de l'agence de transport et de maintenance
    selon le Modèle Conceptuel de Données (MCD) affiné,
    en utilisant SQLite et en définissant les clés étrangères et les cascades.
    """
    # connection = sqlite3.connect('bdd.db')
    # cursor = connection.cursor()

    # Activer la vérification des clés étrangères
    cursor.execute('PRAGMA foreign_keys = ON;')

    # --- TABLES DE BASE ET DE RÉFÉRENCE ---

    # 1. TABLE CHAUFFEUR
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CHAUFFEUR (
            id_chauffeur INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            telephone TEXT UNIQUE,
            date_permis DATE,
            type_permis TEXT
        )
    ''')

    # 2. TABLE CLIENT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CLIENT (
            id_client INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT,
            email TEXT UNIQUE NOT NULL,
            telephone TEXT,
            adresse TEXT
        )
    ''')
    
    # 3. TABLE TYPE_VEHICULE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TYPE_VEHICULE (
            id_type INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_type TEXT NOT NULL UNIQUE,
            intervalle_vidange_km INTEGER,
            intervalle_révision_mois INTEGER
        )
    ''')

    # 4. TABLE VEHICULE (Régi par TYPE_VEHICULE)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS VEHICULE (
            immatriculation TEXT PRIMARY KEY,
            marque TEXT NOT NULL,
            modele TEXT,
            annee INTEGER,
            kilometrage_actuel INTEGER DEFAULT 0,
            capacite_places INTEGER,
            statut_disponibilite TEXT NOT NULL DEFAULT 'Disponible',
            id_type INTEGER NOT NULL,
            FOREIGN KEY(id_type)
            REFERENCES TYPE_VEHICULE(id_type)
            ON UPDATE CASCADE
            ON DELETE RESTRICT -- Empêche la suppression du type s'il y a des véhicules
        )
    ''')

    # 5. TABLE FOURNISSEUR
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FOURNISSEUR (
            id_fournisseur INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_fournisseur TEXT NOT NULL,
            contact TEXT,
            telephone TEXT,
            specialite TEXT -- (Pièces, Garage, Services)
        )
    ''')

    # 6. TABLE PIECE (Sourcée par FOURNISSEUR)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PIECE (
            id_piece INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_piece TEXT NOT NULL,
            reference_fournisseur TEXT UNIQUE,
            prix_unitaire REAL NOT NULL,
            quantite_stock INTEGER DEFAULT 0
            -- Note: La relation SOURCER (M-N) est gérée plus loin si nécessaire, 
            -- ici on se concentre sur les relations 1-N directes.
        )
    ''')

    # --- TABLES DES OPÉRATIONS (VOYAGES ET MAINTENANCE) ---

    # 7. TABLE VOYAGE (Réservé par CLIENT, Attribué à VEHICULE et CHAUFFEUR)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS VOYAGE (
            id_voyage INTEGER PRIMARY KEY AUTOINCREMENT,
            date_debut DATETIME NOT NULL,
            date_fin DATETIME,
            lieu_depart TEXT NOT NULL,
            lieu_arrivee TEXT NOT NULL,
            distance_estimee INTEGER,
            statut_voyage TEXT NOT NULL DEFAULT 'Planifié',
            id_client INTEGER NOT NULL,
            immatriculation TEXT NOT NULL,
            id_chauffeur INTEGER NOT NULL,
            FOREIGN KEY(id_client) REFERENCES CLIENT(id_client)
                ON UPDATE CASCADE ON DELETE RESTRICT,
            FOREIGN KEY(immatriculation) REFERENCES VEHICULE(immatriculation)
                ON UPDATE CASCADE ON DELETE RESTRICT,
            FOREIGN KEY(id_chauffeur) REFERENCES CHAUFFEUR(id_chauffeur)
                ON UPDATE CASCADE ON DELETE RESTRICT
        )
    ''')
    
    # 8. TABLE FACTURE_CLIENT (Liée à VOYAGE)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FACTURE_CLIENT (
            id_facture INTEGER PRIMARY KEY AUTOINCREMENT,
            date_emission DATE NOT NULL,
            date_echeance DATE,
            montant_HT REAL NOT NULL,
            montant_TVA REAL,
            statut_paiement TEXT NOT NULL DEFAULT 'En attente',
            id_voyage INTEGER UNIQUE NOT NULL, -- Un voyage = une facture
            FOREIGN KEY(id_voyage) REFERENCES VOYAGE(id_voyage)
                ON UPDATE CASCADE ON DELETE RESTRICT
        )
    ''')

    # 9. TABLE REPARATION (Concerne VEHICULE, Peut être Sous-Traitée à FOURNISSEUR)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS REPARATION (
            id_reparation INTEGER PRIMARY KEY AUTOINCREMENT,
            date_debut_reparation DATETIME NOT NULL,
            date_fin_reparation DATETIME,
            nature_panne TEXT,
            description_travaux TEXT,
            type_maintenance TEXT NOT NULL, -- Préventive ou Corrective
            immatriculation TEXT NOT NULL,
            id_fournisseur INTEGER, -- NULL si réparation interne
            FOREIGN KEY(immatriculation) REFERENCES VEHICULE(immatriculation)
                ON UPDATE CASCADE ON DELETE RESTRICT,
            FOREIGN KEY(id_fournisseur) REFERENCES FOURNISSEUR(id_fournisseur)
                ON UPDATE CASCADE ON DELETE SET NULL
        )
    ''')
    
    # 10. TABLE COMMANDE_REPARATION (Liée à REPARATION et à FOURNISSEUR)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS COMMANDE_REPARATION (
            id_commande INTEGER PRIMARY KEY AUTOINCREMENT,
            date_commande DATE NOT NULL,
            montant_estime REAL,
            statut_commande TEXT NOT NULL DEFAULT 'En cours',
            id_fournisseur INTEGER NOT NULL,
            FOREIGN KEY(id_fournisseur) REFERENCES FOURNISSEUR(id_fournisseur)
                ON UPDATE CASCADE ON DELETE RESTRICT
        )
    ''')
    
    # --- TABLES DE LIAISON (Relations M:N) ---

    # 11. TABLE PASSER (Liaison M:N entre REPARATION et COMMANDE_REPARATION)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PASSER (
            id_reparation INTEGER NOT NULL,
            id_commande INTEGER NOT NULL,
            PRIMARY KEY (id_reparation, id_commande),
            FOREIGN KEY(id_reparation) REFERENCES REPARATION(id_reparation)
                ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY(id_commande) REFERENCES COMMANDE_REPARATION(id_commande)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
    ''')
    
    # 12. TABLE UTILISER (Liaison M:N entre COMMANDE_REPARATION et PIECE)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UTILISER (
            id_commande INTEGER NOT NULL,
            id_piece INTEGER NOT NULL,
            quantite_utilisee INTEGER NOT NULL,
            PRIMARY KEY (id_commande, id_piece),
            FOREIGN KEY(id_commande) REFERENCES COMMANDE_REPARATION(id_commande)
                ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY(id_piece) REFERENCES PIECE(id_piece)
                ON UPDATE CASCADE ON DELETE RESTRICT
        )
    ''')

    # --- TABLES DE MAINTENANCE ET GPS ---

    # 13. TABLE PLAN_MAINTENANCE (Définie par TYPE_VEHICULE)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PLAN_MAINTENANCE (
            id_plan INTEGER PRIMARY KEY AUTOINCREMENT,
            description_tache TEXT NOT NULL,
            frequence_km INTEGER, -- NULL si basée sur le temps
            frequence_jours INTEGER, -- NULL si basée sur le kilométrage
            est_active BOOLEAN NOT NULL DEFAULT 1,
            id_type INTEGER NOT NULL,
            FOREIGN KEY(id_type) REFERENCES TYPE_VEHICULE(id_type)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
    ''')

    # 14. TABLE SUIVI_GPS (Localise VEHICULE)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SUIVI_GPS (
            id_suivi INTEGER PRIMARY KEY AUTOINCREMENT,
            date_heure DATETIME NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            vitesse INTEGER,
            immatriculation TEXT NOT NULL,
            FOREIGN KEY(immatriculation) REFERENCES VEHICULE(immatriculation)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
    ''')

    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionVoyage.ui !!!!!!!!!!!!!!!!!!
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionVehicule.ui !!!!!!!!!!!!!!!!!!
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionReparation.ui !!!!!!!!!!!!!!!!!!
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionVoyage.ui !!!!!!!!!!!!!!!!!!
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionVehicule.ui !!!!!!!!!!!!!!!!!!
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionReparation.ui !!!!!!!!!!!!!!!!!!
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionVoyage.ui !!!!!!!!!!!!!!!!!!
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionVehicule.ui !!!!!!!!!!!!!!!!!!
    # FIN   ================ Fichier QtDesigner .ui ==========> D:\PYTHON DJANGO HOPES\Projet_LOGICIEL_PyQt6_QtDesigner_Show\GestionReparation.ui !!!!!!!!!!!!!!!!!!






    connection.commit()
    connection.close()

# Appel de la fonction pour mettre à jour la base de données
if __name__ == '__main__':
    create_table()
    print("La base de données 'bdd.db' a été mise à jour avec une clé étrangère obligatoire et des actions en cascade.")




    