import sqlite3
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox, QFileDialog, QLabel

# 🎯 IMPORT HISTORIQUE
from GestionHistorique import GestionHistorique 

class GestionImportExport(QWidget):
    def __init__(self, db_connect_func):
        super().__init__()
        self.db_connect = db_connect_func
        
        self.layout = QVBoxLayout(self)
        
        self.label = QLabel("<h2>Sauvegarde et Restauration (JSON)</h2><p>L'exportation crée une copie complète de la base de données au format JSON.<br>L'importation remplace/met à jour les données actuelles avec celles du fichier JSON.</p>")
        self.layout.addWidget(self.label)
        
        self.btn_export = QPushButton("📤 Exporter la base en fichier JSON (Sauvegarde)")
        self.btn_export.setMinimumHeight(60)
        self.btn_export.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 14px; border-radius: 5px;")
        
        self.btn_import = QPushButton("📥 Importer depuis un fichier JSON (Restauration)")
        self.btn_import.setMinimumHeight(60)
        self.btn_import.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; font-size: 14px; border-radius: 5px;")
        
        self.layout.addWidget(self.btn_export)
        self.layout.addWidget(self.btn_import)
        self.layout.addStretch() 
        
        self.btn_export.clicked.connect(self.exporter_json)
        self.btn_import.clicked.connect(self.importer_json)

    def exporter_json(self):
        chemin_fichier, _ = QFileDialog.getSaveFileName(self, "Sauvegarder la base de données", "sauvegarde_agence.json", "Fichiers JSON (*.json)")
        if not chemin_fichier: return 

        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]
            
            db_data = {}
            for table in tables:
                cursor.execute(f"SELECT * FROM {table}")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                db_data[table] = [dict(zip(columns, row)) for row in rows]
                
            with open(chemin_fichier, 'w', encoding='utf-8') as f:
                json.dump(db_data, f, indent=4, ensure_ascii=False)
                
            # 🎯 LOG HISTORIQUE
            GestionHistorique.ajouter_log(
                self.db_connect, 
                "Administrateur", 
                "Export JSON", 
                f"Sauvegarde complète de la base réussie ({len(tables)} tables exportées)."
            )
                
            QMessageBox.information(self, "Succès", f"Base de données exportée avec succès !\n{len(tables)} tables sauvegardées.")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'exportation : {e}")
        finally:
            if 'conn' in locals() and conn: conn.close()

    def importer_json(self):
        rep = QMessageBox.warning(self, "Attention Critique", "L'importation modifiera la base actuelle.\nIl est recommandé de faire un export avant de continuer. Poursuivre ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if rep == QMessageBox.StandardButton.No: return
        
        chemin_fichier, _ = QFileDialog.getOpenFileName(self, "Ouvrir une sauvegarde", "", "Fichiers JSON (*.json)")
        if not chemin_fichier: return

        try:
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
                
            conn = self.db_connect()
            cursor = conn.cursor()
            
            # Désactivation des contraintes de clés étrangères temporairement pour éviter les blocages d'importation
            cursor.execute('PRAGMA foreign_keys = OFF;') 
            
            for table, lignes in db_data.items():
                if not lignes: continue
                colonnes = ", ".join(lignes[0].keys())
                placeholders = ", ".join(["?"] * len(lignes[0]))
                requete = f"INSERT OR REPLACE INTO {table} ({colonnes}) VALUES ({placeholders})"
                
                for ligne in lignes:
                    cursor.execute(requete, tuple(ligne.values()))
                    
            cursor.execute('PRAGMA foreign_keys = ON;') 
            conn.commit()
            
            # 🎯 LOG HISTORIQUE
            GestionHistorique.ajouter_log(
                self.db_connect, 
                "Administrateur", 
                "Import JSON", 
                "Restauration de la base de données effectuée avec succès depuis un fichier."
            )
            
            QMessageBox.information(self, "Succès", "Restauration terminée ! Veuillez redémarrer l'application pour voir les changements complets.")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'importation (fichier potentiellement corrompu) : {e}")
        finally:
            if 'conn' in locals() and conn: conn.close()