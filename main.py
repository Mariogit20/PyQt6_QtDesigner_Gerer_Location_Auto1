# -*- coding: utf-8 -*-
import sqlite3
import sys
import hashlib
import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QMessageBox, QVBoxLayout,
    QDialog, QLabel, QTextEdit, QPushButton
)
from PyQt6.QtGui import QIcon  

from utils import resource_path

# 🎯 IMPORT DE TOUS VOS MODULES 
from GestionAccueil import GestionAccueil
from GestionIA import GestionIA  
from GestionLocation import GestionLocation
from GestionVehicule import GestionVehicule
from GestionReparation import GestionReparation
from GestionStockEtCommandes import GestionStockEtCommandes
from GestionClient import GestionClient
from GestionRechercheClient import GestionRechercheClient 
from GestionCarburant import GestionCarburant
from GestionChauffeur import GestionChauffeur  
from GestionUtilisateur import GestionUtilisateur 
from GestionHistorique import GestionHistorique
from GestionImportExport import GestionImportExport
from GestionPlanning import GestionPlanning
from GestionFournisseur import GestionFournisseur 
from GestionVoyage import GestionVoyage

def create_agence_tables():
    """Initialisation et mise à jour automatique de la base de données locale SQLite"""
    try:
        conn = sqlite3.connect('bdd.db')
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')

        cursor.execute('''CREATE TABLE IF NOT EXISTS CHAUFFEUR (id_chauffeur INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL, prenom TEXT NOT NULL, telephone TEXT UNIQUE, date_permis DATE, type_permis TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS CLIENT (id_client INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL, prenom TEXT, email TEXT UNIQUE NOT NULL, telephone TEXT, adresse TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS TYPE_VEHICULE (id_type INTEGER PRIMARY KEY AUTOINCREMENT, nom_type TEXT NOT NULL UNIQUE, intervalle_vidange_km INTEGER, intervalle_revision_mois INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS FOURNISSEUR (id_fournisseur INTEGER PRIMARY KEY AUTOINCREMENT, nom_fournisseur TEXT NOT NULL UNIQUE, contact TEXT, telephone TEXT, specialite TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS UTILISATEUR (id_user INTEGER PRIMARY KEY AUTOINCREMENT, login TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'Administrateur')''')
        default_password_hashed = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("INSERT OR IGNORE INTO UTILISATEUR (login, password, role) VALUES ('admin', ?, 'Administrateur')", (default_password_hashed,))

        cursor.execute('''CREATE TABLE IF NOT EXISTS VEHICULE (immatriculation TEXT PRIMARY KEY, marque TEXT NOT NULL, modele TEXT, annee INTEGER, kilometrage_actuel INTEGER DEFAULT 0, capacite_places INTEGER, statut_disponibilite TEXT NOT NULL DEFAULT 'Disponible', date_echeance_assurance DATE, id_type INTEGER NOT NULL, FOREIGN KEY(id_type) REFERENCES TYPE_VEHICULE(id_type) ON UPDATE CASCADE ON DELETE RESTRICT)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS LOCATION (id_location INTEGER PRIMARY KEY AUTOINCREMENT, date_sortie DATETIME NOT NULL, date_retour_prevue DATETIME, date_retour_reelle DATETIME, kilometrage_depart INTEGER, kilometrage_retour INTEGER, statut_location TEXT NOT NULL DEFAULT 'En cours', id_client INTEGER NOT NULL, immatriculation TEXT NOT NULL, id_chauffeur INTEGER, FOREIGN KEY(id_client) REFERENCES CLIENT(id_client) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY(immatriculation) REFERENCES VEHICULE(immatriculation) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY(id_chauffeur) REFERENCES CHAUFFEUR(id_chauffeur) ON UPDATE CASCADE ON DELETE SET NULL)''')
        
        try:
            cursor.execute("ALTER TABLE LOCATION ADD COLUMN confirmation_client BOOLEAN DEFAULT 0")
            cursor.execute("ALTER TABLE LOCATION ADD COLUMN date_envoi_confirmation DATETIME")
        except sqlite3.OperationalError:
            pass 

        # 🎯 AJOUT COLONNE LIEU ARRIVÉE POUR LES LOCATIONS
        try:
            cursor.execute("ALTER TABLE LOCATION ADD COLUMN lieu_arrivee TEXT")
        except sqlite3.OperationalError:
            pass 

        cursor.execute("PRAGMA table_info(VOYAGE)")
        colonnes_voyage = [info[1] for info in cursor.fetchall()]
        if colonnes_voyage and 'lieu_depart' not in colonnes_voyage:
            cursor.execute("DROP TABLE VOYAGE") 
            
        cursor.execute('''CREATE TABLE IF NOT EXISTS VOYAGE (
            id_voyage INTEGER PRIMARY KEY AUTOINCREMENT, id_client INTEGER NOT NULL, immatriculation TEXT NOT NULL, id_chauffeur INTEGER, lieu_depart TEXT, lieu_arrivee TEXT, date_debut_planifiee DATETIME, date_fin_reelle DATETIME, distance_estimee REAL, statut_voyage TEXT NOT NULL DEFAULT 'Planifié', FOREIGN KEY(id_client) REFERENCES CLIENT(id_client) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY(immatriculation) REFERENCES VEHICULE(immatriculation) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY(id_chauffeur) REFERENCES CHAUFFEUR(id_chauffeur) ON UPDATE CASCADE ON DELETE SET NULL
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS FACTURE_CLIENT (id_facture INTEGER PRIMARY KEY AUTOINCREMENT, date_emission DATE NOT NULL, date_echeance DATE, montant_HT REAL NOT NULL, montant_TVA REAL, statut_paiement TEXT NOT NULL DEFAULT 'En attente', id_location INTEGER UNIQUE, id_voyage INTEGER UNIQUE, FOREIGN KEY(id_location) REFERENCES LOCATION(id_location) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY(id_voyage) REFERENCES VOYAGE(id_voyage) ON UPDATE CASCADE ON DELETE RESTRICT)''')
        try:
            cursor.execute("ALTER TABLE FACTURE_CLIENT ADD COLUMN id_voyage INTEGER UNIQUE")
            cursor.execute("ALTER TABLE FACTURE_CLIENT ADD COLUMN date_echeance DATE")
        except sqlite3.OperationalError: pass 

        cursor.execute('''CREATE TABLE IF NOT EXISTS CONSOMMATION_CARBURANT (id_plein INTEGER PRIMARY KEY AUTOINCREMENT, date_plein DATE NOT NULL, montant REAL NOT NULL, litres REAL NOT NULL, immatriculation TEXT NOT NULL, FOREIGN KEY(immatriculation) REFERENCES VEHICULE(immatriculation) ON UPDATE CASCADE ON DELETE CASCADE)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS PIECE (id_piece INTEGER PRIMARY KEY AUTOINCREMENT, nom_piece TEXT NOT NULL, reference_fournisseur TEXT UNIQUE, prix_unitaire REAL NOT NULL, quantite_stock INTEGER DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS REPARATION (id_reparation INTEGER PRIMARY KEY AUTOINCREMENT, date_debut_reparation DATETIME NOT NULL, date_fin_reparation DATETIME, cout_main_d_oeuvre REAL, nature_panne_tache TEXT, description_travaux TEXT, type_maintenance TEXT NOT NULL, statut_reparation TEXT DEFAULT 'En cours', immatriculation TEXT NOT NULL, id_fournisseur INTEGER, FOREIGN KEY(immatriculation) REFERENCES VEHICULE(immatriculation) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY(id_fournisseur) REFERENCES FOURNISSEUR(id_fournisseur) ON UPDATE CASCADE ON DELETE SET NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS COMMANDE_REPARATION (id_commande INTEGER PRIMARY KEY AUTOINCREMENT, date_commande DATE NOT NULL, montant_estime REAL, statut_commande TEXT NOT NULL DEFAULT 'En cours', id_fournisseur INTEGER NOT NULL, FOREIGN KEY(id_fournisseur) REFERENCES FOURNISSEUR(id_fournisseur) ON UPDATE CASCADE ON DELETE RESTRICT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS UTILISER (id_commande INTEGER NOT NULL, id_piece INTEGER NOT NULL, quantite_utilisee INTEGER NOT NULL, PRIMARY KEY (id_commande, id_piece), FOREIGN KEY(id_commande) REFERENCES COMMANDE_REPARATION(id_commande) ON UPDATE CASCADE ON DELETE CASCADE, FOREIGN KEY(id_piece) REFERENCES PIECE(id_piece) ON UPDATE CASCADE ON DELETE RESTRICT)''')

        cursor.execute("INSERT OR IGNORE INTO TYPE_VEHICULE (nom_type) VALUES ('Voiture'), ('SUV'), ('Camionnette')")

        cursor.execute('''CREATE TABLE IF NOT EXISTS HISTORIQUE (id_historique INTEGER PRIMARY KEY AUTOINCREMENT, date_action DATETIME DEFAULT (datetime('now','localtime')), utilisateur TEXT, action TEXT, details TEXT)''')

        conn.commit()
    except Exception as e: print(f"Erreur init DB: {e}")
    finally:
        if 'conn' in locals() and conn: conn.close()


class MainWindow(QMainWindow):
    def __init__(self, role="Administrateur", login="admin"):
        super().__init__()
        self.role_utilisateur = role 
        self.login_utilisateur = login 
        
        icon_path = resource_path("app_icon.png")
        self.setWindowIcon(QIcon(icon_path))
        
        self.setWindowTitle(f"Système de Gestion de Location Automobile - Connecté en tant que : {self.role_utilisateur} ({self.login_utilisateur})")
        self.setGeometry(100, 100, 1400, 850) 
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.table = QTabWidget()
        self.table.setTabPosition(QTabWidget.TabPosition.North)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.table)
        
        self.setup_modules()
        self.verifier_assurances()

    def db_connect(self):
        conn = sqlite3.connect('bdd.db')
        conn.execute('PRAGMA foreign_keys = ON;')
        return conn

    def verifier_assurances(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT immatriculation, marque, modele, date_echeance_assurance FROM VEHICULE WHERE date_echeance_assurance IS NOT NULL AND date_echeance_assurance <= date('now', '+30 days') ORDER BY date_echeance_assurance ASC")
            vehicules_a_risques = cursor.fetchall()
            
            if vehicules_a_risques:
                dialog = QDialog(self)
                dialog.setWindowTitle("⚠️ Renouvellement d'Assurances Requis")
                dialog.resize(500, 400) 
                layout = QVBoxLayout(dialog)
                
                label_titre = QLabel("<b>Les véhicules suivants nécessitent un renouvellement d'assurance imminent :</b>")
                label_titre.setStyleSheet("font-size: 14px; color: #c0392b; padding-bottom: 10px;")
                layout.addWidget(label_titre)
                
                zone_texte = QTextEdit()
                zone_texte.setReadOnly(True) 
                zone_texte.setStyleSheet("background-color: #fdfde3; font-size: 13px; padding: 10px; border: 1px solid #bdc3c7;")
                
                texte_alerte = ""
                for immat, marque, modele, date_exp in vehicules_a_risques: 
                    texte_alerte += f"🚗 {immat} ({marque} {modele})\n   👉 Expire le : {date_exp}\n\n"
                zone_texte.setPlainText(texte_alerte)
                layout.addWidget(zone_texte)
                
                btn_ok = QPushButton("J'ai pris connaissance")
                btn_ok.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
                btn_ok.clicked.connect(dialog.accept) 
                layout.addWidget(btn_ok)
                
                dialog.exec()
        except Exception as e: pass
        finally:
            if 'conn' in locals() and conn: conn.close()

    def setup_modules(self):
        try:
            # 1. Initialisation
            self.gestion_accueil = GestionAccueil(self.db_connect)
            self.gestion_ia = GestionIA(self.db_connect) 
            self.gestion_recherche = GestionRechercheClient(self.db_connect) 
            self.gestion_client = GestionClient(self.db_connect)
            self.gestion_chauffeur = GestionChauffeur(self.db_connect)  
            self.gestion_vehicule = GestionVehicule(self.db_connect)
            self.gestion_location = GestionLocation(self.db_connect)
            self.gestion_voyage = GestionVoyage(self.db_connect) 
            self.gestion_carburant = GestionCarburant(self.db_connect, self.role_utilisateur)
            self.gestion_reparation = GestionReparation(self.db_connect)
            self.gestion_stock = GestionStockEtCommandes(self.db_connect)
            self.gestion_fournisseur = GestionFournisseur(self.db_connect)
            self.gestion_utilisateur = GestionUtilisateur(self.db_connect)
            self.gestion_historique = GestionHistorique(self.db_connect)
            self.gestion_import_export = GestionImportExport(self.db_connect)
            self.gestion_planning = GestionPlanning(self.db_connect)

            # 2. Ajout des onglets
            self.table.addTab(self.gestion_accueil, "🏠 Accueil (Dashboard)")
            self.table.addTab(self.gestion_ia, "🧠 IA & Prédictions") 
            self.table.addTab(self.gestion_planning, "🗓️ Planning & Dispos")
            self.table.addTab(self.gestion_location, "🔑 Locations (Ent/Sor)")
            self.table.addTab(self.gestion_voyage, "🗺️ Voyages & Facturation") 
            self.table.addTab(self.gestion_vehicule, "🚗 Flotte & Assurances")
            self.table.addTab(self.gestion_chauffeur, "👔 Chauffeurs")     
            self.table.addTab(self.gestion_carburant, "⛽ Suivi Carburant")
            self.table.addTab(self.gestion_reparation, "🔧 Maintenance")
            self.table.addTab(self.gestion_stock, "📦 Stock & Pièces")
            self.table.addTab(self.gestion_fournisseur, "🏭 Fournisseurs")

            # 3. Onglets Administrateur 
            if self.role_utilisateur == "Administrateur":
                self.table.addTab(self.gestion_client, "👥 Fichier Clients")
                self.table.addTab(self.gestion_recherche, "🔎 Recherche Globale Client") 
                self.table.addTab(self.gestion_utilisateur, "🛡️ Admin Utilisateurs") 
                self.table.addTab(self.gestion_historique, "📜 Historique (Logs)")
                self.table.addTab(self.gestion_import_export, "💾 Import / Export JSON")

            # 4. Connexions
            self.gestion_chauffeur.chauffeur_modifie.connect(self.gestion_location.charger_comboboxes)
            self.gestion_vehicule.vehicule_modifie.connect(self.gestion_location.charger_comboboxes)
            self.gestion_vehicule.vehicule_modifie.connect(self.gestion_reparation.charger_vehicules_a_reparer)
            self.gestion_vehicule.vehicule_modifie.connect(self.gestion_carburant.charger_vehicules)
            
            self.gestion_location.location_terminee.connect(self.gestion_vehicule.load_vehicules)
            self.gestion_location.location_terminee.connect(self.gestion_reparation.charger_vehicules_a_reparer)
            self.gestion_location.location_terminee.connect(self.gestion_accueil.charger_statistiques)
            
            self.gestion_reparation.reparation_terminee.connect(self.gestion_accueil.charger_statistiques)
            self.gestion_reparation.reparation_terminee.connect(self.gestion_vehicule.load_vehicules)
            self.gestion_reparation.reparation_terminee.connect(self.gestion_location.charger_comboboxes)
            
            self.gestion_fournisseur.fournisseur_modifie.connect(self.gestion_stock.charger_commandes)
            
            self.table.currentChanged.connect(self.rafraichir_onglet_actif)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de chargement: {e}")
            sys.exit(1)

    def rafraichir_onglet_actif(self, index_selectionne):
        onglet_actif = self.table.widget(index_selectionne)
        
        if onglet_actif == self.gestion_accueil: self.gestion_accueil.charger_statistiques()
        elif onglet_actif == self.gestion_vehicule: self.gestion_vehicule.load_vehicules()
        elif onglet_actif == self.gestion_chauffeur: self.gestion_chauffeur.load_chauffeurs()
        elif onglet_actif == self.gestion_location: 
            self.gestion_location.load_locations()
            self.gestion_location.charger_comboboxes() 
        elif onglet_actif == self.gestion_voyage: 
            self.gestion_voyage.load_voyages()
            self.gestion_voyage.charger_comboboxes() 
        elif onglet_actif == self.gestion_reparation: 
            self.gestion_reparation.load_reparations()
            self.gestion_reparation.charger_vehicules_a_reparer()
        elif onglet_actif == self.gestion_carburant: 
            self.gestion_carburant.load_pleins()
            self.gestion_carburant.charger_vehicules()
        elif onglet_actif == self.gestion_stock: 
            self.gestion_stock.charger_pieces()
            self.gestion_stock.charger_commandes()
        elif onglet_actif == self.gestion_fournisseur: self.gestion_fournisseur.load_fournisseurs()
        elif onglet_actif == self.gestion_utilisateur: self.gestion_utilisateur.load_users()
        elif onglet_actif == self.gestion_client: self.gestion_client.load_clients()
        elif onglet_actif == self.gestion_recherche: self.gestion_recherche.charger_donnees() 
        elif onglet_actif == self.gestion_historique: self.gestion_historique.load_history()
        elif onglet_actif == self.gestion_planning: 
            self.gestion_planning.charger_donnees()
            self.gestion_planning.generer_gantt()

    def closeEvent(self, event):
        dossier_backup = resource_path("Sauvegardes_Automatiques")
        if not os.path.exists(dossier_backup): os.makedirs(dossier_backup)
        
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        chemin_fichier = os.path.join(dossier_backup, f"Backup_Auto_{date_str}.json")
        
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]
            db_data = {}
            for table in tables:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                colonnes = [desc[0] for desc in cursor.description]
                db_data[table] = [dict(zip(colonnes, row)) for row in rows]
            
            with open(chemin_fichier, 'w', encoding='utf-8') as f: 
                json.dump(db_data, f, indent=4, ensure_ascii=False)
                
            GestionHistorique.ajouter_log(self.db_connect, "Système", "Auto-Backup", f"Sauvegarde locale générée : {chemin_fichier}")
            
        except Exception as e: print(f"Erreur lors de l'auto-backup : {e}")
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    from style import STYLE_GLOBAL
    app.setStyleSheet(STYLE_GLOBAL)
    try: 
        create_agence_tables()
    except Exception: pass
        
    window = MainWindow(role="Administrateur", login="admin") 
    window.show()
    sys.exit(app.exec())