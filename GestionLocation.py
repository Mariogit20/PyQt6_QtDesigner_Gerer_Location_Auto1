# -*- coding: utf-8 -*-
import sqlite3
import os 
import sys
import re  
import urllib.parse 
import socket  
from PyQt6.QtCore import pyqtSignal, Qt, QDateTime, QTimer  
from PyQt6.QtWidgets import (QWidget, QMessageBox, QTreeWidgetItem, QDialog, 
                             QVBoxLayout, QLabel, QDateTimeEdit, QPushButton, QFileDialog, QLineEdit)
from PyQt6.uic import loadUi
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from utils import resource_path
from GestionHistorique import GestionHistorique 

class GestionLocation(QWidget):
    location_terminee = pyqtSignal()
    
    def __init__(self, db_connect_func):
        super().__init__()
        loadUi(resource_path("GestionLocation.ui"), self) 
        self.db_connect = db_connect_func 
        
        self.btn_reserver = QPushButton("📅 Nouvelle Réservation (Envoie Email)")
        self.btn_reserver.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 8px; border-radius: 4px; margin-bottom: 5px;")
        self.btn_reserver.clicked.connect(self.ouvrir_dialogue_reservation)
        self.layout().insertWidget(0, self.btn_reserver)
        
        self.btn_valider_conf = QPushButton("✅ Valider Confirmation Manuelle")
        self.btn_valider_conf.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px; border-radius: 4px; margin-bottom: 5px;")
        self.btn_valider_conf.clicked.connect(self.valider_confirmation_manuelle)
        self.layout().insertWidget(1, self.btn_valider_conf)

        self.btn_renvoyer_mail = QPushButton("🔄 Renvoyer Email de Demande")
        self.btn_renvoyer_mail.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold; padding: 8px; border-radius: 4px; margin-bottom: 10px;")
        self.btn_renvoyer_mail.clicked.connect(self.renvoyer_email_manuel)
        self.layout().insertWidget(2, self.btn_renvoyer_mail)

        self.btn_imprimer_contrat = QPushButton("📄 Imprimer Contrat (PDF)")
        self.btn_imprimer_contrat.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold; padding: 8px; border-radius: 4px; margin-bottom: 10px;")
        self.btn_imprimer_contrat.clicked.connect(self.imprimer_contrat)
        self.layout().insertWidget(3, self.btn_imprimer_contrat)
        
        self.btn_planifier.clicked.connect(self.enregistrer_sortie)
        self.btn_terminer.clicked.connect(self.enregistrer_retour)
        self.charger_comboboxes()
        
        self.tableVoyages.setColumnCount(10)
        self.load_locations()
        
        self.timer_init = QTimer(self)
        self.timer_init.setSingleShot(True)
        self.timer_init.timeout.connect(self.processus_auto_renvoi_emails)
        self.timer_init.start(8000) 
        
        self.timer_sync_auto = QTimer(self)
        self.timer_sync_auto.timeout.connect(self.processus_auto_renvoi_emails)
        self.timer_sync_auto.start(300000) 

    def verifier_connexion_internet(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5) 
            return True
        except OSError:
            return False

    def processus_auto_renvoi_emails(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            # 🎯 AJOUT: Récupération de téléphone et adresse pour le mode hors-ligne
            cursor.execute("""
                SELECT L.id_location, L.date_sortie, COALESCE(L.date_retour_prevue, 'Non définie'), 
                       C.nom, C.prenom, C.email, C.telephone, C.adresse,
                       V.immatriculation, V.marque, V.modele,
                       CH.nom, CH.prenom, L.lieu_arrivee
                FROM LOCATION L JOIN CLIENT C ON L.id_client = C.id_client 
                JOIN VEHICULE V ON L.immatriculation = V.immatriculation 
                LEFT JOIN CHAUFFEUR CH ON L.id_chauffeur = CH.id_chauffeur
                WHERE L.statut_location = 'En attente' AND (L.date_envoi_confirmation IS NULL OR L.date_envoi_confirmation = '')
            """)
            emails_bloques = cursor.fetchall()
            
            if not emails_bloques or not self.verifier_connexion_internet():
                return 

            emails_envoyes_avec_succes = 0
            for data in emails_bloques:
                id_loc, d_s, d_r, c_nom, c_prenom, email_dest, c_tel, c_adresse, immat, marque, modele, ch_nom, ch_prenom, lieu_arr = data
                if not email_dest: continue
                    
                nom_complet = f"{c_nom} {c_prenom}"
                chauffeur_nom_complet = f"{ch_nom} {ch_prenom}" if ch_nom else ""
                tel_str = c_tel if c_tel else "Non renseigné"
                adr_str = c_adresse if c_adresse else "Non renseignée"
                
                succes, msg = self.envoyer_email_confirmation(email_dest, nom_complet, tel_str, adr_str, immat, marque, modele, chauffeur_nom_complet, d_s, d_r, id_loc, lieu_arr)
                if succes:
                    cursor.execute("UPDATE LOCATION SET date_envoi_confirmation = ? WHERE id_location = ?", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id_loc))
                    conn.commit()
                    emails_envoyes_avec_succes += 1
                    
            if emails_envoyes_avec_succes > 0:
                self.load_locations()
                QMessageBox.information(self, "Synchronisation 🌐", f"Le logiciel a détecté Internet et a envoyé {emails_envoyes_avec_succes} email(s) en attente.")
        except sqlite3.Error: pass
        finally:
            if 'conn' in locals() and conn: conn.close()

    def charger_comboboxes(self):
        try:
            conn = self.db_connect(); cursor = conn.cursor()
            cursor.execute("SELECT id_client, nom || ' ' || prenom FROM CLIENT"); self.combo_client.clear()
            for id_c, nom in cursor.fetchall(): self.combo_client.addItem(nom, id_c)
            cursor.execute("SELECT id_chauffeur, nom || ' ' || prenom FROM CHAUFFEUR"); self.combo_chauffeur.clear(); self.combo_chauffeur.addItem("👤 SANS CHAUFFEUR", None)
            for id_ch, nom_complet in cursor.fetchall(): self.combo_chauffeur.addItem(nom_complet, id_ch)
            cursor.execute("SELECT immatriculation, marque, modele FROM VEHICULE WHERE statut_disponibilite = 'Disponible'"); self.combo_vehicule.clear(); self.combo_vehicule.addItem("🚗 Sélectionner...", None) 
            for immat, marque, modele in cursor.fetchall(): self.combo_vehicule.addItem(f"{immat} - {marque} {modele}", immat) 
        except sqlite3.Error as e: print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    def load_locations(self):
        try:
            conn = self.db_connect(); cursor = conn.cursor()
            cursor.execute("SELECT L.id_location, C.nom, Ve.immatriculation, Ve.marque || ' ' || Ve.modele, L.statut_location, L.date_sortie, COALESCE(L.date_retour_reelle, L.date_retour_prevue), L.confirmation_client, L.date_envoi_confirmation, L.lieu_arrivee FROM LOCATION L JOIN CLIENT C ON L.id_client = C.id_client JOIN VEHICULE Ve ON L.immatriculation = Ve.immatriculation ORDER BY L.id_location DESC")
            self.tableVoyages.clear()
            
            self.tableVoyages.setHeaderLabels(["ID", "Client", "Immat.", "Véhicule", "Statut", "Sortie", "Retour", "Confirmé ?", "Date Envoi Email", "Destination"])
            
            for row in cursor.fetchall():
                item = QTreeWidgetItem(self.tableVoyages)
                for i in range(7): item.setText(i, str(row[i]))
                item.setText(7, "✅ Oui" if row[7] else "❌ Non")
                item.setText(8, str(row[8]) if row[8] else "Hors Ligne")
                item.setText(9, str(row[9]) if row[9] else "Non renseigné") 
                item.setData(0, Qt.ItemDataRole.UserRole, row[0])
        except sqlite3.Error as e: print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()

    # 🎯 AJOUT: Paramètres c_tel et c_adresse ajoutés à la fonction
    def envoyer_email_confirmation(self, email_destinataire, nom_client, c_tel, c_adresse, immat, marque, modele, chauffeur_nom, d_debut, d_fin, id_loc, lieu_arrivee):
        from VerificateurEmail import verifier_email_complet
        est_valide, message_erreur = verifier_email_complet(email_destinataire)
        if not est_valide: return False, message_erreur

        email_agence = "progsuividpe@gmail.com"; mot_de_passe_app = "mmtbbxsrnzzbreaj"    		
        sujet_agence = f"ACTION REQUISE : Confirmation Réservation N°{id_loc}"
        chauffeur_texte = f"Oui ({chauffeur_nom})" if chauffeur_nom else "Non (Sans chauffeur)"
        lieu_texte = lieu_arrivee if lieu_arrivee else "Non spécifié"
        
        sujet_reponse = f"CONFIRMATION RESERVATION N°{id_loc} - {nom_client}"
        corps_reponse = f"Bonjour,\n\nJe confirme officiellement ma réservation N°{id_loc}.\nMerci de la valider dans votre logiciel.\nCordialement,"
        lien_mailto = f"mailto:{email_agence}?subject={urllib.parse.quote(sujet_reponse)}&body={urllib.parse.quote(corps_reponse)}"

        # 🎯 AJOUT: Le bloc HTML avec les coordonnées du client
        corps_message = f"""
        <html><body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2>Bonjour {nom_client},</h2>
        <p>Nous avons bien enregistré votre demande de réservation. Voici le récapitulatif de votre dossier :</p>
        
        <h3 style="color: #2980b9;">📋 Vos informations :</h3>
        <ul style="list-style-type: none; padding-left: 0;">
            <li>👤 <b>Nom & Prénom :</b> {nom_client}</li>
            <li>📞 <b>Téléphone :</b> {c_tel}</li>
            <li>📧 <b>Email :</b> {email_destinataire}</li>
            <li>🏠 <b>Adresse :</b> {c_adresse}</li>
        </ul>

        <h3 style="color: #2980b9;">🚗 Détails de la location :</h3>
        <ul style="list-style-type: none; padding-left: 0;">
            <li>🚙 <b>Véhicule :</b> {marque} {modele} ({immat})</li>
            <li>👔 <b>Chauffeur :</b> {chauffeur_texte}</li>
            <li>📍 <b>Destination :</b> {lieu_texte}</li>
            <li>📅 <b>Du :</b> {d_debut} <b>Au :</b> {d_fin}</li>
        </ul><br>
        
        <div style="background-color: #fdfde3; border: 1px solid #f39c12; padding: 15px; border-radius: 5px; text-align: center;">
            <h3 style="color: #c0392b; margin-top: 0;">⚠️ ACTION REQUISE POUR VALIDER LA RÉSERVATION ⚠️</h3>
            <p>Cliquez sur le bouton ci-dessous puis envoyez le message généré automatiquement :</p><br>
            <a href="{lien_mailto}" style="background-color: #2ecc71; color: white; padding: 12px 25px; text-decoration: none; font-weight: bold; border-radius: 4px; display: inline-block;">✅ CLIQUEZ ICI POUR CONFIRMER</a>
        </div>
        </body></html>
        """

        msg = MIMEMultipart(); msg['From'] = email_agence; msg['To'] = email_destinataire; msg['Subject'] = sujet_agence
        msg.attach(MIMEText(corps_message, 'html'))

        try:
            serveur = smtplib.SMTP('smtp.gmail.com', 587); serveur.starttls(); serveur.login(email_agence, mot_de_passe_app)
            serveur.send_message(msg); serveur.quit()
            return True, "Email envoyé avec succès."
        except Exception as e: return False, f"Erreur réseau : {e}"

    def ouvrir_dialogue_reservation(self):
        id_client = self.combo_client.currentData()
        id_chauffeur = self.combo_chauffeur.currentData()
        immat = self.combo_vehicule.currentData()
        
        try:
            lieu_arr = self.input_lieu.text().strip()
        except AttributeError:
            lieu_arr = ""
            print("Attention: le champ 'input_lieu' est introuvable dans l'UI.")
            
        if not immat: return QMessageBox.warning(self, "Erreur", "Sélectionnez un véhicule.")

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Réservation - {immat}")
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("📅 Dates de la location :"))
        date_depart = QDateTimeEdit(QDateTime.currentDateTime()); layout.addWidget(date_depart)
        date_retour = QDateTimeEdit(QDateTime.currentDateTime().addDays(3)); layout.addWidget(date_retour)
        btn_valider = QPushButton("✅ Enregistrer & Demander Confirmation"); layout.addWidget(btn_valider)
        
        def valider_reservation():
            date_s = date_depart.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            date_r = date_retour.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            
            if date_r <= date_s: return QMessageBox.warning(dialog, "Erreur", "Date de fin invalide.")
            try:
                conn = self.db_connect(); cursor = conn.cursor()
                cursor.execute("INSERT INTO LOCATION (id_client, immatriculation, id_chauffeur, date_sortie, date_retour_prevue, statut_location, confirmation_client, lieu_arrivee) VALUES (?, ?, ?, ?, ?, 'En attente', 0, ?)", (id_client, immat, id_chauffeur, date_s, date_r, lieu_arr))
                id_loc_creee = cursor.lastrowid; conn.commit()
                
                # 🎯 AJOUT: Récupération de téléphone et adresse à la création
                cursor.execute("SELECT nom, prenom, email, telephone, adresse FROM CLIENT WHERE id_client = ?", (id_client,))
                c_data = cursor.fetchone()
                cursor.execute("SELECT marque, modele FROM VEHICULE WHERE immatriculation = ?", (immat,))
                v_data = cursor.fetchone()
                ch_nom = ""
                if id_chauffeur:
                    cursor.execute("SELECT nom, prenom FROM CHAUFFEUR WHERE id_chauffeur = ?", (id_chauffeur,))
                    ch_info = cursor.fetchone()
                    if ch_info: ch_nom = f"{ch_info[0]} {ch_info[1]}"

                if c_data and v_data and c_data[2]: 
                    tel_str = c_data[3] if c_data[3] else "Non renseigné"
                    adr_str = c_data[4] if c_data[4] else "Non renseignée"
                    
                    succes, message = self.envoyer_email_confirmation(c_data[2], f"{c_data[0]} {c_data[1]}", tel_str, adr_str, immat, v_data[0], v_data[1], ch_nom, date_s, date_r, id_loc_creee, lieu_arr)
                    if succes: 
                        cursor.execute("UPDATE LOCATION SET date_envoi_confirmation = ? WHERE id_location = ?", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id_loc_creee)); conn.commit()
                        QMessageBox.information(dialog, "Succès", "Réservation créée et email envoyé !")
                    else: QMessageBox.warning(dialog, "Mode Hors-Ligne Activé 🔌", f"Réservation créée, mais email non envoyé : {message}\nIl sera envoyé automatiquement dès le retour de la connexion.")
                dialog.accept()
                
                try:
                    self.input_lieu.clear()
                except AttributeError:
                    pass
                
            except sqlite3.Error as e: print(e)
            finally:
                if 'conn' in locals() and conn: conn.close()
            self.load_locations(); self.charger_comboboxes(); self.location_terminee.emit() 

        btn_valider.clicked.connect(valider_reservation); dialog.exec()

    def valider_confirmation_manuelle(self):
        selected = self.tableVoyages.currentItem()
        if not selected: return QMessageBox.warning(self, "Erreur", "Sélectionnez une réservation.")
        id_loc = selected.data(0, Qt.ItemDataRole.UserRole)
        try:
            conn = self.db_connect(); conn.cursor().execute("UPDATE LOCATION SET confirmation_client = 1, statut_location = 'Planifiée' WHERE id_location = ?", (id_loc,)); conn.commit()
            QMessageBox.information(self, "Validé", "Réservation confirmée.")
        except sqlite3.Error as e: print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
        self.load_locations()

    def renvoyer_email_manuel(self):
        selected = self.tableVoyages.currentItem()
        if not selected: return QMessageBox.warning(self, "Erreur", "Sélectionnez une réservation.")
        id_loc = selected.data(0, Qt.ItemDataRole.UserRole)
        try:
            conn = self.db_connect(); cursor = conn.cursor()
            # 🎯 AJOUT: Récupération de téléphone et adresse pour le renvoi manuel
            cursor.execute("SELECT L.date_sortie, L.date_retour_prevue, C.nom, C.prenom, C.email, C.telephone, C.adresse, V.immatriculation, V.marque, V.modele, CH.nom, CH.prenom, L.lieu_arrivee FROM LOCATION L JOIN CLIENT C ON L.id_client = C.id_client JOIN VEHICULE V ON L.immatriculation = V.immatriculation LEFT JOIN CHAUFFEUR CH ON L.id_chauffeur = CH.id_chauffeur WHERE L.id_location = ?", (id_loc,))
            data = cursor.fetchone()
            if data and data[4]: 
                tel_str = data[5] if data[5] else "Non renseigné"
                adr_str = data[6] if data[6] else "Non renseignée"
                ch_nom_complet = f"{data[10]} {data[11]}" if data[10] else ""
                
                succes, msg = self.envoyer_email_confirmation(data[4], f"{data[2]} {data[3]}", tel_str, adr_str, data[7], data[8], data[9], ch_nom_complet, data[0], data[1], id_loc, data[12])
                if succes:
                    cursor.execute("UPDATE LOCATION SET date_envoi_confirmation = ? WHERE id_location = ?", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id_loc)); conn.commit()
                    QMessageBox.information(self, "Succès", "Relance envoyée !")
                else: QMessageBox.warning(self, "Erreur", f"Échec de l'envoi : {msg}")
        except sqlite3.Error as e: print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
        self.load_locations()

    def enregistrer_sortie(self):
        selected = self.tableVoyages.currentItem()
        if not selected: return QMessageBox.warning(self, "Erreur", "Sélectionnez une réservation.")
        if selected.text(4) != 'Planifiée': return QMessageBox.warning(self, "Erreur", "La réservation doit être Planifiée.")
        id_loc = selected.data(0, Qt.ItemDataRole.UserRole); immat = selected.text(2)
        try:
            conn = self.db_connect(); cursor = conn.cursor()
            cursor.execute("UPDATE LOCATION SET statut_location = 'En location', date_sortie = ? WHERE id_location = ?", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id_loc))
            cursor.execute("UPDATE VEHICULE SET statut_disponibilite = 'En location' WHERE immatriculation = ?", (immat,)); conn.commit()
            QMessageBox.information(self, "Validé", "Sortie enregistrée.")
        except sqlite3.Error as e: print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
        self.load_locations(); self.location_terminee.emit()

    def enregistrer_retour(self):
        selected = self.tableVoyages.currentItem()
        if not selected: return QMessageBox.warning(self, "Erreur", "Sélectionnez une réservation active.")
        id_loc = selected.data(0, Qt.ItemDataRole.UserRole); immat = selected.text(2)
        try:
            conn = self.db_connect(); cursor = conn.cursor()
            cursor.execute("UPDATE LOCATION SET statut_location = 'Terminée', date_retour_reelle = ? WHERE id_location = ?", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id_loc))
            cursor.execute("UPDATE VEHICULE SET statut_disponibilite = 'Disponible' WHERE immatriculation = ?", (immat,)); conn.commit()
            QMessageBox.information(self, "Validé", "Retour enregistré.")
        except sqlite3.Error as e: print(e)
        finally:
            if 'conn' in locals() and conn: conn.close()
        self.load_locations(); self.location_terminee.emit()

    def imprimer_contrat(self):
        selected = self.tableVoyages.currentItem()
        if not selected: return QMessageBox.warning(self, "Erreur", "Sélectionnez une location.")
        id_loc = selected.data(0, Qt.ItemDataRole.UserRole)
        try:
            conn = self.db_connect(); cursor = conn.cursor()
            cursor.execute("""
                SELECT C.nom, C.prenom, C.telephone, C.email, C.adresse,
                       V.immatriculation, V.marque, V.modele,
                       L.date_sortie, COALESCE(L.date_retour_prevue, L.date_retour_reelle),
                       L.statut_location, CH.nom, CH.prenom, L.lieu_arrivee
                FROM LOCATION L JOIN CLIENT C ON L.id_client = C.id_client
                JOIN VEHICULE V ON L.immatriculation = V.immatriculation
                LEFT JOIN CHAUFFEUR CH ON L.id_chauffeur = CH.id_chauffeur
                WHERE L.id_location = ?
            """, (id_loc,))
            data = cursor.fetchone()
            if not data: return
            c_nom, c_prenom, c_tel, c_email, c_adresse, v_immat, v_marque, v_modele, d_sortie, d_retour, statut, ch_nom, ch_prenom, lieu_arrivee = data
        except sqlite3.Error as e: return
        finally:
            if 'conn' in locals() and conn: conn.close()

        fichier, _ = QFileDialog.getSaveFileName(self, "Enregistrer Contrat", f"Contrat_{id_loc}_{c_nom}.pdf", "Fichiers PDF (*.pdf)")
        if not fichier: return
        try:
            c = canvas.Canvas(fichier, pagesize=A4)
            largeur, hauteur = A4
            
            c.setFont("Helvetica-Bold", 24)
            c.setFillColorRGB(0.17, 0.24, 0.31)
            c.drawString(2 * cm, hauteur - 3 * cm, "CONTRAT DE LOCATION AUTOMOBILE")
            
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(2 * cm, hauteur - 4 * cm, f"Référence Contrat : N° {id_loc}")
            c.drawString(2 * cm, hauteur - 4.5 * cm, f"Édité le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
            
            c.setStrokeColorRGB(0.74, 0.76, 0.78)
            c.line(2 * cm, hauteur - 5 * cm, largeur - 2 * cm, hauteur - 5 * cm)
            
            c.setFont("Helvetica-Bold", 14)
            c.setFillColorRGB(0.16, 0.5, 0.72)
            c.drawString(2 * cm, hauteur - 6.5 * cm, "1. INFORMATIONS DU LOCATAIRE")
            c.setFont("Helvetica", 12)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(2.5 * cm, hauteur - 7.5 * cm, f"Nom & Prénom : {c_nom} {c_prenom}")
            c.drawString(2.5 * cm, hauteur - 8.2 * cm, f"Téléphone : {c_tel if c_tel else 'Non renseigné'}")
            c.drawString(2.5 * cm, hauteur - 8.9 * cm, f"Email : {c_email}")
            c.drawString(2.5 * cm, hauteur - 9.6 * cm, f"Adresse : {c_adresse if c_adresse else 'Non renseignée'}")
            
            c.setFont("Helvetica-Bold", 14)
            c.setFillColorRGB(0.16, 0.5, 0.72)
            c.drawString(2 * cm, hauteur - 11.5 * cm, "2. VÉHICULE LOUÉ")
            c.setFont("Helvetica", 12)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(2.5 * cm, hauteur - 12.5 * cm, f"Marque & Modèle : {v_marque} {v_modele}")
            c.drawString(2.5 * cm, hauteur - 13.2 * cm, f"Immatriculation : {v_immat}")
            chauffeur_str = f"{ch_nom} {ch_prenom}" if ch_nom else "SANS CHAUFFEUR"
            c.drawString(2.5 * cm, hauteur - 13.9 * cm, f"Chauffeur assigné : {chauffeur_str}")
            
            c.setFont("Helvetica-Bold", 14)
            c.setFillColorRGB(0.16, 0.5, 0.72)
            c.drawString(2 * cm, hauteur - 15.8 * cm, "3. PÉRIODE ET STATUT")
            c.setFont("Helvetica", 12)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(2.5 * cm, hauteur - 16.8 * cm, f"Date de Départ : {d_sortie}")
            c.drawString(2.5 * cm, hauteur - 17.5 * cm, f"Date de Retour : {d_retour}")
            c.drawString(2.5 * cm, hauteur - 18.2 * cm, f"Destination : {lieu_arrivee if lieu_arrivee else 'Non spécifiée'}")
            c.drawString(2.5 * cm, hauteur - 18.9 * cm, f"Statut actuel : {statut}")
            
            c.setFont("Helvetica-Oblique", 10)
            c.setFillColorRGB(0.3, 0.3, 0.3)
            c.drawString(2 * cm, hauteur - 21 * cm, "Le locataire declare avoir examine le vehicule et reconnu qu'il est en bon etat de marche.")
            c.drawString(2 * cm, hauteur - 21.6 * cm, "Il s'engage a le restituer dans le meme etat a la date convenue.")
            
            c.setFont("Helvetica-Bold", 12)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(3 * cm, 6 * cm, "Signature de l'Agence :")
            c.drawString(13 * cm, 6 * cm, "Signature du Locataire :")
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(13 * cm, 5.5 * cm, "Lu et approuve,")
            
            c.save()
            if os.name == 'nt': os.startfile(fichier)
            elif sys.platform == "darwin": 
                import subprocess
                subprocess.Popen(["open", fichier])
            else: 
                import subprocess
                subprocess.Popen(["xdg-open", fichier])
        except Exception as e: pass