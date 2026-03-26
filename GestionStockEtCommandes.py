import sqlite3
from PyQt6.QtWidgets import (QWidget, QMessageBox, QTableWidgetItem, QDialog, 
                             QVBoxLayout, QFormLayout, QComboBox, QSpinBox, QDialogButtonBox)
from PyQt6.uic import loadUi
from PyQt6.QtCore import QDate

from utils import resource_path
from GestionHistorique import GestionHistorique # 🎯 IMPORT HISTORIQUE

# =========================================================================
# 🛠️ NOUVELLE CLASSE : BOÎTE DE DIALOGUE POUR LA SÉLECTION DES PIÈCES
# =========================================================================
class DialogSelectionPiece(QDialog):
    def __init__(self, db_connect_func, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter une pièce à la commande")
        self.setMinimumWidth(350)
        self.db_connect = db_connect_func

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        # Menu déroulant pour les pièces
        self.combo_piece = QComboBox()
        # Sélecteur numérique pour la quantité
        self.spin_quantite = QSpinBox()
        self.spin_quantite.setMinimum(1)
        self.spin_quantite.setMaximum(1000)
        self.spin_quantite.setValue(1)

        self.form_layout.addRow("Sélectionner la pièce :", self.combo_piece)
        self.form_layout.addRow("Quantité à commander :", self.spin_quantite)
        self.layout.addLayout(self.form_layout)

        # Boutons OK et Annuler
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.charger_pieces()

    def charger_pieces(self):
        """Charge toutes les pièces disponibles dans la base de données"""
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id_piece, nom_piece, reference_fournisseur, prix_unitaire FROM PIECE")
            for id_p, nom, ref, prix in cursor.fetchall():
                texte_affichage = f"{nom} (Réf: {ref}) - {prix}€ HT"
                # On stocke l'id_piece dans les "Data" du combobox
                self.combo_piece.addItem(texte_affichage, id_p)
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def get_data(self):
        """Retourne l'ID de la pièce et la quantité choisie"""
        return self.combo_piece.currentData(), self.spin_quantite.value()

# =========================================================================
# 📦 CLASSE PRINCIPALE : GESTION DU STOCK ET DES COMMANDES
# =========================================================================
class GestionStockEtCommandes(QWidget):
    def __init__(self, db_connect_func):
        super().__init__()
        loadUi(resource_path("GestionStockEtCommandes.ui"), self)
        self.db_connect = db_connect_func 

        self.btn_ajouter_piece.clicked.connect(self.ajouter_piece)
        self.btn_passer_commande.clicked.connect(self.passer_commande_reparation)
        self.btn_recevoir_commande.clicked.connect(self.recevoir_commande)
        
        self.charger_pieces()
        self.charger_fournisseurs(self.combo_fournisseur_commande)
        self.charger_commandes()
        
    def charger_fournisseurs(self, combobox):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id_fournisseur, nom_fournisseur FROM FOURNISSEUR")
            combobox.clear()
            for id_f, nom in cursor.fetchall(): combobox.addItem(f"{id_f} - {nom}")
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def charger_pieces(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id_piece, nom_piece, reference_fournisseur, prix_unitaire, quantite_stock FROM PIECE")
            pieces = cursor.fetchall()
            self.table_pieces.setRowCount(len(pieces))
            for row_num, row_data in enumerate(pieces):
                for col_num, data in enumerate(row_data):
                    self.table_pieces.setItem(row_num, col_num, QTableWidgetItem(str(data)))
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def ajouter_piece(self):
        nom, ref = self.input_nom_piece.text().strip(), self.input_ref_piece.text().strip()
        prix_unitaire = self.input_prix_unitaire.text().strip().replace(',', '.')
        quantite = self.input_quantite_stock.text().strip()
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO PIECE (nom_piece, reference_fournisseur, prix_unitaire, quantite_stock) VALUES (?, ?, ?, ?)", (nom, ref, float(prix_unitaire), int(quantite)))
            conn.commit()
            
            # 🎯 LOG HISTORIQUE
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Ajout Pièce", f"Pièce ajoutée: {nom} (Réf: {ref})")
            
            QMessageBox.information(self, "Succès", f"Pièce ajoutée.")
            self.input_nom_piece.clear()
            self.input_ref_piece.clear()
            self.input_prix_unitaire.clear()
            self.input_quantite_stock.clear()
        except sqlite3.IntegrityError: 
            return QMessageBox.critical(self, "Erreur", "Référence déjà utilisée.")
        except ValueError: 
            return QMessageBox.warning(self, "Erreur", "Vérifiez les valeurs numériques saisies.")
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.charger_pieces()

    def charger_commandes(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT C.id_commande, F.nom_fournisseur, C.date_commande, C.montant_estime, C.statut_commande FROM COMMANDE_REPARATION C JOIN FOURNISSEUR F ON C.id_fournisseur = F.id_fournisseur ORDER BY C.date_commande DESC")
            commandes = cursor.fetchall()
            self.table_commandes.setRowCount(len(commandes))
            for row_num, row_data in enumerate(commandes):
                for col_num, data in enumerate(row_data):
                    self.table_commandes.setItem(row_num, col_num, QTableWidgetItem(str(data)))
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def passer_commande_reparation(self):
        fournisseur_str = self.combo_fournisseur_commande.currentText()
        if not fournisseur_str: 
            return QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un fournisseur.")
            
        id_fournisseur = int(fournisseur_str.split(" - ")[0])
        montant_str = self.input_montant_commande.text().strip().replace(',', '.')
        montant = float(montant_str) if montant_str else 0.0

        # 1. Ouvrir la boîte de dialogue pour choisir la pièce
        dialog = DialogSelectionPiece(self.db_connect, self)
        
        # Si l'utilisateur clique sur "OK"
        if dialog.exec() == QDialog.DialogCode.Accepted:
            id_piece, quantite = dialog.get_data()
            
            if not id_piece:
                return QMessageBox.warning(self, "Erreur", "Aucune pièce n'a pu être sélectionnée.")

            try:
                conn = self.db_connect()
                cursor = conn.cursor()
                
                # 2. Créer l'entête de la commande
                cursor.execute(
                    "INSERT INTO COMMANDE_REPARATION (date_commande, montant_estime, id_fournisseur, statut_commande) VALUES (?, ?, ?, 'En cours')", 
                    (QDate.currentDate().toString("yyyy-MM-dd"), montant, id_fournisseur)
                )
                id_commande = cursor.lastrowid
                
                # 3. Lier la pièce choisie à cette commande dans la table UTILISER
                cursor.execute(
                    "INSERT INTO UTILISER (id_commande, id_piece, quantite_utilisee) VALUES (?, ?, ?)", 
                    (id_commande, id_piece, quantite)
                )

                conn.commit()
                
                # 🎯 LOG HISTORIQUE
                GestionHistorique.ajouter_log(
                    self.db_connect, 
                    "Utilisateur", 
                    "Nouvelle Commande", 
                    f"Commande n°{id_commande} passée : {quantite}x Pièce ID {id_piece} (Montant est.: {montant}€)"
                )
                
                QMessageBox.information(self, "Succès", "La commande a été enregistrée avec succès !")
                self.input_montant_commande.clear()
                
            except Exception as e: 
                print(e)
                QMessageBox.critical(self, "Erreur BDD", f"Une erreur est survenue lors de l'enregistrement : {e}")
            finally:
                if 'conn' in locals() and conn: conn.close()
                
            # Rafraîchir le tableau des commandes
            self.charger_commandes()

    def recevoir_commande(self):
        selected_items = self.table_commandes.selectedItems()
        if not selected_items: return
        id_commande = int(self.table_commandes.item(selected_items[0].row(), 0).text())
        if self.table_commandes.item(selected_items[0].row(), 4).text() == 'Livrée': return
        
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id_piece, quantite_utilisee FROM UTILISER WHERE id_commande = ?", (id_commande,))
            for id_piece, quantite in cursor.fetchall():
                cursor.execute("UPDATE PIECE SET quantite_stock = quantite_stock + ? WHERE id_piece = ?", (quantite, id_piece))
            cursor.execute("UPDATE COMMANDE_REPARATION SET statut_commande = 'Livrée' WHERE id_commande = ?", (id_commande,))
            conn.commit()
            
            # 🎯 LOG HISTORIQUE
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Réception Commande", f"Commande ID {id_commande} réceptionnée. Stock mis à jour.")
            
            QMessageBox.information(self, "Succès", "Commande reçue, stock mis à jour !")
        except sqlite3.Error as e: 
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
            
        self.charger_commandes()
        self.charger_pieces()