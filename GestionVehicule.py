import sqlite3
from PyQt6.QtCore import pyqtSignal, QDate
from PyQt6.QtWidgets import QWidget, QMessageBox, QTreeWidgetItem
from PyQt6.uic import loadUi

from utils import resource_path
from GestionHistorique import GestionHistorique  # 🎯 IMPORT HISTORIQUE

class GestionVehicule(QWidget):
    vehicule_modifie = pyqtSignal()
    
    def __init__(self, db_connect_func):
        super().__init__()
        loadUi(resource_path("GestionVehicule.ui"), self)
        self.db_connect = db_connect_func 

        self.btn_nouveau.clicked.connect(self.nouveau_enregistrement)
        self.btn_ajouter.clicked.connect(self.ajouter_vehicule)
        self.btn_modifier.clicked.connect(self.modifier_vehicule)
        self.btn_supprimer.clicked.connect(self.supprimer_vehicule)
        self.tableVehicules.itemSelectionChanged.connect(self.charger_champs_vehicule)
        
        self.combo_statut.setEnabled(False) 
        self.input_assurance.setDate(QDate.currentDate())
        self.load_vehicules()

    def nouveau_enregistrement(self):
        self.tableVehicules.clearSelection()
        self.input_immat.clear()
        self.input_marque.clear()
        self.input_modele.clear()
        self.input_kilometrage.clear()
        self.input_assurance.setDate(QDate.currentDate())
        self.combo_statut.setCurrentText("Disponible")
        self.input_immat.setFocus()

    def load_vehicules(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT immatriculation, marque, modele, kilometrage_actuel, statut_disponibilite, date_echeance_assurance FROM VEHICULE ORDER BY immatriculation")
            self.tableVehicules.clear()
            self.tableVehicules.setHeaderLabels(["Immat", "Marque", "Modèle", "Km", "Statut", "Assurance"])
            for row in cursor.fetchall():
                item = QTreeWidgetItem(self.tableVehicules)
                for col, data in enumerate(row): item.setText(col, str(data if data else ''))
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def charger_champs_vehicule(self):
        selected_item = self.tableVehicules.currentItem() 
        if selected_item:
            self.input_immat.setText(selected_item.text(0))
            self.input_marque.setText(selected_item.text(1))
            self.input_modele.setText(selected_item.text(2))
            self.input_kilometrage.setText(selected_item.text(3))
            self.combo_statut.setCurrentText(selected_item.text(4))
            date_str = selected_item.text(5)
            if date_str: self.input_assurance.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))

    def ajouter_vehicule(self):
        immat, marque, modele = self.input_immat.text().strip().upper(), self.input_marque.text().strip(), self.input_modele.text().strip()
        kilometrage = self.input_kilometrage.text().strip() or "0"
        assurance = self.input_assurance.date().toString("yyyy-MM-dd") 
        
        if not immat or not marque: return QMessageBox.warning(self, "Erreur", "Immatriculation et Marque obligatoires.")
        
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO VEHICULE (immatriculation, marque, modele, kilometrage_actuel, statut_disponibilite, date_echeance_assurance, id_type) VALUES (?, ?, ?, ?, 'Disponible', ?, 1)", (immat, marque, modele, int(kilometrage), assurance))
            conn.commit()
            
            # 🎯 LOG HISTORIQUE
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Ajout Véhicule", f"Véhicule {marque} {modele} ajouté (Immat: {immat})")
            
        except sqlite3.IntegrityError: 
            return QMessageBox.warning(self, "Erreur", "Immatriculation existante.")
        except Exception as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.load_vehicules()
        self.vehicule_modifie.emit()
        self.nouveau_enregistrement()

    def modifier_vehicule(self):
        selected_item = self.tableVehicules.currentItem()
        if not selected_item: return
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE VEHICULE SET immatriculation=?, marque=?, modele=?, kilometrage_actuel=?, date_echeance_assurance=? WHERE immatriculation=?", 
                           (self.input_immat.text().strip().upper(), self.input_marque.text().strip(), self.input_modele.text().strip(), int(self.input_kilometrage.text().strip() or "0"), self.input_assurance.date().toString("yyyy-MM-dd"), selected_item.text(0)))
            conn.commit()
            
            # 🎯 LOG HISTORIQUE
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Modif. Véhicule", f"Mise à jour du véhicule {selected_item.text(0)}")
            
            QMessageBox.information(self, "Succès", "Véhicule modifié.")
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.load_vehicules()
        self.vehicule_modifie.emit()

    def supprimer_vehicule(self):
        selected_item = self.tableVehicules.currentItem()
        if not selected_item: return
        immat = selected_item.text(0)
        
        if QMessageBox.question(self, 'Confirmation', f"Supprimer {immat} ?") == QMessageBox.StandardButton.Yes:
            try:
                conn = self.db_connect()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM VEHICULE WHERE immatriculation = ?", (immat,))
                conn.commit()
                
                # 🎯 LOG HISTORIQUE
                GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Suppression Véhicule", f"Suppression du véhicule {immat}")
                
            except sqlite3.IntegrityError: 
                return QMessageBox.critical(self, "Erreur", "Impossible : historique existant.")
            except sqlite3.Error as e:
                print(e)
            finally:
                if 'conn' in locals() and conn: conn.close()
                
            self.load_vehicules()
            self.vehicule_modifie.emit() 
            self.nouveau_enregistrement()