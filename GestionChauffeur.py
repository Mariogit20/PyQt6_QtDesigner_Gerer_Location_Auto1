import sqlite3
from PyQt6.QtWidgets import QWidget, QMessageBox, QTreeWidgetItem
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSignal, Qt

from utils import resource_path
from GestionHistorique import GestionHistorique # 🎯 IMPORT HISTORIQUE

class GestionChauffeur(QWidget):
    chauffeur_modifie = pyqtSignal()
    
    def __init__(self, db_connect_func):
        super().__init__()
        loadUi(resource_path("GestionChauffeur.ui"), self)
        self.db_connect = db_connect_func 
        
        self.btn_nouveau.clicked.connect(self.nouveau_enregistrement)
        self.btn_ajouter.clicked.connect(self.ajouter_chauffeur)
        self.btn_modifier.clicked.connect(self.modifier_chauffeur)
        self.btn_supprimer.clicked.connect(self.supprimer_chauffeur)
        self.tableChauffeurs.itemSelectionChanged.connect(self.charger_champs)
        self.load_chauffeurs()

    def nouveau_enregistrement(self):
        self.tableChauffeurs.clearSelection()
        self.input_nom.clear(); self.input_prenom.clear(); self.input_tel.clear(); self.input_permis.clear()
        self.input_nom.setFocus()

    def load_chauffeurs(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id_chauffeur, nom, prenom, telephone, type_permis FROM CHAUFFEUR")
            self.tableChauffeurs.clear()
            self.tableChauffeurs.setHeaderLabels(["ID", "Nom", "Prénom", "Téléphone", "Permis"])
            for row in cursor.fetchall():
                item = QTreeWidgetItem(self.tableChauffeurs)
                for col, data in enumerate(row): item.setText(col, str(data))
                item.setData(0, Qt.ItemDataRole.UserRole, row[0])
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def charger_champs(self):
        selected = self.tableChauffeurs.currentItem()
        if selected:
            self.input_nom.setText(selected.text(1))
            self.input_prenom.setText(selected.text(2))
            self.input_tel.setText(selected.text(3))
            self.input_permis.setText(selected.text(4))

    def ajouter_chauffeur(self):
        nom, prenom, tel, permis = self.input_nom.text().upper(), self.input_prenom.text(), self.input_tel.text(), self.input_permis.text().upper()
        if not nom or not prenom: return QMessageBox.warning(self, "Erreur", "Nom et Prénom obligatoires.")
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO CHAUFFEUR (nom, prenom, telephone, type_permis) VALUES (?, ?, ?, ?)", (nom, prenom, tel, permis))
            conn.commit()
            
            # 🎯 LOG HISTORIQUE
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Ajout Chauffeur", f"Chauffeur {nom} {prenom} ajouté")
            
        except sqlite3.IntegrityError: 
            return QMessageBox.warning(self, "Erreur", "Téléphone déjà utilisé.")
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.load_chauffeurs()
        self.chauffeur_modifie.emit()
        self.nouveau_enregistrement() 

    def modifier_chauffeur(self):
        selected = self.tableChauffeurs.currentItem()
        if not selected: return
        id_chauffeur = selected.data(0, Qt.ItemDataRole.UserRole)
        
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE CHAUFFEUR SET nom=?, prenom=?, telephone=?, type_permis=? WHERE id_chauffeur=?", 
                           (self.input_nom.text().upper(), self.input_prenom.text(), self.input_tel.text(), self.input_permis.text().upper(), id_chauffeur))
            conn.commit()
            
            # 🎯 LOG HISTORIQUE
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Modif. Chauffeur", f"Mise à jour du chauffeur ID {id_chauffeur}")
            
            QMessageBox.information(self, "Succès", "Chauffeur modifié avec succès.")
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.load_chauffeurs()
        self.chauffeur_modifie.emit()

    def supprimer_chauffeur(self):
        selected = self.tableChauffeurs.currentItem()
        if not selected: return
        id_chauffeur = selected.data(0, Qt.ItemDataRole.UserRole)
        nom = selected.text(1)
        
        if QMessageBox.question(self, 'Confirmation', "Supprimer ce chauffeur ?") == QMessageBox.StandardButton.Yes:
            try:
                conn = self.db_connect()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM CHAUFFEUR WHERE id_chauffeur=?", (id_chauffeur,))
                conn.commit()
                
                # 🎯 LOG HISTORIQUE
                GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Suppression Chauffeur", f"Chauffeur {nom} supprimé")
                
            except sqlite3.IntegrityError:
                return QMessageBox.critical(self, "Suppression Interdite", "Ce chauffeur a déjà effectué des locations.\nImpossible de le supprimer pour conserver l'historique comptable.")
            except sqlite3.Error as e:
                print(e)
            finally:
                if 'conn' in locals() and conn: conn.close()
                
            self.load_chauffeurs()
            self.chauffeur_modifie.emit()
            self.nouveau_enregistrement()