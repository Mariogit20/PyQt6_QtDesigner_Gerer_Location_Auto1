# -*- coding: utf-8 -*-
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QMessageBox, QTabWidget, QTreeWidget, QTreeWidgetItem, QDialog, QLineEdit)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class GestionIA(QWidget):
    def __init__(self, db_connect_func):
        super().__init__()
        self.db_connect = db_connect_func
        self.layout_principal = QVBoxLayout(self)
        
        titre = QLabel("🧠 Moteur d'Intelligence Décisionnelle & Système Expert")
        titre.setStyleSheet("color: #2c3e50; font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_principal.addWidget(titre)
        
        self.btn_analyser = QPushButton("🔍 Lancer l'Analyse Profonde")
        self.btn_analyser.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold; padding: 12px; border-radius: 5px;")
        self.btn_analyser.clicked.connect(self.generer_analyse)
        self.layout_principal.addWidget(self.btn_analyser)
        
        self.onglets_ia = QTabWidget()
        self.onglets_ia.setStyleSheet("""
            QTabBar::tab { font-size: 14px; font-weight: bold; padding: 10px 20px; }
            QTabBar::tab:selected { background-color: #ecf0f1; color: #2980b9; border-bottom: 3px solid #3498db; }
        """)
        self.layout_principal.addWidget(self.onglets_ia)
        
        # --- ONGLET 1 : GRAPHIQUES ---
        self.tab_graphiques = QWidget()
        self.layout_graphiques = QVBoxLayout(self.tab_graphiques)
        self.onglets_ia.addTab(self.tab_graphiques, "📊 Tableau de Bord Visuel")
        
        # --- ONGLET 2 : RAPPORT EXPERT INTÉGRAL ---
        self.tab_rapport = QWidget()
        self.layout_rapport = QVBoxLayout(self.tab_rapport)
        self.zone_texte_rapport = QTextEdit()
        self.zone_texte_rapport.setReadOnly(True)
        self.zone_texte_rapport.setStyleSheet("background-color: #fdfde3; color: #2c3e50; font-size: 14px; line-height: 1.6; padding: 20px; border: 1px solid #f39c12;")
        self.layout_rapport.addWidget(self.zone_texte_rapport)
        self.onglets_ia.addTab(self.tab_rapport, "📑 Rapport Expert (Analyses Avancées)")

        # --- ONGLET 3 : MARKETING ET CRM ---
        self.tab_clients = QWidget()
        self.layout_clients = QVBoxLayout(self.tab_clients)
        
        self.btn_promo = QPushButton("📧 Envoyer une Offre Promotionnelle au Client Sélectionné")
        self.btn_promo.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.btn_promo.clicked.connect(self.ouvrir_dialogue_promo)
        self.layout_clients.addWidget(self.btn_promo)
        
        self.table_clients = QTreeWidget()
        self.table_clients.setHeaderLabels(["ID", "Nom", "Catégorie", "Email", "Téléphone", "Dernière Loc"])
        self.table_clients.setStyleSheet("QTreeWidget { font-size: 13px; } QHeaderView::section { background-color: #34495e; color: white; font-weight: bold; }")
        self.layout_clients.addWidget(self.table_clients)
        self.onglets_ia.addTab(self.tab_clients, "👥 Détails Clustering")
        
        self.canvas_ia = None

    def generer_analyse(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            maintenant = datetime.now()
            
            cursor.execute("SELECT V.marque || ' ' || V.modele as vehicule, COUNT(L.id_location) FROM LOCATION L JOIN VEHICULE V ON L.immatriculation = V.immatriculation GROUP BY vehicule ORDER BY COUNT(L.id_location) DESC LIMIT 5")
            top_vehicules = cursor.fetchall()
            
            cursor.execute("SELECT strftime('%m', date_sortie) as mois, COUNT(id_location) FROM LOCATION WHERE date_sortie IS NOT NULL GROUP BY mois ORDER BY mois")
            saisonnalite = cursor.fetchall()
            
            cursor.execute("SELECT C.id_client, C.nom, C.prenom, C.email, C.telephone, COUNT(L.id_location), MAX(L.date_sortie) FROM CLIENT C JOIN LOCATION L ON C.id_client = L.id_client WHERE L.date_sortie IS NOT NULL GROUP BY C.id_client")
            clients_stats = cursor.fetchall()
            
            nb_vips, nb_saisonniers, nb_endormis, nb_nouveaux = 0, 0, 0, 0
            client_clusters = {}
            self.table_clients.clear() 

            for client in clients_stats:
                id_c = client[0]
                try: jours_ecoules = (maintenant - datetime.strptime(client[6][:10], "%Y-%m-%d")).days
                except: jours_ecoules = 0
                
                if jours_ecoules > 365: cluster = 'Endormi'; icone = '❄️'; nb_endormis += 1
                elif client[5] >= 3: cluster = 'VIP'; icone = '👑'; nb_vips += 1
                elif client[5] == 2: cluster = 'Saisonnier'; icone = '☀️'; nb_saisonniers += 1
                else: cluster = 'Nouveau'; icone = '🌱'; nb_nouveaux += 1
                
                client_clusters[id_c] = cluster
                item = QTreeWidgetItem(self.table_clients)
                item.setText(0, str(id_c)); item.setText(1, f"{client[1]} {client[2] if client[2] else ''}"); item.setText(2, f"{icone} {cluster}"); item.setText(3, client[3] or "Non renseigné"); item.setText(4, client[4] or "Non renseigné"); item.setText(5, client[6][:10] if client[6] else "N/A")

            cursor.execute("SELECT L.id_client, V.marque || ' ' || V.modele, strftime('%m', L.date_sortie) FROM LOCATION L JOIN VEHICULE V ON L.immatriculation = V.immatriculation WHERE L.date_sortie IS NOT NULL")
            toutes_locations = cursor.fetchall()
            vip_vehicules, vip_mois, nouveaux_vehicules, nouveaux_mois = {}, {}, {}, {}
            for loc in toutes_locations:
                le_cluster = client_clusters.get(loc[0])
                if le_cluster == 'VIP': vip_vehicules[loc[1]] = vip_vehicules.get(loc[1], 0) + 1; vip_mois[loc[2]] = vip_mois.get(loc[2], 0) + 1
                elif le_cluster == 'Nouveau': nouveaux_vehicules[loc[1]] = nouveaux_vehicules.get(loc[1], 0) + 1; nouveaux_mois[loc[2]] = nouveaux_mois.get(loc[2], 0) + 1

            cursor.execute("SELECT V.marque || ' ' || V.modele, CASE WHEN COALESCE(Loc.total_jours, 0) > 0 THEN COALESCE(Depense.total_carburant, 0) / Loc.total_jours ELSE 0 END as cout_jour FROM VEHICULE V JOIN (SELECT immatriculation, SUM(montant) as total_carburant FROM CONSOMMATION_CARBURANT GROUP BY immatriculation) Depense ON V.immatriculation = Depense.immatriculation JOIN (SELECT immatriculation, SUM(MAX(1, julianday(date_retour_reelle) - julianday(date_sortie))) as total_jours FROM LOCATION WHERE date_retour_reelle IS NOT NULL GROUP BY immatriculation) Loc ON V.immatriculation = Loc.immatriculation WHERE cout_jour > 0 ORDER BY cout_jour DESC LIMIT 5")
            carburant_stats = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM VEHICULE WHERE statut_disponibilite != 'Hors service'")
            total_flotte = cursor.fetchone()[0] or 1
            date_dans_15j = (maintenant + timedelta(days=15)).strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(*) FROM LOCATION WHERE date_sortie BETWEEN date('now') AND ?", (date_dans_15j,))
            resas_futures = cursor.fetchone()[0] or 0
            taux_occupation_futur = (resas_futures / total_flotte) * 100

            cursor.execute("SELECT V.immatriculation, V.marque || ' ' || V.modele, SUM(R.cout_main_d_oeuvre) FROM VEHICULE V JOIN REPARATION R ON V.immatriculation = R.immatriculation GROUP BY V.immatriculation HAVING SUM(R.cout_main_d_oeuvre) > 0 ORDER BY SUM(R.cout_main_d_oeuvre) DESC LIMIT 3")
            gouffres = cursor.fetchall()

            cursor.execute("SELECT C.nom || ' ' || C.prenom, AVG(julianday(L.date_retour_reelle) - julianday(L.date_retour_prevue)) FROM LOCATION L JOIN CLIENT C ON L.id_client = C.id_client WHERE L.date_retour_reelle IS NOT NULL AND L.date_retour_prevue IS NOT NULL AND L.date_retour_reelle > L.date_retour_prevue GROUP BY L.id_client HAVING AVG(julianday(L.date_retour_reelle) - julianday(L.date_retour_prevue)) > 0.5 ORDER BY AVG(julianday(L.date_retour_reelle) - julianday(L.date_retour_prevue)) DESC LIMIT 3")
            clients_risque = cursor.fetchall()

            cursor.execute("SELECT V.immatriculation, V.marque || ' ' || V.modele, MAX(L.date_retour_reelle) FROM VEHICULE V LEFT JOIN LOCATION L ON V.immatriculation = L.immatriculation WHERE V.statut_disponibilite = 'Disponible' GROUP BY V.immatriculation ORDER BY MAX(L.date_retour_reelle) ASC NULLS FIRST LIMIT 3")
            vehicules_endormis = cursor.fetchall()

        except sqlite3.Error as e: return
        finally:
            if 'conn' in locals() and conn: conn.close()

        # ==========================================
        # 🎨 CRÉATION DES GRAPHIQUES (CORRECTION SUPERPOSITION)
        # ==========================================
        if self.canvas_ia is not None:
            self.layout_graphiques.removeWidget(self.canvas_ia)
            self.canvas_ia.deleteLater()
            self.canvas_ia = None
            
        plt.close('all')
        
        # On agrandit la zone de dessin
        fig, axes = plt.subplots(2, 2, figsize=(15, 11))
        fig.patch.set_facecolor('#ffffff')
        ax1, ax2, ax3, ax4 = axes[0,0], axes[0,1], axes[1,0], axes[1,1]
        
        # 📊 1. Graphe Top Modèles
        if top_vehicules:
            noms_v = [v[0] for v in top_vehicules]
            valeurs_v = [v[1] for v in top_vehicules]
            
            barres = ax1.bar(noms_v, valeurs_v, color='#3498db')
            ax1.set_title("Top 5 Modèles Rentables", fontweight='bold', fontsize=12)
            
            # 🛠️ FIX : On réduit le "labelpad" pour recoller la légende à son graphique
            ax1.set_xlabel("Modèles de Véhicules", fontweight='bold', color='#7f8c8d', labelpad=5)
            ax1.set_ylabel("Nombre de Locations", fontweight='bold', color='#7f8c8d', labelpad=5)
            ax1.tick_params(axis='x', rotation=15) # Rotation douce pour gagner de la place
            ax1.bar_label(barres, fmt='%d', label_type='center', color='white', fontweight='bold', fontsize=12)
        
        # 📈 2. Graphe Saisonnalité
        mois_noms = {'01':'Janv', '02':'Fév', '03':'Mar', '04':'Avr', '05':'Mai', '06':'Juin', '07':'Juil', '08':'Août', '09':'Sep', '10':'Oct', '11':'Nov', '12':'Déc'}
        if saisonnalite:
            mois_x = [mois_noms.get(m[0], m[0]) for m in saisonnalite]
            valeurs_m = [m[1] for m in saisonnalite]
            
            ax2.plot(mois_x, valeurs_m, marker='o', color='#e74c3c', linewidth=2)
            ax2.set_title("Courbe de Saisonnalité", fontweight='bold', fontsize=12)
            ax2.set_xlabel("Mois de l'Année", fontweight='bold', color='#7f8c8d', labelpad=5)
            ax2.set_ylabel("Volume de Locations", fontweight='bold', color='#7f8c8d', labelpad=5)
            ax2.grid(True, linestyle='--', alpha=0.6)
            for i, txt in enumerate(valeurs_m):
                ax2.annotate(txt, (mois_x[i], valeurs_m[i]), textcoords="offset points", xytext=(0,8), ha='center', fontweight='bold', color='#c0392b')
            
        # 🥧 3. Graphe Clustering
        tot = nb_vips + nb_saisonniers + nb_nouveaux + nb_endormis
        if tot > 0:
            sizes = [s for s in [nb_vips, nb_saisonniers, nb_nouveaux, nb_endormis] if s > 0]
            labels = [l for s, l in zip([nb_vips, nb_saisonniers, nb_nouveaux, nb_endormis], ['VIPs', 'Saisonniers', 'Nouveaux', 'Endormis']) if s > 0]
            colors = [c for s, c in zip([nb_vips, nb_saisonniers, nb_nouveaux, nb_endormis], ['#9b59b6', '#f1c40f', '#2ecc71', '#95a5a6']) if s > 0]
            ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax3.set_title("Clustering Clientèle", fontweight='bold', fontsize=12)

        # ⛽ 4. Graphe Carburant
        if carburant_stats:
            ax4.pie([c[1] for c in carburant_stats], labels=[f"{c[0]}\n({c[1]:.2f}€/j)" for c in carburant_stats], autopct='%1.1f%%', startangle=45)
            ax4.set_title("Pire Dépense Carburant (Coût/Jour)", fontweight='bold', fontsize=12)
        else:
            ax4.text(0.5, 0.5, "Pas assez de données de carburant", ha='center', va='center', color='gray')
            ax4.axis('off')

        # 🛠️ FIX ULTIME : On impose manuellement un espace vertical géant entre les graphiques (hspace=0.8)
        fig.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.9, wspace=0.3, hspace=0.8)
        
        self.canvas_ia = FigureCanvas(fig)
        self.layout_graphiques.addWidget(self.canvas_ia)

        # ==========================================
        # 🧠 RAPPORT EXPERT 
        # ==========================================
        html = f"<h2 style='color:#2980b9;'>📑 Rapport d'Intelligence Décisionnelle Intégral du {maintenant.strftime('%d/%m/%Y')}</h2><hr>"
        
        html += f"<h3>💹 1. Yield Management (Tarification)</h3><ul>"
        if taux_occupation_futur > 75: html += f"<li>📈 <b>Forte Demande :</b> {taux_occupation_futur:.0f}% de la flotte est réservée. <b>💡 IA : Augmentez vos tarifs de +15%.</b></li></ul>"
        elif taux_occupation_futur < 30: html += f"<li>📉 <b>Basse Saison :</b> {taux_occupation_futur:.0f}% de la flotte est réservée. <b>💡 IA : Lancez une promotion flash.</b></li></ul>"
        else: html += f"<li>⚖️ <b>Activité Normale :</b> {taux_occupation_futur:.0f}% de la flotte réservée. Maintenez les prix.</li></ul>"

        html += f"<h3>⏱️ 2. Risk Scoring (Clients)</h3><ul>"
        if clients_risque:
            html += "<li>🚨 <b>Profils à risque (Retards) :</b></li><ul>"
            for c in clients_risque: html += f"<li>Client {c[0]} : {c[1]:.1f} jours de retard moyen.</li>"
            html += "</ul><li><b>💡 IA : Exigez une caution plus importante pour ces clients.</b></li></ul>"
        else: html += "<li>✅ Aucun retard chronique détecté chez vos clients.</li></ul>"

        html += f"<h3>🔧 3. Alertes Maintenance</h3><ul>"
        if gouffres:
            html += "<li>⚠️ <b>Gouffres financiers détectés :</b></li><ul>"
            for v in gouffres: html += f"<li>{v[1]} : {v[2]:.2f} € de réparations.</li>"
            html += "</ul><li><b>💡 IA : Envisagez une revente de ces véhicules.</b></li></ul>"
        else: html += "<li>✅ Aucun frais mécanique critique détecté.</li></ul>"

        html += f"<h3>🛌 4. Taux de Rotation</h3><ul>"
        if vehicules_endormis and vehicules_endormis[0][2]:
            j_inactif = (maintenant - datetime.strptime(vehicules_endormis[0][2][:10], "%Y-%m-%d")).days
            if j_inactif > 30: html += f"<li>💤 Le véhicule <b>{vehicules_endormis[0][1]}</b> n'a pas été loué depuis {j_inactif} jours. <b>💡 IA : Proposez-le en Location Longue Durée.</b></li></ul>"
            else: html += "<li>✅ Rotation saine des véhicules.</li></ul>"
        else: html += "<li>✅ Rotation saine des véhicules.</li></ul>"

        html += f"<h3>🔍 5. Analyse Croisée (Préférences)</h3><ul>"
        if vip_vehicules and vip_mois: html += f"<li>👑 <b>VIPs :</b> Préfèrent le modèle <b>{max(vip_vehicules, key=vip_vehicules.get)}</b> (Mois : {mois_noms.get(max(vip_mois, key=vip_mois.get), max(vip_mois, key=vip_mois.get))}).</li>"
        if nouveaux_vehicules and nouveaux_mois: html += f"<li>🌱 <b>Nouveaux :</b> Attirés par le modèle <b>{max(nouveaux_vehicules, key=nouveaux_vehicules.get)}</b> (Mois : {mois_noms.get(max(nouveaux_mois, key=nouveaux_mois.get), max(nouveaux_mois, key=nouveaux_mois.get))}).</li>"
        html += "</ul>"

        self.zone_texte_rapport.setHtml(html)
        self.onglets_ia.setCurrentIndex(0) # Ramène sur l'onglet Visuel pour admirer le résultat
        self.table_clients.resizeColumnToContents(1)
        self.table_clients.resizeColumnToContents(3)

    # ==========================================
    # 🎯 FONCTION MARKETING 
    # ==========================================
    def ouvrir_dialogue_promo(self):
        selected = self.table_clients.currentItem()
        if not selected: return QMessageBox.warning(self, "Erreur", "Sélectionnez un client dans la liste.")
            
        nom_client = selected.text(1); categorie_ia = selected.text(2); email_client = selected.text(3)
        if "@" not in email_client: return QMessageBox.warning(self, "Erreur", "Email invalide pour ce client.")

        sujet = "Une offre spéciale pour vous !"
        corps = f"Bonjour {nom_client},<br><br>Nous avons une offre pour vous."
        if "Nouveau" in categorie_ia: sujet = "🎁 Cadeau : -10% sur votre prochaine location !"; corps = f"Bonjour {nom_client},<br><br>Voici 10% de réduction avec le code BIENVENUE10."
        elif "Endormi" in categorie_ia: sujet = "🚗 Vous nous manquez ! Voici -20%"; corps = f"Bonjour {nom_client},<br><br>Voici 20% de remise avec le code RETOUR20."
        elif "VIP" in categorie_ia: sujet = "👑 Surclassement gratuit pour vous !"; corps = f"Bonjour {nom_client},<br><br>Nous vous offrons un surclassement gratuit lors de votre prochain passage."

        dialog = QDialog(self); dialog.setWindowTitle(f"Marketing - {nom_client}"); layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"<b>Destinataire :</b> {email_client}"))
        input_sujet = QLineEdit(sujet); layout.addWidget(input_sujet)
        input_corps = QTextEdit(); input_corps.setHtml(corps); layout.addWidget(input_corps)
        
        btn_envoyer = QPushButton("🚀 Envoyer l'Offre")
        btn_envoyer.setStyleSheet("background-color: #27ae60; color: white; padding: 10px;")
        
        def valider_envoi():
            from VerificateurEmail import verifier_email_complet
            est_valide, msg_erreur = verifier_email_complet(email_client)
            if not est_valide: return QMessageBox.warning(dialog, "Email Invalide", f"Envoi bloqué par sécurité !\n\n{msg_erreur}")

            try:
                msg = MIMEMultipart(); msg['From'] = "progsuividpe@gmail.com"; msg['To'] = email_client; msg['Subject'] = input_sujet.text()
                html_final = f"<html><body style='font-family: Arial; padding: 20px;'>{input_corps.toHtml()}</body></html>"
                msg.attach(MIMEText(html_final, 'html'))
                serveur = smtplib.SMTP('smtp.gmail.com', 587); serveur.starttls(); serveur.login("progsuividpe@gmail.com", "mmtbbxsrnzzbreaj")
                serveur.send_message(msg); serveur.quit()
                QMessageBox.information(dialog, "Succès", "L'offre a été envoyée !"); dialog.accept()
            except Exception as e: QMessageBox.critical(dialog, "Erreur", f"Erreur d'envoi : {e}")

        btn_envoyer.clicked.connect(valider_envoi); layout.addWidget(btn_envoyer)
        dialog.exec()