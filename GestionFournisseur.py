# -*- coding: utf-8 -*-
import sqlite3
from PyQt6.QtWidgets import QWidget, QMessageBox, QTreeWidgetItem
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSignal, Qt

from utils import resource_path
from GestionHistorique import GestionHistorique 

class GestionFournisseur(QWidget):
    # Ce signal permettra de prévenir l'onglet "Stock" qu'un fournisseur a été ajouté
    fournisseur_modifie = pyqtSignal()
    
    def __init__(self, db_connect_func):
        super().__init__()
        loadUi(resource_path("GestionFournisseur.ui"), self)
        self.db_connect = db_connect_func
        
        self.btn_nouveau.clicked.connect(self.nouveau_enregistrement)
        self.btn_ajouter.clicked.connect(self.ajouter_fournisseur)
        self.btn_modifier.clicked.connect(self.modifier_fournisseur)
        self.btn_supprimer.clicked.connect(self.supprimer_fournisseur)
        self.tableFournisseurs.itemSelectionChanged.connect(self.charger_champs)
        
        self.load_fournisseurs()

    def nouveau_enregistrement(self):
        self.tableFournisseurs.clearSelection()
        self.input_nom.clear()
        self.input_contact.clear()
        self.input_tel.clear()
        self.input_specialite.clear()
        self.input_nom.setFocus()

    def load_fournisseurs(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id_fournisseur, nom_fournisseur, contact, telephone, specialite FROM FOURNISSEUR ORDER BY nom_fournisseur")
            self.tableFournisseurs.clear()
            for row in cursor.fetchall():
                item = QTreeWidgetItem(self.tableFournisseurs)
                item.setText(0, str(row[0]))
                item.setData(0, Qt.ItemDataRole.UserRole, row[0])
                item.setText(1, row[1])
                item.setText(2, row[2] if row[2] else "")
                item.setText(3, row[3] if row[3] else "")
                item.setText(4, row[4] if row[4] else "")
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def charger_champs(self):
        selected = self.tableFournisseurs.currentItem()
        if not selected: return
        self.input_nom.setText(selected.text(1))
        self.input_contact.setText(selected.text(2))
        self.input_tel.setText(selected.text(3))
        self.input_specialite.setText(selected.text(4))

    def ajouter_fournisseur(self):
        nom = self.input_nom.text().strip()
        contact = self.input_contact.text().strip()
        tel = self.input_tel.text().strip()
        specialite = self.input_specialite.text().strip()

        if not nom:
            return QMessageBox.warning(self, "Erreur", "Le nom de l'entreprise est obligatoire.")

        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO FOURNISSEUR (nom_fournisseur, contact, telephone, specialite) VALUES (?, ?, ?, ?)", (nom, contact, tel, specialite))
            conn.commit()
            
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Ajout Fournisseur", f"Fournisseur {nom} ajouté")
            QMessageBox.information(self, "Succès", "Fournisseur ajouté avec succès.")
            self.nouveau_enregistrement()
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Erreur", "Un fournisseur avec ce nom existe déjà.")
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.load_fournisseurs()
        self.fournisseur_modifie.emit()

    def modifier_fournisseur(self):
        selected = self.tableFournisseurs.currentItem()
        if not selected: return QMessageBox.warning(self, "Erreur", "Sélectionnez un fournisseur à modifier.")
        
        id_fournisseur = selected.data(0, Qt.ItemDataRole.UserRole)
        nom = self.input_nom.text().strip()
        contact = self.input_contact.text().strip()
        tel = self.input_tel.text().strip()
        specialite = self.input_specialite.text().strip()

        if not nom: return QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")

        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE FOURNISSEUR SET nom_fournisseur=?, contact=?, telephone=?, specialite=? WHERE id_fournisseur=?", (nom, contact, tel, specialite, id_fournisseur))
            conn.commit()
            
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Modif. Fournisseur", f"Fournisseur {nom} modifié")
            QMessageBox.information(self, "Succès", "Fournisseur modifié avec succès.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Erreur", "Ce nom de fournisseur existe déjà.")
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.load_fournisseurs()
        self.fournisseur_modifie.emit()

    def supprimer_fournisseur(self):
        selected = self.tableFournisseurs.currentItem()
        if not selected: return QMessageBox.warning(self, "Erreur", "Sélectionnez un fournisseur à supprimer.")
        
        id_fournisseur = selected.data(0, Qt.ItemDataRole.UserRole)
        nom = selected.text(1)

        if QMessageBox.question(self, 'Confirmation', f"Supprimer le fournisseur {nom} ?") == QMessageBox.StandardButton.Yes:
            try:
                conn = self.db_connect()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM FOURNISSEUR WHERE id_fournisseur=?", (id_fournisseur,))
                conn.commit()
                GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Suppression Fournisseur", f"Fournisseur {nom} supprimé")
            except sqlite3.IntegrityError:
                return QMessageBox.critical(self, "Interdit", "Impossible de supprimer ce fournisseur car il est lié à des commandes de pièces existantes.")
            except sqlite3.Error as e:
                print(e)
            finally:
                if 'conn' in locals() and conn: conn.close()
                
            self.load_fournisseurs()
            self.nouveau_enregistrement()
            self.fournisseur_modifie.emit()