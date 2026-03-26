# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QTableWidget, QTableWidgetItem, QLabel, QPushButton, 
                             QHeaderView, QDateEdit, QMessageBox, QScrollArea, QDialog, QDateTimeEdit)
from PyQt6.QtCore import Qt, QDate, QDateTime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

from GestionHistorique import GestionHistorique

class GestionPlanning(QWidget):
    def __init__(self, db_connect_func):
        super().__init__()
        self.db_connect = db_connect_func
        
        # 🎯 INITIALISATION DU NIVEAU DE ZOOM
        self.zoom_level = 1.0
        
        self.layout_principal = QVBoxLayout(self)
        self.onglets = QTabWidget()
        self.layout_principal.addWidget(self.onglets)
        
        self.tab_gantt = QWidget()
        self.layout_gantt = QVBoxLayout(self.tab_gantt)
        
        self.toolbar_gantt = QHBoxLayout()
        self.label_debut = QLabel("📅 Du :")
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate().addDays(-7)) 
        
        self.label_fin = QLabel("Au :")
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate().addDays(30)) 
        
        self.btn_rechercher_gantt = QPushButton("🔍 Actualiser la période")
        self.btn_rechercher_gantt.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 6px 15px; border-radius: 4px;")
        
        # 🎯 BOUTONS DE ZOOM
        self.btn_zoom_out = QPushButton("➖ Dézoomer")
        self.btn_zoom_out.setStyleSheet("background-color: #95a5a6; color: white; font-weight: bold; padding: 6px 10px; border-radius: 4px;")
        
        self.btn_zoom_in = QPushButton("➕ Zoomer")
        self.btn_zoom_in.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 6px 10px; border-radius: 4px;")
        
        self.toolbar_gantt.addWidget(self.label_debut)
        self.toolbar_gantt.addWidget(self.date_debut)
        self.toolbar_gantt.addWidget(self.label_fin)
        self.toolbar_gantt.addWidget(self.date_fin)
        self.toolbar_gantt.addWidget(self.btn_rechercher_gantt)
        self.toolbar_gantt.addSpacing(20)
        self.toolbar_gantt.addWidget(self.btn_zoom_out)
        self.toolbar_gantt.addWidget(self.btn_zoom_in)
        self.toolbar_gantt.addStretch()
        self.layout_gantt.addLayout(self.toolbar_gantt)
        
        self.scroll_area_gantt = QScrollArea()
        self.scroll_area_gantt.setWidgetResizable(True)
        self.scroll_area_gantt.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area_gantt.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.layout_gantt.addWidget(self.scroll_area_gantt)
        
        self.canvas_gantt = None
        self.onglets.addTab(self.tab_gantt, "📊 Planning des Réservations (Gantt)")
        
        self.tab_dispos = QWidget()
        self.layout_dispos = QVBoxLayout(self.tab_dispos)
        self.table_dispos = QTableWidget()
        self.table_dispos.setColumnCount(4)
        self.table_dispos.setHorizontalHeaderLabels(["Immatriculation", "Marque", "Modèle", "Kilométrage"])
        self.table_dispos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout_dispos.addWidget(self.table_dispos)
        self.onglets.addTab(self.tab_dispos, "✅ Voitures Disponibles")
        
        self.tab_non_dispos = QWidget()
        self.layout_non_dispos = QVBoxLayout(self.tab_non_dispos)
        self.table_non_dispos = QTableWidget()
        self.table_non_dispos.setColumnCount(4)
        self.table_non_dispos.setHorizontalHeaderLabels(["Immatriculation", "Marque", "Modèle", "Statut Actuel"])
        self.table_non_dispos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout_non_dispos.addWidget(self.table_non_dispos)
        self.onglets.addTab(self.tab_non_dispos, "❌ Voitures Non Disponibles")
        
        # 🎯 CONNEXIONS DES BOUTONS
        self.btn_rechercher_gantt.clicked.connect(self.reset_zoom_and_generate)
        self.btn_zoom_in.clicked.connect(self.action_zoom_in)
        self.btn_zoom_out.clicked.connect(self.action_zoom_out)
        self.onglets.currentChanged.connect(self.charger_donnees)
        
        self.charger_donnees()
        self.generer_gantt()

    # 🎯 FONCTIONS DE GESTION DU ZOOM
    def reset_zoom_and_generate(self):
        self.zoom_level = 1.0 # Réinitialise le zoom lors d'une nouvelle recherche
        self.generer_gantt()
        
    def action_zoom_in(self):
        self.zoom_level *= 1.5 # Grossit de 50%
        self.generer_gantt()
        
    def action_zoom_out(self):
        self.zoom_level /= 1.5 # Réduit de 50%
        self.generer_gantt()

    def charger_donnees(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            
            cursor.execute("SELECT immatriculation, marque, modele, kilometrage_actuel FROM VEHICULE WHERE statut_disponibilite = 'Disponible'")
            dispos = cursor.fetchall()
            self.table_dispos.setRowCount(len(dispos))
            for row_idx, row_data in enumerate(dispos):
                for col_idx, data in enumerate(row_data):
                    self.table_dispos.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
                    
            cursor.execute("SELECT immatriculation, marque, modele, statut_disponibilite FROM VEHICULE WHERE statut_disponibilite != 'Disponible'")
            non_dispos = cursor.fetchall()
            self.table_non_dispos.setRowCount(len(non_dispos))
            for row_idx, row_data in enumerate(non_dispos):
                for col_idx, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    if col_idx == 3: 
                        if data == "En location": item.setForeground(Qt.GlobalColor.blue)
                        elif data == "En réparation": item.setForeground(Qt.GlobalColor.red)
                    self.table_non_dispos.setItem(row_idx, col_idx, item)
                    
        except sqlite3.Error as e:
            print(f"Erreur SQL chargement listes: {e}")
        finally:
            if 'conn' in locals() and conn: conn.close()

    def generer_gantt(self):
        if self.canvas_gantt is not None:
            self.layout_gantt.removeWidget(self.canvas_gantt)
            self.canvas_gantt.deleteLater()
            self.canvas_gantt = None
            
        plt.close('all')
            
        d_debut_q = self.date_debut.date()
        d_fin_q = self.date_fin.date()
        
        date_debut_filtre = datetime(d_debut_q.year(), d_debut_q.month(), d_debut_q.day())
        date_fin_filtre = datetime(d_fin_q.year(), d_fin_q.month(), d_fin_q.day())
        
        if date_fin_filtre <= date_debut_filtre:
            QMessageBox.warning(self, "Période invalide", "La date de fin doit être strictement supérieure à la date de début.")
            return
            
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            
            def parse_dt(date_str):
                if not date_str: return None
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return datetime.strptime(date_str[:10], "%Y-%m-%d")
            
            cursor.execute("SELECT immatriculation, marque, modele FROM VEHICULE ORDER BY immatriculation")
            vehicules = cursor.fetchall()
            
            delta_jours = max(1, (date_fin_filtre - date_debut_filtre).days)
            
            # 🎯 TAILLE DYNAMIQUE MULTIPLIÉE PAR LE NIVEAU DE ZOOM
            hauteur_fig = max(6, len(vehicules) * 0.8) 
            largeur_fig = max(12, delta_jours * 0.25 * self.zoom_level) 
            
            fig, self.ax = plt.subplots(figsize=(largeur_fig, hauteur_fig))
            
            self.rectangles_gantt = [] 
            self.tooltip = self.ax.annotate(
                "", xy=(0,0), xytext=(15, 15),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.5", fc="#fdfde3", ec="black", lw=1),
                fontsize=10, zorder=100
            )
            self.tooltip.set_visible(False)

            y_ticks = []
            y_labels = []
            self.ax.set_xlim(date_debut_filtre, date_fin_filtre)
            
            # 🎯 GESTION INTELLIGENTE DE L'ÉCHELLE DU TEMPS SELON LE ZOOM
            visual_span = delta_jours / self.zoom_level
            
            if visual_span <= 3:
                # Si on est très zoomé (ou sur très peu de jours) : on affiche les Heures
                self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=4)) # Toutes les 4 heures
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
            elif visual_span <= 35:
                # Affichage par jours
                self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            elif visual_span <= 95:
                # Affichage par semaines
                self.ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
            elif visual_span <= 365:
                # Affichage par mois
                self.ax.xaxis.set_major_locator(mdates.MonthLocator())
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            else:
                # Si on est très dézoomé (plusieurs années) : on affiche les Années
                self.ax.xaxis.set_major_locator(mdates.YearLocator())
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

            legende_loc_ajoutee = False
            legende_plan_ajoutee = False
            self.legende_retard_ajoutee = False 
            legende_rep_ajoutee = False

            maintenant = datetime.now()

            for index, (immat, marque, modele) in enumerate(vehicules):
                position_y = index * 10
                y_ticks.append(position_y + 5)
                y_labels.append(f"{immat}\n({marque})")
                
                cursor.execute("""
                    SELECT L.id_location, L.date_sortie, L.date_retour_prevue, L.statut_location, C.nom, C.prenom 
                    FROM LOCATION L
                    JOIN CLIENT C ON L.id_client = C.id_client
                    WHERE L.immatriculation = ? AND L.statut_location IN ('Planifiée', 'Planifié', 'En cours', 'En location')
                """, (immat,))
                
                for id_loc, date_debut, date_fin, statut, c_nom, c_prenom in cursor.fetchall():
                    try:
                        d_debut = parse_dt(date_debut)
                        d_fin = parse_dt(date_fin) if date_fin else d_debut + timedelta(days=1)
                        
                        duree_totale_flt = (d_fin - d_debut).total_seconds() / 86400.0
                        pourcentage_texte = "" 
                        
                        est_en_retard = False
                        if statut in ('En cours', 'En location') and d_fin < maintenant:
                            d_fin = maintenant 
                            duree_totale_flt = (d_fin - d_debut).total_seconds() / 86400.0
                            est_en_retard = True

                        if est_en_retard:
                            label = "⚠️ En retard !" if not self.legende_retard_ajoutee else ""
                            self.legende_retard_ajoutee = True
                            self.ax.broken_barh([(d_debut, timedelta(days=duree_totale_flt))], (position_y + 1, 8), 
                                       facecolors='#c0392b', label=label, alpha=0.9, edgecolor='black')
                        elif statut in ('En cours', 'En location'):
                            self.ax.broken_barh([(d_debut, timedelta(days=duree_totale_flt))], (position_y + 1, 8), 
                                       facecolors='#d5f5e3', edgecolor='black', linestyle=':') 
                            
                            temps_ecoule = (maintenant - d_debut).total_seconds() / 86400.0
                            if temps_ecoule < 0.1: temps_ecoule = 0.1 
                            if temps_ecoule > duree_totale_flt: temps_ecoule = duree_totale_flt
                            
                            pourcentage = int((temps_ecoule / duree_totale_flt) * 100) if duree_totale_flt > 0 else 0
                            pourcentage_texte = f"{pourcentage}%"

                            label = "Progression Location (En cours)" if not legende_loc_ajoutee else ""
                            legende_loc_ajoutee = True
                            self.ax.broken_barh([(d_debut, timedelta(days=temps_ecoule))], (position_y + 1, 8), 
                                       facecolors='#2ecc71', label=label, alpha=0.9, edgecolor='black')
                        else:
                            label = "Réservé (100% Planifié)" if not legende_plan_ajoutee else ""
                            legende_plan_ajoutee = True
                            self.ax.broken_barh([(d_debut, timedelta(days=duree_totale_flt))], (position_y + 1, 8), 
                                       facecolors='#3498db', label=label, alpha=0.9, edgecolor='black')
                        
                        alerte_texte = "\n🚨 VÉHICULE EN RETARD !" if est_en_retard else ""
                        self.rectangles_gantt.append({
                            'x_min': mdates.date2num(d_debut),
                            'x_max': mdates.date2num(d_debut) + max(0.1, duree_totale_flt),
                            'y_min': position_y + 1,
                            'y_max': position_y + 9,
                            'info': f"🚗 LOCATION ({statut}){alerte_texte}\n🚘 Véhicule: {marque} {modele}\n👤 Client: {c_nom} {c_prenom}\n📅 Du {d_debut.strftime('%d/%m/%Y à %H:%M')} au {d_fin.strftime('%d/%m/%Y à %H:%M')}\n(Cliquez pour modifier)",
                            'id': id_loc,
                            'type': 'location',
                            'immat': immat,
                            'marque': marque,
                            'modele': modele
                        })

                        # Ne dessiner le texte des dates que si on est assez zoomé (sinon ça devient illisible)
                        if visual_span <= 60:
                            self.ax.text(mdates.date2num(d_debut), position_y + 9.5, d_debut.strftime('%d/%m %H:%M'), 
                                         ha='right', va='bottom', fontsize=8, color='black', fontweight='bold')
                            self.ax.text(mdates.date2num(d_debut) + duree_totale_flt, position_y + 9.5, d_fin.strftime('%d/%m %H:%M'), 
                                         ha='left', va='bottom', fontsize=8, color='black', fontweight='bold')
                        
                        if pourcentage_texte:
                            centre_x = mdates.date2num(d_debut) + (duree_totale_flt / 2)
                            self.ax.text(centre_x, position_y + 5, pourcentage_texte, 
                                         ha='center', va='center', fontsize=9, color='black', fontweight='bold')
                            
                    except Exception as e: print(e)

                cursor.execute("""
                    SELECT id_reparation, date_debut_reparation, date_fin_reparation, nature_panne_tache 
                    FROM REPARATION 
                    WHERE immatriculation = ? AND statut_reparation = 'En cours'
                """, (immat,))
                
                for id_rep, date_debut, date_fin, nature in cursor.fetchall():
                    try:
                        d_debut = parse_dt(date_debut)
                        d_fin = parse_dt(date_fin) if date_fin else d_debut + timedelta(days=3) 
                        duree = (d_fin - d_debut).total_seconds() / 86400.0
                        
                        label = "En Réparation" if not legende_rep_ajoutee else ""
                        self.ax.broken_barh([(d_debut, timedelta(days=duree))], (position_y + 1, 8), 
                                       facecolors='#e67e22', label=label, alpha=0.9, hatch='///', edgecolor='black')
                        legende_rep_ajoutee = True
                        
                        self.rectangles_gantt.append({
                            'x_min': mdates.date2num(d_debut),
                            'x_max': mdates.date2num(d_debut) + max(0.1, duree),
                            'y_min': position_y + 1,
                            'y_max': position_y + 9,
                            'info': f"🔧 RÉPARATION\n🚘 Véhicule: {marque} {modele}\n⚠️ Nature: {nature}\n📅 Du {d_debut.strftime('%d/%m/%Y %H:%M')} au {d_fin.strftime('%d/%m/%Y %H:%M')}\n(Cliquez pour modifier)",
                            'id': id_rep,
                            'type': 'reparation',
                            'immat': immat,
                            'marque': marque,
                            'modele': modele
                        })

                        if visual_span <= 60:
                            self.ax.text(mdates.date2num(d_debut), position_y + 9.5, d_debut.strftime('%d/%m %H:%M'), 
                                         ha='right', va='bottom', fontsize=8, color='black', fontweight='bold')
                            self.ax.text(mdates.date2num(d_debut) + duree, position_y + 9.5, d_fin.strftime('%d/%m %H:%M'), 
                                         ha='left', va='bottom', fontsize=8, color='black', fontweight='bold')
                                     
                    except Exception: pass

            self.ax.set_yticks(y_ticks)
            self.ax.set_yticklabels(y_labels, fontsize=9)
            self.ax.grid(True, axis='x', linestyle='--', alpha=0.7)
            
            aujourdhui_reel = datetime.now()
            if date_debut_filtre <= aujourdhui_reel <= date_fin_filtre:
                self.ax.axvline(x=aujourdhui_reel, color='red', linestyle='-', linewidth=2, alpha=0.5, label="Aujourd'hui")
            
            handles, labels = self.ax.get_legend_handles_labels()
            if handles:
                self.ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.08), ncol=4, fontsize=10)
                
            plt.title(f"Diagramme de Gantt avec Progression Temps Réel (Zoom x{self.zoom_level:.1f})", fontsize=14, pad=45)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            self.canvas_gantt = FigureCanvas(fig)
            self.canvas_gantt.mpl_connect("motion_notify_event", self.on_hover_gantt)
            self.canvas_gantt.mpl_connect("button_press_event", self.on_click_gantt)
            
            # 🎯 SCROLLBAR DYNAMIQUE MULTIPLIÉE PAR LE ZOOM
            largeur_min_scroll = max(1200, int(delta_jours * 25 * self.zoom_level))
            hauteur_min_scroll = max(600, len(vehicules) * 60)
            self.canvas_gantt.setMinimumSize(largeur_min_scroll, hauteur_min_scroll)
            
            self.scroll_area_gantt.setWidget(self.canvas_gantt)
            
        except sqlite3.Error as e:
            print(f"Erreur SQL Gantt : {e}")
        finally:
            if 'conn' in locals() and conn: conn.close()

    def on_hover_gantt(self, event):
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            found = False
            for rect in self.rectangles_gantt:
                if rect['x_min'] <= x <= rect['x_max'] and rect['y_min'] <= y <= rect['y_max']:
                    self.tooltip.xy = (x, y) 
                    self.tooltip.set_text(rect['info']) 
                    self.tooltip.set_visible(True) 
                    self.canvas_gantt.draw_idle()
                    found = True
                    break
            
            if not found and self.tooltip.get_visible():
                self.tooltip.set_visible(False)
                self.canvas_gantt.draw_idle()

    def on_click_gantt(self, event):
        if event.inaxes == self.ax and event.button == 1:
            x, y = event.xdata, event.ydata
            for rect in self.rectangles_gantt:
                if rect['x_min'] <= x <= rect['x_max'] and rect['y_min'] <= y <= rect['y_max']:
                    self.ouvrir_dialogue_modification(rect)
                    break

    def ouvrir_dialogue_modification(self, rect):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Modification Rapide - {rect['immat']}")
        dialog.setMinimumWidth(380)
        layout = QVBoxLayout(dialog)
        
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            
            if rect['type'] == 'location':
                cursor.execute("SELECT date_sortie, date_retour_prevue FROM LOCATION WHERE id_location = ?", (rect['id'],))
                res = cursor.fetchone()
                if not res: return
                date_s_str, date_r_str = res
                lbl = QLabel(f"🚗 <b>Modification de la Location</b><br>Véhicule : {rect['marque']} {rect['modele']} ({rect['immat']})")
            else:
                cursor.execute("SELECT date_debut_reparation, date_fin_reparation FROM REPARATION WHERE id_reparation = ?", (rect['id'],))
                res = cursor.fetchone()
                if not res: return
                date_s_str, date_r_str = res
                lbl = QLabel(f"🔧 <b>Modification de la Maintenance</b><br>Véhicule : {rect['marque']} {rect['modele']} ({rect['immat']})")
                
            lbl.setStyleSheet("font-size: 14px; padding-bottom: 10px;")
            layout.addWidget(lbl)
            
            def formater_date(d_str):
                if not d_str: return QDateTime.currentDateTime()
                if len(d_str) > 10: return QDateTime.fromString(d_str, "yyyy-MM-dd HH:mm:ss")
                return QDateTime.fromString(d_str + " 12:00:00", "yyyy-MM-dd HH:mm:ss")

            edit_debut = QDateTimeEdit(formater_date(date_s_str))
            edit_debut.setCalendarPopup(True)
            layout.addWidget(QLabel("Nouvelle Date/Heure de DÉBUT :"))
            layout.addWidget(edit_debut)
            
            edit_fin = QDateTimeEdit(formater_date(date_r_str))
            edit_fin.setCalendarPopup(True)
            layout.addWidget(QLabel("Nouvelle Date/Heure de FIN :"))
            layout.addWidget(edit_fin)
            
            btn_save = QPushButton("💾 Enregistrer la modification")
            btn_save.setStyleSheet("background-color: #f39c12; color: white; padding: 10px; font-weight: bold; border-radius: 5px; margin-top: 10px;")
            layout.addWidget(btn_save)
            
            def valider_modification():
                nouveau_debut = edit_debut.dateTime().toString("yyyy-MM-dd HH:mm:ss")
                nouveau_fin = edit_fin.dateTime().toString("yyyy-MM-dd HH:mm:ss")
                
                if nouveau_fin <= nouveau_debut:
                    return QMessageBox.warning(dialog, "Erreur", "La date de fin doit obligatoirement être après le début.")
                    
                c = conn.cursor()
                immat = rect['immat']
                
                c.execute("SELECT date_debut_planifiee FROM VOYAGE WHERE immatriculation=? AND statut_voyage IN ('Planifié', 'En cours') AND date_debut_planifiee >= ? AND date_debut_planifiee <= ?", (immat, nouveau_debut, nouveau_fin))
                if c.fetchone(): return QMessageBox.warning(dialog, "Bouclier Activé 🛡️", "Ces nouvelles dates chevauchent un VOYAGE prévu.")

                if rect['type'] == 'location':
                    c.execute("SELECT id_location FROM LOCATION WHERE immatriculation=? AND id_location!=? AND statut_location IN ('Planifiée', 'En cours', 'En location') AND date_sortie < ? AND COALESCE(date_retour_reelle, date_retour_prevue, '2099-12-31') > ?", (immat, rect['id'], nouveau_fin, nouveau_debut))
                    if c.fetchone(): return QMessageBox.warning(dialog, "Bouclier Activé 🛡️", "Ces nouvelles dates chevauchent une AUTRE location déjà enregistrée.")
                    
                    c.execute("SELECT id_reparation FROM REPARATION WHERE immatriculation=? AND statut_reparation='En cours' AND date_debut_reparation < ? AND COALESCE(date_fin_reparation, date('now', '+3 days')) > ?", (immat, nouveau_fin, nouveau_debut))
                    if c.fetchone(): return QMessageBox.warning(dialog, "Bouclier Activé 🛡️", "Ces nouvelles dates chevauchent une maintenance prévue pour ce véhicule.")
                    
                    c.execute("UPDATE LOCATION SET date_sortie=?, date_retour_prevue=? WHERE id_location=?", (nouveau_debut, nouveau_fin, rect['id']))
                    GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Modif. Planning Rapide", f"Dates modifiées pour la location du {immat} via le Gantt.")

                else:
                    c.execute("SELECT id_reparation FROM REPARATION WHERE immatriculation=? AND id_reparation!=? AND statut_reparation='En cours' AND date_debut_reparation < ? AND COALESCE(date_fin_reparation, date('now', '+3 days')) > ?", (immat, rect['id'], nouveau_fin, nouveau_debut))
                    if c.fetchone(): return QMessageBox.warning(dialog, "Bouclier Activé 🛡️", "Ces nouvelles dates chevauchent une AUTRE maintenance.")
                    
                    c.execute("SELECT id_location FROM LOCATION WHERE immatriculation=? AND statut_location IN ('Planifiée', 'En cours', 'En location') AND date_sortie < ? AND COALESCE(date_retour_reelle, date_retour_prevue, '2099-12-31') > ?", (immat, nouveau_fin, nouveau_debut))
                    if c.fetchone(): return QMessageBox.warning(dialog, "Bouclier Activé 🛡️", "Ces nouvelles dates chevauchent une location prévue par un client.")
                    
                    c.execute("UPDATE REPARATION SET date_debut_reparation=?, date_fin_reparation=? WHERE id_reparation=?", (nouveau_debut, nouveau_fin, rect['id']))
                    GestionHistorique.ajouter_log(self.db_connect, "Utilisateur", "Modif. Planning Rapide", f"Dates de maintenance modifiées pour {immat} via le Gantt.")
                    
                conn.commit()
                QMessageBox.information(dialog, "Succès", "Mise à jour effectuée avec succès !")
                dialog.accept()
                
                self.generer_gantt()
                
            btn_save.clicked.connect(valider_modification)
            dialog.exec()
            
        except sqlite3.Error as e: 
            print(f"Erreur modif: {e}")
        finally: 
            if 'conn' in locals() and conn: conn.close()