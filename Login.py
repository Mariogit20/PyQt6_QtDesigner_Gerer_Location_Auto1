# -*- coding: utf-8 -*-
import sys
import sqlite3
import hashlib
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.uic import loadUi

from utils import resource_path
from main import MainWindow, create_agence_tables
from GestionHistorique import GestionHistorique

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        loadUi(resource_path("Login.ui"), self)
        
        icon_path = resource_path("app_icon.png")
        self.setWindowIcon(QIcon(icon_path))
        
        self.setWindowTitle("Gestion de Location Automobile - Connexion")
        self.pushButton_connexion.setStyleSheet("") 
        
        self.lineEditPassword.setEchoMode(self.lineEditPassword.EchoMode.Password)
        self.pushButton_connexion.clicked.connect(self.verifier_identifiants)

    def verifier_identifiants(self):
        identifiant = self.lineEditLogin.text().strip()
        mot_de_passe_clair = self.lineEditPassword.text().strip()
        
        if not identifiant or not mot_de_passe_clair:
            return QMessageBox.warning(self, "Champs vides", "Veuillez saisir votre Login et Mot de passe.")

        mot_de_passe_hash = hashlib.sha256(mot_de_passe_clair.encode()).hexdigest()

        try:
            conn = sqlite3.connect('bdd.db')
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM UTILISATEUR WHERE login = ? AND password = ?", (identifiant, mot_de_passe_hash))
            utilisateur = cursor.fetchone()

            if utilisateur:
                role_utilisateur = utilisateur[0]
                
                def db_connect_local():
                    c = sqlite3.connect('bdd.db')
                    c.execute('PRAGMA foreign_keys = ON;')
                    return c
                
                GestionHistorique.ajouter_log(
                    db_connect_local, 
                    identifiant, 
                    "Connexion Système", 
                    f"Session ouverte avec le rôle : {role_utilisateur}"
                )

                self.main_window = MainWindow(role=role_utilisateur, login=identifiant)
                self.main_window.show()
                self.close()
            else:
                QMessageBox.critical(self, "Accès Refusé", "Identifiant ou mot de passe incorrect.")
                self.lineEditPassword.clear()
                self.lineEditPassword.setFocus()
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur BDD", f"Erreur de lecture : {e}")
        finally:
            if 'conn' in locals() and conn: conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    from style import STYLE_GLOBAL
    app.setStyleSheet(STYLE_GLOBAL)
    
    try:
        create_agence_tables()
    except Exception:
        pass
        
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())