# -*- coding: utf-8 -*-
import sqlite3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt

class GestionClient(QWidget):
    def __init__(self, db_connect_func):
        super().__init__()
        self.db_connect = db_connect_func
        self.layout_principal = QVBoxLayout(self)

        titre = QLabel("👥 Gestion des Clients")
        titre.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        self.layout_principal.addWidget(titre)

        # Formulaire
        self.layout_form = QHBoxLayout()
        self.champ_nom = QLineEdit(); self.champ_nom.setPlaceholderText("Nom")
        self.champ_prenom = QLineEdit(); self.champ_prenom.setPlaceholderText("Prénom")
        self.champ_email = QLineEdit(); self.champ_email.setPlaceholderText("Email")
        self.champ_tel = QLineEdit(); self.champ_tel.setPlaceholderText("Téléphone")
        
        self.layout_form.addWidget(self.champ_nom)
        self.layout_form.addWidget(self.champ_prenom)
        self.layout_form.addWidget(self.champ_email)
        self.layout_form.addWidget(self.champ_tel)
        self.layout_principal.addLayout(self.layout_form)

        # Boutons
        self.btn_ajouter = QPushButton("➕ Ajouter Client")
        self.btn_ajouter.clicked.connect(self.ajouter_client)
        self.layout_principal.addWidget(self.btn_ajouter)

        # Tableau
        self.table_clients = QTableWidget()
        self.table_clients.setColumnCount(5)
        self.table_clients.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Email", "Téléphone"])
        self.layout_principal.addWidget(self.table_clients)

        self.load_clients()

    def ajouter_client(self):
        nom = self.champ_nom.text().strip()
        prenom = self.champ_prenom.text().strip()
        email = self.champ_email.text().strip()
        tel = self.champ_tel.text().strip()

        if not nom or not email:
            return QMessageBox.warning(self, "Erreur", "Le nom et l'email sont obligatoires.")

        # 🛡️ LE BOUCLIER NIVEAU 3 EST ICI !
        from VerificateurEmail import verifier_email_complet
        est_valide, msg_erreur = verifier_email_complet(email)
        if not est_valide:
            return QMessageBox.warning(self, "Email Invalide", f"Enregistrement bloqué :\n\n{msg_erreur}")

        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO CLIENT (nom, prenom, email, telephone) VALUES (?, ?, ?, ?)", (nom, prenom, email, tel))
            conn.commit()
            self.champ_nom.clear(); self.champ_prenom.clear(); self.champ_email.clear(); self.champ_tel.clear()
            self.load_clients()
            QMessageBox.information(self, "Succès", "Client ajouté avec un email vérifié et valide !")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Erreur", "Cet email existe déjà dans la base.")
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def load_clients(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id_client, nom, prenom, email, telephone FROM CLIENT ORDER BY id_client DESC")
            lignes = cursor.fetchall()
            self.table_clients.setRowCount(len(lignes))
            for row, data in enumerate(lignes):
                for col, value in enumerate(data):
                    self.table_clients.setItem(row, col, QTableWidgetItem(str(value)))
        except sqlite3.Error as e: print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()