# -*- coding: utf-8 -*-
import sqlite3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox)
from PyQt6.QtCore import Qt

class GestionRechercheClient(QWidget):
    def __init__(self, db_connect_func):
        super().__init__()
        self.db_connect = db_connect_func
        self.layout_principal = QVBoxLayout(self)

        # 1. EN-TÊTE
        titre = QLabel("🔍 Moteur de Recherche Global & Historique Client")
        titre.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #2980b9;")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_principal.addWidget(titre)

        # 2. ZONE DE FILTRES DYNAMIQUES
        groupe_filtres = QGroupBox("🔎 Tapez vos critères (Le tableau se met à jour automatiquement)")
        groupe_filtres.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #bdc3c7; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        layout_filtres = QGridLayout(groupe_filtres)

        # Création des champs de recherche
        self.champ_nom = QLineEdit(); self.champ_nom.setPlaceholderText("Ex: Dupont...")
        self.champ_email = QLineEdit(); self.champ_email.setPlaceholderText("Ex: @gmail.com...")
        self.champ_tel = QLineEdit(); self.champ_tel.setPlaceholderText("Ex: 06...")
        self.champ_adresse = QLineEdit(); self.champ_adresse.setPlaceholderText("Ex: Paris...")
        self.champ_immat = QLineEdit(); self.champ_immat.setPlaceholderText("Ex: AB-123-CD...")
        self.champ_vehicule = QLineEdit(); self.champ_vehicule.setPlaceholderText("Ex: Toyota Yaris...")
        self.champ_destination = QLineEdit(); self.champ_destination.setPlaceholderText("Ex: Aéroport, Hôtel...")

        # Placement dans la grille
        layout_filtres.addWidget(QLabel("👤 Nom / Prénom :"), 0, 0)
        layout_filtres.addWidget(self.champ_nom, 0, 1)
        layout_filtres.addWidget(QLabel("📧 Email :"), 0, 2)
        layout_filtres.addWidget(self.champ_email, 0, 3)
        
        layout_filtres.addWidget(QLabel("📞 Téléphone :"), 1, 0)
        layout_filtres.addWidget(self.champ_tel, 1, 1)
        layout_filtres.addWidget(QLabel("🏠 Adresse :"), 1, 2)
        layout_filtres.addWidget(self.champ_adresse, 1, 3)
        
        layout_filtres.addWidget(QLabel("🚗 Marque / Modèle :"), 2, 0)
        layout_filtres.addWidget(self.champ_vehicule, 2, 1)
        layout_filtres.addWidget(QLabel("🔢 Immatriculation :"), 2, 2)
        layout_filtres.addWidget(self.champ_immat, 2, 3)
        
        layout_filtres.addWidget(QLabel("🗺️ Destination :"), 3, 0)
        layout_filtres.addWidget(self.champ_destination, 3, 1, 1, 3)

        self.layout_principal.addWidget(groupe_filtres)

        # 3. CONNEXION DES SIGNAUX (La magie du temps réel)
        self.champ_nom.textChanged.connect(self.charger_donnees)
        self.champ_email.textChanged.connect(self.charger_donnees)
        self.champ_tel.textChanged.connect(self.charger_donnees)
        self.champ_adresse.textChanged.connect(self.charger_donnees)
        self.champ_immat.textChanged.connect(self.charger_donnees)
        self.champ_vehicule.textChanged.connect(self.charger_donnees)
        self.champ_destination.textChanged.connect(self.charger_donnees)

        # 4. TABLEAU DES RÉSULTATS
        self.table_resultats = QTableWidget()
        self.table_resultats.setColumnCount(7)
        self.table_resultats.setHorizontalHeaderLabels([
            "N°", "Nom et Prénom du Client", "Email du Client", 
            "Période (A-M-J) de Location", "Lieu de Destination", 
            "Immatriculation", "Modèle et Marque"
        ])
        # Ajustement des colonnes pour utiliser toute la largeur
        self.table_resultats.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_resultats.setStyleSheet("QTableWidget { font-size: 13px; alternate-background-color: #f2f6f8; } QHeaderView::section { background-color: #34495e; color: white; font-weight: bold; padding: 4px; }")
        self.table_resultats.setAlternatingRowColors(True)
        self.layout_principal.addWidget(self.table_resultats)

        # Chargement initial complet
        self.charger_donnees()

    def charger_donnees(self):
        # Récupération de ce qui est tapé (avec % pour la recherche partielle SQL)
        nom_filtre = f"%{self.champ_nom.text().strip()}%"
        email_filtre = f"%{self.champ_email.text().strip()}%"
        tel_filtre = f"%{self.champ_tel.text().strip()}%"
        adresse_filtre = f"%{self.champ_adresse.text().strip()}%"
        immat_filtre = f"%{self.champ_immat.text().strip()}%"
        vehicule_filtre = f"%{self.champ_vehicule.text().strip()}%"
        dest_filtre = f"%{self.champ_destination.text().strip()}%"

        try:
            conn = self.db_connect()
            cursor = conn.cursor()

            # La requête fusionne intelligemment les Locations classiques ET les Voyages
            requete = """
                SELECT * FROM (
                    -- Bloc 1 : Les locations simples
                    SELECT 
                        'LOC-' || L.id_location AS numero,
                        C.nom || ' ' || COALESCE(C.prenom, '') AS nom_complet,
                        COALESCE(C.email, 'Non renseigné') AS email,
                        COALESCE(SUBSTR(L.date_sortie, 1, 10), 'Inconnue') AS periode,
                        'Non spécifié' AS destination,
                        V.immatriculation AS immat,
                        V.marque || ' ' || COALESCE(V.modele, '') AS marque_modele,
                        COALESCE(C.telephone, '') AS tel,
                        COALESCE(C.adresse, '') AS adresse
                    FROM LOCATION L
                    JOIN CLIENT C ON L.id_client = C.id_client
                    JOIN VEHICULE V ON L.immatriculation = V.immatriculation

                    UNION ALL

                    -- Bloc 2 : Les voyages (avec destination)
                    SELECT 
                        'VOY-' || Y.id_voyage AS numero,
                        C.nom || ' ' || COALESCE(C.prenom, '') AS nom_complet,
                        COALESCE(C.email, 'Non renseigné') AS email,
                        COALESCE(SUBSTR(Y.date_debut_planifiee, 1, 10), 'Inconnue') AS periode,
                        COALESCE(Y.lieu_arrivee, 'Non spécifié') AS destination,
                        V.immatriculation AS immat,
                        V.marque || ' ' || COALESCE(V.modele, '') AS marque_modele,
                        COALESCE(C.telephone, '') AS tel,
                        COALESCE(C.adresse, '') AS adresse
                    FROM VOYAGE Y
                    JOIN CLIENT C ON Y.id_client = C.id_client
                    JOIN VEHICULE V ON Y.immatriculation = V.immatriculation
                )
                WHERE nom_complet LIKE ? 
                  AND email LIKE ?
                  AND tel LIKE ?
                  AND adresse LIKE ?
                  AND immat LIKE ?
                  AND marque_modele LIKE ?
                  AND destination LIKE ?
                ORDER BY periode DESC
            """
            
            cursor.execute(requete, (nom_filtre, email_filtre, tel_filtre, adresse_filtre, immat_filtre, vehicule_filtre, dest_filtre))
            lignes = cursor.fetchall()
            
            self.table_resultats.setRowCount(len(lignes))
            for row, data in enumerate(lignes):
                # data = (numero, nom_complet, email, periode, destination, immat, marque_modele, tel, adresse)
                for col in range(7):
                    item = QTableWidgetItem(str(data[col]))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) # Rendre non modifiable
                    self.table_resultats.setItem(row, col, item)

        except sqlite3.Error as e:
            print(f"Erreur DB Recherche: {e}")
        finally:
            if 'conn' in locals() and conn: conn.close()