import sqlite3
import hashlib
from PyQt6.QtWidgets import QWidget, QMessageBox, QTreeWidgetItem
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt

from utils import resource_path 
from GestionHistorique import GestionHistorique # 🎯 IMPORT HISTORIQUE

class GestionUtilisateur(QWidget):
    def __init__(self, db_connect_func):
        super().__init__()
        loadUi(resource_path("GestionUtilisateur.ui"), self)
        self.db_connect = db_connect_func

        self.input_password.setEchoMode(self.input_password.EchoMode.Password)
        self.btn_nouveau.clicked.connect(self.nouveau_enregistrement)
        self.btn_ajouter.clicked.connect(self.ajouter_user)
        self.btn_modifier.clicked.connect(self.modifier_user)
        self.btn_supprimer.clicked.connect(self.supprimer_user)
        self.tableUtilisateurs.itemSelectionChanged.connect(self.charger_champs)
        self.load_users()

    def nouveau_enregistrement(self):
        self.tableUtilisateurs.clearSelection()
        self.input_login.clear()
        self.input_password.clear()
        self.combo_role.setCurrentIndex(0)
        self.input_login.setFocus()

    def load_users(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id_user, login, role FROM UTILISATEUR")
            self.tableUtilisateurs.clear()
            self.tableUtilisateurs.setHeaderLabels(["ID", "Login", "Rôle"])
            for row in cursor.fetchall():
                item = QTreeWidgetItem(self.tableUtilisateurs)
                item.setText(0, str(row[0])); item.setText(1, str(row[1])); item.setText(2, str(row[2]))
                item.setData(0, Qt.ItemDataRole.UserRole, row[0])
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def charger_champs(self):
        selected = self.tableUtilisateurs.currentItem()
        if selected:
            self.input_login.setText(selected.text(1))
            self.combo_role.setCurrentText(selected.text(2))
            self.input_password.clear()

    def ajouter_user(self):
        login, password, role = self.input_login.text().strip(), self.input_password.text().strip(), self.combo_role.currentText()
        if not login or not password: 
            return QMessageBox.warning(self, "Erreur", "Login et mot de passe requis.")
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO UTILISATEUR (login, password, role) VALUES (?, ?, ?)", (login, password_hash, role))
            conn.commit()
            
            # 🎯 LOG HISTORIQUE
            GestionHistorique.ajouter_log(self.db_connect, "Administrateur", "Création Utilisateur", f"Nouveau compte: {login} ({role})")
            
        except sqlite3.IntegrityError: 
            return QMessageBox.warning(self, "Erreur", "Ce login existe déjà.")
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.load_users()
        self.nouveau_enregistrement()

    def modifier_user(self):
        selected = self.tableUtilisateurs.currentItem()
        if not selected: return
        
        id_user = selected.data(0, Qt.ItemDataRole.UserRole)
        login, password, role = self.input_login.text().strip(), self.input_password.text().strip(), self.combo_role.currentText()
        
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            if password: 
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("UPDATE UTILISATEUR SET login=?, password=?, role=? WHERE id_user=?", (login, password_hash, role, id_user))
            else: 
                cursor.execute("UPDATE UTILISATEUR SET login=?, role=? WHERE id_user=?", (login, role, id_user))
            conn.commit()
            
            # 🎯 LOG HISTORIQUE
            GestionHistorique.ajouter_log(self.db_connect, "Administrateur", "Modif. Utilisateur", f"Compte {login} mis à jour.")
            
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.load_users()
        QMessageBox.information(self, "Succès", "Accès mis à jour.")

    def supprimer_user(self):
        selected = self.tableUtilisateurs.currentItem()
        if not selected: return
        
        id_user = selected.data(0, Qt.ItemDataRole.UserRole)
        login = selected.text(1)
        
        if login.lower() == "admin": 
            return QMessageBox.critical(self, "Interdit", "Le compte admin principal est intouchable.")
            
        if QMessageBox.question(self, 'Confirmation', f"Supprimer l'accès de {login} ?") == QMessageBox.StandardButton.Yes:
            try:
                conn = self.db_connect()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM UTILISATEUR WHERE id_user=?", (id_user,))
                conn.commit()
                
                # 🎯 LOG HISTORIQUE
                GestionHistorique.ajouter_log(self.db_connect, "Administrateur", "Suppression Utilisateur", f"Compte {login} supprimé.")
                
            except sqlite3.Error: 
                pass
            finally:
                if 'conn' in locals() and conn: conn.close()
                
            self.load_users()
            self.nouveau_enregistrement()