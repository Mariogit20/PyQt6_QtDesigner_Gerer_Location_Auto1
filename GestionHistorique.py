# -*- coding: utf-8 -*-
import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QPushButton, QHBoxLayout, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt

class GestionHistorique(QWidget):
    def __init__(self, db_connect_func):
        super().__init__()
        self.db_connect = db_connect_func
        
        # --- Interface générée en code (Pas besoin de .ui) ---
        self.layout = QVBoxLayout(self)
        
        # Section des boutons avec les Emojis
        self.btn_layout = QHBoxLayout()
        self.btn_rafraichir = QPushButton("🔄 Actualiser l'historique")
        self.btn_rafraichir.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 8px; border-radius: 4px;")
        
        self.btn_vider = QPushButton("🗑️ Vider l'historique")
        self.btn_vider.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 8px; border-radius: 4px;")
        
        self.btn_layout.addWidget(self.btn_rafraichir)
        self.btn_layout.addWidget(self.btn_vider)
        self.layout.addLayout(self.btn_layout)
        
        # Tableau d'affichage des logs
        self.tableHistorique = QTreeWidget()
        self.tableHistorique.setHeaderLabels(["ID", "Date", "Utilisateur", "Action", "Détails"])
        self.tableHistorique.header().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tableHistorique.header().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.tableHistorique)
        
        # Connexions
        self.btn_rafraichir.clicked.connect(self.load_history)
        self.btn_vider.clicked.connect(self.vider_historique)
        
        self.load_history()

    def load_history(self):
        """Charge les logs depuis la base de données"""
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM HISTORIQUE ORDER BY date_action DESC")
            
            self.tableHistorique.clear()
            for row in cursor.fetchall():
                item = QTreeWidgetItem(self.tableHistorique)
                item.setText(0, str(row[0]))
                item.setText(1, str(row[1]))
                item.setText(2, str(row[2]))
                item.setText(3, str(row[3]))
                item.setText(4, str(row[4]))
                
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def vider_historique(self):
        """Supprime tout le contenu de la table HISTORIQUE"""
        if QMessageBox.question(self, 'Confirmation', "Voulez-vous vraiment vider tout l'historique ? Cette action est irréversible.") == QMessageBox.StandardButton.Yes:
            try:
                conn = self.db_connect()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM HISTORIQUE")
                conn.commit()
                QMessageBox.information(self, "Succès", "L'historique a été entièrement vidé.")
                self.load_history()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de vider l'historique : {e}")
            finally:
                if 'conn' in locals() and conn: conn.close()

    # =========================================================================
    # MÉTHODE STATIQUE (Le cœur du système, appelée par tous les autres fichiers)
    # =========================================================================
    @staticmethod
    def ajouter_log(db_connect_func, utilisateur, action, details):
        """
        Méthode statique permettant d'ajouter une ligne dans l'historique 
        depuis n'importe quel autre module (Client, Véhicule, Location, etc.)
        sans avoir besoin d'instancier la classe GestionHistorique.
        """
        try:
            conn = db_connect_func()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO HISTORIQUE (utilisateur, action, details) VALUES (?, ?, ?)", 
                (utilisateur, action, details)
            )
            conn.commit()
        except sqlite3.Error as e:
            # On print l'erreur dans la console au lieu de bloquer l'utilisateur avec une popup
            print(f"Erreur silencieuse d'historisation : {e}")
        finally:
            if 'conn' in locals() and conn: conn.close()