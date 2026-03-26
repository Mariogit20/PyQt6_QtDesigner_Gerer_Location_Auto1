# -*- coding: utf-8 -*-
import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class GestionAccueil(QWidget):
    def __init__(self, db_connect_func):
        super().__init__()
        self.db_connect = db_connect_func
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(20, 20, 20, 20)
        self.layout_principal.setSpacing(20)

        # Titre de la page
        titre = QLabel("📊 Tableau de Bord")
        titre.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_principal.addWidget(titre)

        # Grille pour les cartes (Kpis)
        self.grille_kpi = QGridLayout()
        self.layout_principal.addLayout(self.grille_kpi)

        self.layout_principal.addStretch() # Pousse tout vers le haut

        self.charger_statistiques()

    def creer_carte(self, titre, valeur, couleur, icone):
        carte = QFrame()
        carte.setStyleSheet(f"""
            QFrame {{
                background-color: {couleur};
                border-radius: 10px;
                padding: 15px;
            }}
            QLabel {{ color: white; }}
        """)
        layout = QVBoxLayout(carte)
        
        lbl_icone = QLabel(icone)
        lbl_icone.setStyleSheet("font-size: 40px;")
        lbl_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_valeur = QLabel(str(valeur))
        lbl_valeur.setStyleSheet("font-size: 32px; font-weight: bold;")
        lbl_valeur.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_titre = QLabel(titre)
        lbl_titre.setStyleSheet("font-size: 14px; font-weight: bold;")
        lbl_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(lbl_icone)
        layout.addWidget(lbl_valeur)
        layout.addWidget(lbl_titre)
        
        return carte

    def charger_statistiques(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()

            # 1. Véhicules en location
            cursor.execute("SELECT COUNT(*) FROM VEHICULE WHERE statut_disponibilite = 'En location'")
            vehicules_loues = cursor.fetchone()[0]

            # 2. Assurances à renouveler (< 30 jours)
            cursor.execute("SELECT COUNT(*) FROM VEHICULE WHERE date_echeance_assurance <= date('now', '+30 days')")
            assurances_alertes = cursor.fetchone()[0]

            # 3. CA du mois en cours
            cursor.execute("SELECT SUM(montant_HT) FROM FACTURE_CLIENT WHERE strftime('%Y-%m', date_emission) = strftime('%Y-%m', 'now')")
            ca_mois = cursor.fetchone()[0] or 0.0

            # 4. Véhicules au garage
            cursor.execute("SELECT COUNT(*) FROM VEHICULE WHERE statut_disponibilite = 'En réparation'")
            vehicules_garage = cursor.fetchone()[0]

            # Vider la grille avant de la remplir (utile lors des rafraîchissements)
            for i in reversed(range(self.grille_kpi.count())): 
                self.grille_kpi.itemAt(i).widget().setParent(None)

            # Ajouter les cartes dans la grille (Ligne, Colonne)
            self.grille_kpi.addWidget(self.creer_carte("En Location", vehicules_loues, "#3498db", "🚗"), 0, 0)
            self.grille_kpi.addWidget(self.creer_carte("Assurances à Renouveler", assurances_alertes, "#e74c3c", "⚠️"), 0, 1)
            self.grille_kpi.addWidget(self.creer_carte("CA du Mois (HT)", f"{ca_mois:.2f} €", "#2ecc71", "💰"), 1, 0)
            self.grille_kpi.addWidget(self.creer_carte("Au Garage", vehicules_garage, "#f39c12", "🔧"), 1, 1)

        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()