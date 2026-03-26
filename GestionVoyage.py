# -*- coding: utf-8 -*-
import sqlite3
from PyQt6.QtCore import pyqtSignal, Qt, QDateTime
from PyQt6.QtWidgets import QWidget, QMessageBox, QTreeWidgetItem
from PyQt6.uic import loadUi
from datetime import datetime, timedelta

from utils import resource_path
from GestionHistorique import GestionHistorique

class GestionVoyage(QWidget):
    voyage_termine = pyqtSignal()
    
    def __init__(self, db_connect_func):
        super().__init__()
        loadUi(resource_path("GestionVoyage.ui"), self)
        
        self.db_connect = db_connect_func 

        # 🎯 ACTIVATION DU CALENDRIER (DATEPICKER)
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDateTime(QDateTime.currentDateTime())

        self.btn_planifier.clicked.connect(self.planifier_voyage)
        self.btn_terminer.clicked.connect(self.terminer_voyage)
        self.btn_facturer.clicked.connect(self.generer_facture)
        self.tableVoyages.itemSelectionChanged.connect(self.charger_champs_voyage)
        
        self.charger_comboboxes()
        self.load_voyages()

    def charger_comboboxes(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()

            cursor.execute("SELECT id_client, nom || ' ' || prenom FROM CLIENT ORDER BY nom, prenom")
            clients = cursor.fetchall()
            self.combo_client.clear()
            self.combo_client.addItem("Sélectionner un client...", -1) 
            for id_client, nom_complet in clients: self.combo_client.addItem(nom_complet, id_client) 

            cursor.execute("SELECT id_chauffeur, nom || ' ' || prenom FROM CHAUFFEUR ORDER BY nom, prenom")
            chauffeurs = cursor.fetchall()
            self.combo_chauffeur.clear()
            self.combo_chauffeur.addItem("Sélectionner un chauffeur...", -1)
            for id_chauffeur, nom_complet in chauffeurs: self.combo_chauffeur.addItem(nom_complet, id_chauffeur)

            cursor.execute("SELECT immatriculation FROM VEHICULE WHERE statut_disponibilite = 'Disponible'") 
            vehicules = [row[0] for row in cursor.fetchall()]
            self.combo_vehicule.clear()
            self.combo_vehicule.addItem("Sélectionner un véhicule disponible...") 
            self.combo_vehicule.addItems(vehicules)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur DB", f"Erreur: {e}")
        finally:
            if 'conn' in locals() and conn: conn.close()

    def load_voyages(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    V.id_voyage, C.nom, Ch.nom, Ve.immatriculation, V.statut_voyage, 
                    V.lieu_depart, V.lieu_arrivee, V.date_debut_planifiee, V.distance_estimee, V.date_fin_reelle
                FROM VOYAGE V
                JOIN CLIENT C ON V.id_client = C.id_client
                JOIN CHAUFFEUR Ch ON V.id_chauffeur = Ch.id_chauffeur
                JOIN VEHICULE Ve ON V.immatriculation = Ve.immatriculation
                ORDER BY V.id_voyage DESC
            """)
            voyages = cursor.fetchall()
            self.tableVoyages.clear()
            self.tableVoyages.setHeaderLabels([
                "ID Voyage", "Client", "Chauffeur", "Immatriculation", "Statut", 
                "Départ", "Arrivée", "Date Début", "Distance Estimée (km)", "Date Fin Réelle"
            ])
            for row_data in voyages:
                item = QTreeWidgetItem(self.tableVoyages)
                for col_num, data in enumerate(row_data): item.setText(col_num, str(data if data is not None else ''))
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def charger_champs_voyage(self):
        selected_item = self.tableVoyages.currentItem() 
        if selected_item:
            try:
                self.combo_client.setCurrentText(selected_item.text(1))
                self.combo_chauffeur.setCurrentText(selected_item.text(2))
            except:
                pass 

    def planifier_voyage(self):
        id_client = self.combo_client.currentData()
        id_chauffeur = self.combo_chauffeur.currentData()
        immatriculation = self.combo_vehicule.currentText()
        depart = self.input_depart.text().strip()
        arrivee = self.input_arrivee.text().strip()
        date_debut = self.date_debut.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        distance_input = self.input_distance_estimee.text().strip()
        
        try:
            distance_estimee = float(distance_input) if distance_input else 0.0
            if distance_estimee < 0: return QMessageBox.warning(self, "Erreur", "Distance négative.")
        except ValueError:
            return QMessageBox.warning(self, "Erreur", "Distance invalide.")
        
        if id_client == -1 or id_chauffeur == -1 or immatriculation == "Sélectionner un véhicule disponible...":
            return QMessageBox.warning(self, "Erreur", "Sélections invalides.")

        try:
            conn = self.db_connect()
            cursor = conn.cursor()

            # ==========================================
            # 🛡️ LE BOUCLIER ANTI-CHEVAUCHEMENT GLOBAL
            # ==========================================
            
            # 1. Test contre une LOCATION existante
            cursor.execute("""
                SELECT date_sortie, COALESCE(date_retour_prevue, '2099-12-31') 
                FROM LOCATION 
                WHERE immatriculation = ? 
                AND statut_location IN ('Planifiée', 'En location', 'En cours')
                AND date_sortie <= datetime(?, '+12 hours') 
                AND COALESCE(date_retour_reelle, date_retour_prevue, '2099-12-31') >= ?
            """, (immatriculation, date_debut, date_debut))
            chev_loc = cursor.fetchone()
            if chev_loc:
                return QMessageBox.warning(self, "Bouclier Activé 🛡️", f"Impossible : ce véhicule est déjà prévu pour une LOCATION du {chev_loc[0]} au {chev_loc[1]}.")

            # 2. Test contre une RÉPARATION existante
            cursor.execute("""
                SELECT date_debut_reparation, COALESCE(date_fin_reparation, 'Non définie') 
                FROM REPARATION 
                WHERE immatriculation = ? 
                AND statut_reparation = 'En cours'
                AND date_debut_reparation <= datetime(?, '+12 hours')
                AND COALESCE(date_fin_reparation, '2099-12-31') >= ?
            """, (immatriculation, date_debut, date_debut))
            chev_rep = cursor.fetchone()
            if chev_rep:
                return QMessageBox.warning(self, "Bouclier Activé 🛡️", f"Impossible : ce véhicule sera en RÉPARATION à partir du {chev_rep[0]}.")

            # 3. Test contre un VOYAGE existant
            cursor.execute("""
                SELECT date_debut_planifiee 
                FROM VOYAGE 
                WHERE immatriculation = ? 
                AND statut_voyage IN ('Planifié', 'En cours')
                AND date_debut_planifiee >= datetime(?, '-12 hours')
                AND date_debut_planifiee <= datetime(?, '+12 hours')
            """, (immatriculation, date_debut, date_debut))
            chev_voy = cursor.fetchone()
            if chev_voy:
                return QMessageBox.warning(self, "Bouclier Activé 🛡️", f"Impossible : un autre VOYAGE est déjà prévu le {chev_voy[0]}.")
            # ==========================================

            cursor.execute("""
                INSERT INTO VOYAGE (id_client, immatriculation, id_chauffeur, statut_voyage, 
                                    lieu_depart, lieu_arrivee, date_debut_planifiee, distance_estimee)
                VALUES (?, ?, ?, 'Planifié', ?, ?, ?, ?)
            """, (id_client, immatriculation, id_chauffeur, depart, arrivee, date_debut, distance_estimee))
            
            cursor.execute("UPDATE VEHICULE SET statut_disponibilite = 'En course' WHERE immatriculation = ?", (immatriculation,))
            conn.commit()
            
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Planification Voyage", f"De {depart} vers {arrivee} (Client ID: {id_client}, Véhicule: {immatriculation})")
            
            QMessageBox.information(self, "Succès", "Voyage planifié avec succès.")
            self.load_voyages()
            self.charger_comboboxes() 
            self.input_depart.clear(); self.input_arrivee.clear(); self.input_distance_estimee.clear()
            self.combo_client.setCurrentIndex(0); self.combo_chauffeur.setCurrentIndex(0); self.combo_vehicule.setCurrentIndex(0)
            
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def terminer_voyage(self):
        selected_item = self.tableVoyages.currentItem()
        if not selected_item: return QMessageBox.warning(self, "Erreur", "Sélectionnez un voyage à terminer.")

        id_voyage = selected_item.text(0)
        statut_actuel = selected_item.text(4)
        immatriculation = selected_item.text(3)
        
        if statut_actuel != 'Planifié': return QMessageBox.warning(self, "Statut", "Seuls les voyages planifiés peuvent être terminés.")

        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            date_fin = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("UPDATE VOYAGE SET statut_voyage = 'Terminé', date_fin_reelle = ? WHERE id_voyage = ?", (date_fin, id_voyage))
            cursor.execute("UPDATE VEHICULE SET statut_disponibilite = 'Disponible' WHERE immatriculation = ?", (immatriculation,))
            conn.commit()
            
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Clôture Voyage", f"Voyage ID {id_voyage} terminé.")
            
            QMessageBox.information(self, "Succès", f"Voyage ID {id_voyage} terminé.")
            self.load_voyages()
            self.charger_comboboxes()
            self.voyage_termine.emit()
            
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def generer_facture(self):
        selected_item = self.tableVoyages.currentItem()
        if not selected_item: return QMessageBox.warning(self, "Erreur", "Sélectionnez un voyage.")

        id_voyage = selected_item.text(0)
        statut_actuel = selected_item.text(4)
        distance_estimee_str = selected_item.text(8) 
        
        if statut_actuel != 'Terminé': return QMessageBox.warning(self, "Statut", "Voyage non terminé.")

        try:
            distance_estimee = float(distance_estimee_str) if distance_estimee_str else 0.0
            TARIF_KM_HT = 2.50
            TAUX_TVA = 0.20

            montant_ht = round(distance_estimee * TARIF_KM_HT, 2)
            montant_tva = round(montant_ht * TAUX_TVA, 2)
            date_emission_dt = datetime.now()
            date_echeance_dt = date_emission_dt + timedelta(days=30)
            
            date_emission = date_emission_dt.strftime('%Y-%m-%d %H:%M:%S')
            date_echeance = date_echeance_dt.strftime('%Y-%m-%d %H:%M:%S')
            statut_paiement = 'En attente'

            conn = self.db_connect()
            cursor = conn.cursor()

            cursor.execute("SELECT id_facture FROM FACTURE_CLIENT WHERE id_voyage = ?", (id_voyage,))
            if cursor.fetchone(): return QMessageBox.information(self, "Information", f"Déjà facturé.")

            cursor.execute("""
                INSERT INTO FACTURE_CLIENT (id_voyage, date_emission, date_echeance, montant_HT, montant_TVA, statut_paiement) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_voyage, date_emission, date_echeance, montant_ht, montant_tva, statut_paiement))
            
            cursor.execute("UPDATE VOYAGE SET statut_voyage = 'Facturé' WHERE id_voyage = ?", (id_voyage,))
            conn.commit()
            
            GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Facturation", f"Facture émise pour le voyage {id_voyage} ({montant_ht}€ HT)")
            
            QMessageBox.information(self, "Succès", f"Facture générée. Montant HT: {montant_ht}€.")
            self.load_voyages()
            
        except ValueError:
            QMessageBox.critical(self, "Erreur", "Distance invalide.")
        except sqlite3.Error as e:
            print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()