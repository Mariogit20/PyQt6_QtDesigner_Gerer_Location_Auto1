import sqlite3
from PyQt6.QtWidgets import QWidget, QMessageBox, QTreeWidgetItem
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSignal, Qt 
from datetime import datetime

from utils import resource_path
from GestionHistorique import GestionHistorique

class GestionReparation(QWidget):
    reparation_terminee = pyqtSignal()
    
    def __init__(self, db_connect_func):
        super().__init__()
        loadUi(resource_path("GestionReparation.ui"), self)
        self.db_connect = db_connect_func 
        self.date_debut.setDate(datetime.now().date())
        self.date_fin.setDate(datetime.now().date())
        self.btn_enregistrer.clicked.connect(self.enregistrer_reparation)
        self.btn_cloturer.clicked.connect(self.cloturer_reparation)
        self.tableReparations.itemSelectionChanged.connect(self.charger_champs_reparation)
        self.charger_vehicules_a_reparer()
        self.load_reparations()
    
    def charger_vehicules_a_reparer(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT immatriculation, statut_disponibilite FROM VEHICULE WHERE statut_disponibilite != 'En location' ORDER BY immatriculation") 
            self.combo_vehicule.clear()
            self.combo_vehicule.addItem("Sélectionner un véhicule...", "") 
            for immat, statut in cursor.fetchall():
                self.combo_vehicule.addItem(f"{immat} ({statut})", immat) 
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def load_reparations(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT R.id_reparation, R.immatriculation, Ve.marque, Ve.modele, 
                       R.type_maintenance, R.nature_panne_tache, R.date_debut_reparation, 
                       R.statut_reparation, COALESCE(R.cout_main_d_oeuvre, 0) 
                FROM REPARATION R
                JOIN VEHICULE Ve ON R.immatriculation = Ve.immatriculation
                ORDER BY R.id_reparation DESC
            """)
            self.tableReparations.clear() 
            self.tableReparations.setHeaderLabels(["ID Rép.", "Immat.", "Marque", "Modèle", "Type", "Nature", "Début", "Statut", "Coût MO"])
            for row_data in cursor.fetchall():
                item = QTreeWidgetItem(self.tableReparations)
                for col_num, data in enumerate(row_data): item.setText(col_num, str(data))
                item.setData(0, Qt.ItemDataRole.UserRole, row_data[0]) 
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def charger_champs_reparation(self):
        selected_item = self.tableReparations.currentItem() 
        if selected_item:
            self.input_cout_mo.setText(selected_item.text(8).replace(' €', '').replace(',', '.'))

    def enregistrer_reparation(self):
        immatriculation = self.combo_vehicule.currentData()
        type_maintenance = self.combo_type_maintenance.currentText().split('(')[0].strip()
        nature = self.input_nature.text().strip()
        date_debut = self.date_debut.date().toString("yyyy-MM-dd")
        date_debut_db = f"{date_debut} 00:00:00"
        
        if not immatriculation or not nature: 
            return QMessageBox.warning(self, "Erreur", "Véhicule et Nature requis.")
        
        try:
            conn = self.db_connect()
            cursor = conn.cursor()

            # ==========================================
            # 🛡️ BOUCLIER ANTI-CHEVAUCHEMENT GLOBAL 
            # ==========================================
            # Test contre une Location
            cursor.execute("""
                SELECT date_sortie, COALESCE(date_retour_prevue, '2099-12-31') 
                FROM LOCATION 
                WHERE immatriculation = ? 
                AND statut_location IN ('Planifiée', 'En cours', 'En location')
                AND COALESCE(date_retour_reelle, date_retour_prevue, '2099-12-31') >= ?
            """, (immatriculation, date_debut_db))
            chev_loc = cursor.fetchone()
            if chev_loc:
                return QMessageBox.warning(self, "Bouclier Activé 🛡️", f"Impossible : ce véhicule est déjà prévu pour une LOCATION du {chev_loc[0]} au {chev_loc[1]}.")

            # Test contre un Voyage
            cursor.execute("""
                SELECT date_debut_planifiee 
                FROM VOYAGE 
                WHERE immatriculation = ? 
                AND statut_voyage IN ('Planifié', 'En cours')
                AND date_debut_planifiee >= ?
            """, (immatriculation, date_debut_db))
            chev_voy = cursor.fetchone()
            if chev_voy:
                return QMessageBox.warning(self, "Bouclier Activé 🛡️", f"Impossible : un VOYAGE est prévu pour ce véhicule le {chev_voy[0]}.")
            # ==========================================

            cursor.execute("INSERT INTO REPARATION (immatriculation, type_maintenance, nature_panne_tache, date_debut_reparation, statut_reparation) VALUES (?, ?, ?, ?, 'En cours')", (immatriculation, type_maintenance, nature, date_debut))
            cursor.execute("UPDATE VEHICULE SET statut_disponibilite = 'En réparation' WHERE immatriculation = ?", (immatriculation,))
            conn.commit()
            
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Ouverture Réparation", f"Véhicule {immatriculation} en maintenance ({nature})")

        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.load_reparations()
        self.charger_vehicules_a_reparer()

    def cloturer_reparation(self):
        selected_item = self.tableReparations.currentItem()
        if not selected_item or selected_item.text(7) != 'En cours': 
            return QMessageBox.warning(self, "Erreur", "Sélectionnez une réparation 'En cours'.")
            
        id_reparation = selected_item.data(0, Qt.ItemDataRole.UserRole)
        immatriculation = selected_item.text(1)
        cout_mo = self.input_cout_mo.text().strip().replace(',', '.') or "0"
        description = self.input_description_travaux.toPlainText().strip()
        date_fin = self.date_fin.date().toString("yyyy-MM-dd")
        
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE REPARATION SET statut_reparation = 'Terminée', date_fin_reparation = ?, cout_main_d_oeuvre = ?, description_travaux = ? WHERE id_reparation = ?", (date_fin, float(cout_mo), description, id_reparation)) 
            cursor.execute("UPDATE VEHICULE SET statut_disponibilite = 'Disponible' WHERE immatriculation = ?", (immatriculation,))
            conn.commit()
            
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Clôture Réparation", f"Maintenance terminée pour {immatriculation} (Coût: {cout_mo}€)")

            QMessageBox.information(self, "Succès", "Réparation clôturée. Véhicule disponible.")
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.load_reparations()
        self.charger_vehicules_a_reparer()
        self.reparation_terminee.emit()