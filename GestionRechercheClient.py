# -*- coding: utf-8 -*-
import sqlite3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QGroupBox, QDateTimeEdit, QCheckBox)
from PyQt6.QtCore import Qt, QDateTime

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

        # Création des champs de recherche textes
        self.champ_nom = QLineEdit(); self.champ_nom.setPlaceholderText("Ex: Dupont...")
        self.champ_email = QLineEdit(); self.champ_email.setPlaceholderText("Ex: @gmail.com...")
        self.champ_tel = QLineEdit(); self.champ_tel.setPlaceholderText("Ex: 06...")
        self.champ_adresse = QLineEdit(); self.champ_adresse.setPlaceholderText("Ex: Paris...")
        self.champ_vehicule = QLineEdit(); self.champ_vehicule.setPlaceholderText("Ex: Toyota Yaris...")
        self.champ_immat = QLineEdit(); self.champ_immat.setPlaceholderText("Ex: AB-123-CD...")
        self.champ_destination = QLineEdit(); self.champ_destination.setPlaceholderText("Ex: Aéroport...")

        # CASE À COCHER POUR ACTIVER LA RECHERCHE PAR INTERVALLE
        self.check_filtrer_dates = QCheckBox("Activer la recherche par intervalle de dates")
        self.check_filtrer_dates.setStyleSheet("color: #d35400; font-weight: bold;")

        # CRÉATION DES DATEPICKERS (INTERVALLE MIN - MAX)
        # --- Date Minimum (Du...) ---
        self.champ_date_debut = QDateTimeEdit()
        self.champ_date_debut.setCalendarPopup(True)
        self.champ_date_debut.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.champ_date_debut.setDateTime(QDateTime.currentDateTime()) 
        self.champ_date_debut.setEnabled(False) 

        # --- Date Maximum (Au...) ---
        self.champ_date_fin = QDateTimeEdit()
        self.champ_date_fin.setCalendarPopup(True)
        self.champ_date_fin.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.champ_date_fin.setDateTime(QDateTime.currentDateTime().addDays(1)) 
        self.champ_date_fin.setEnabled(False) 

        # Sécurité : La Date Max ne peut pas être inférieure à la Date Min
        self.champ_date_debut.dateTimeChanged.connect(lambda dt: self.champ_date_fin.setMinimumDateTime(dt))

        # Placement dans la grille de recherche
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
        layout_filtres.addWidget(self.champ_destination, 3, 1)
        
        layout_filtres.addWidget(self.check_filtrer_dates, 4, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_filtres.addWidget(QLabel("📅 DU (Date Minimum) :"), 5, 0)
        layout_filtres.addWidget(self.champ_date_debut, 5, 1)
        layout_filtres.addWidget(QLabel("🏁 AU (Date Maximum) :"), 5, 2)
        layout_filtres.addWidget(self.champ_date_fin, 5, 3)

        self.layout_principal.addWidget(groupe_filtres)

        # 3. CONNEXION DES SIGNAUX
        self.champ_nom.textChanged.connect(self.charger_donnees)
        self.champ_email.textChanged.connect(self.charger_donnees)
        self.champ_tel.textChanged.connect(self.charger_donnees)
        self.champ_adresse.textChanged.connect(self.charger_donnees)
        self.champ_vehicule.textChanged.connect(self.charger_donnees)
        self.champ_immat.textChanged.connect(self.charger_donnees)
        self.champ_destination.textChanged.connect(self.charger_donnees)
        
        self.check_filtrer_dates.toggled.connect(self.basculer_filtre_dates)
        self.check_filtrer_dates.toggled.connect(self.charger_donnees)
        self.champ_date_debut.dateTimeChanged.connect(self.charger_donnees)
        self.champ_date_fin.dateTimeChanged.connect(self.charger_donnees)

        # 4. TABLEAU DES RÉSULTATS
        self.table_resultats = QTableWidget()
        self.table_resultats.setColumnCount(8)
        self.table_resultats.setHorizontalHeaderLabels([
            "N°", "Client", "Email", 
            "Date de Début", "Date de Fin", 
            "Destination", "Véhicule", "Immat."
        ])
        
        self.table_resultats.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_resultats.setStyleSheet("QTableWidget { font-size: 13px; alternate-background-color: #f2f6f8; } QHeaderView::section { background-color: #34495e; color: white; font-weight: bold; padding: 4px; }")
        self.table_resultats.setAlternatingRowColors(True)
        self.layout_principal.addWidget(self.table_resultats)

        self.charger_donnees()

    def basculer_filtre_dates(self, etat):
        self.champ_date_debut.setEnabled(etat)
        self.champ_date_fin.setEnabled(etat)

    def charger_donnees(self):
        nom_filtre = f"%{self.champ_nom.text().strip()}%"
        email_filtre = f"%{self.champ_email.text().strip()}%"
        tel_filtre = f"%{self.champ_tel.text().strip()}%"
        adresse_filtre = f"%{self.champ_adresse.text().strip()}%"
        vehicule_filtre = f"%{self.champ_vehicule.text().strip()}%"
        immat_filtre = f"%{self.champ_immat.text().strip()}%"
        dest_filtre = f"%{self.champ_destination.text().strip()}%"
        
        parametres = [nom_filtre, email_filtre, tel_filtre, adresse_filtre, vehicule_filtre, immat_filtre, dest_filtre]

        try:
            conn = self.db_connect()
            cursor = conn.cursor()

            requete = """
                SELECT * FROM (
                    -- Bloc 1 : Les locations simples
                    SELECT 
                        'LOC-' || L.id_location AS numero,
                        C.nom || ' ' || COALESCE(C.prenom, '') AS nom_complet,
                        COALESCE(C.email, 'Non renseigné') AS email,
                        COALESCE(SUBSTR(L.date_sortie, 1, 16), '?') AS date_debut,
                        COALESCE(SUBSTR(COALESCE(L.date_retour_reelle, L.date_retour_prevue), 1, 16), '?') AS date_fin,
                        COALESCE(L.lieu_arrivee, 'Non spécifié') AS destination,
                        V.marque || ' ' || COALESCE(V.modele, '') AS marque_modele,
                        V.immatriculation AS immat,
                        COALESCE(C.telephone, '') AS tel,
                        COALESCE(C.adresse, '') AS adresse
                    FROM LOCATION L
                    JOIN CLIENT C ON L.id_client = C.id_client
                    JOIN VEHICULE V ON L.immatriculation = V.immatriculation

                    UNION ALL

                    -- Bloc 2 : Les voyages spécifiques
                    SELECT 
                        'VOY-' || Y.id_voyage AS numero,
                        C.nom || ' ' || COALESCE(C.prenom, '') AS nom_complet,
                        COALESCE(C.email, 'Non renseigné') AS email,
                        COALESCE(SUBSTR(Y.date_debut_planifiee, 1, 16), '?') AS date_debut,
                        COALESCE(SUBSTR(Y.date_fin_reelle, 1, 16), 'En cours') AS date_fin,
                        COALESCE(Y.lieu_arrivee, 'Non spécifié') AS destination,
                        V.marque || ' ' || COALESCE(V.modele, '') AS marque_modele,
                        V.immatriculation AS immat,
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
                  AND marque_modele LIKE ?
                  AND immat LIKE ?
                  AND destination LIKE ?
            """
            
            # 🎯 LA CORRECTION EST ICI : 
            # On vérifie bien la colonne "date_debut" avec le Min ET la colonne "date_fin" avec le Max !
            if self.check_filtrer_dates.isChecked():
                date_min = self.champ_date_debut.dateTime().toString("yyyy-MM-dd HH:mm")
                date_max = self.champ_date_fin.dateTime().toString("yyyy-MM-dd HH:mm")
                
                requete += " AND date_debut >= ? AND (date_fin <= ? OR date_fin = 'En cours' OR date_fin = '?')"
                parametres.extend([date_min, date_max])

            requete += " ORDER BY date_debut DESC"
            
            cursor.execute(requete, parametres)
            lignes = cursor.fetchall()
            
            self.table_resultats.setRowCount(len(lignes))
            for row, data in enumerate(lignes):
                for col in range(8):
                    item = QTableWidgetItem(str(data[col]))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) 
                    self.table_resultats.setItem(row, col, item)

        except sqlite3.Error as e:
            print(f"Erreur DB Recherche: {e}")
        finally:
            if 'conn' in locals() and conn: conn.close()